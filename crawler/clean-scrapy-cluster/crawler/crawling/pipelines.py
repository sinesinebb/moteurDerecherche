# -*- coding: utf-8 -*-
from builtins import object
import json
import datetime as dt
import base64
import logging
import time
from kafka import KafkaProducer
from scrapy.exceptions import NotConfigured
from crawling.items import RawResponseItem
from scutils.log_factory import LogFactory
from parsel import Selector


class LoggingBeforePipeline(object):
    """
    Logs crawl events before sending to Kafka
    """
    def __init__(self, logger):
        self.logger = logger
        self.logger.debug("LoggingBeforePipeline initialized")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        logger = LogFactory.get_instance(
            json=settings.get('SC_LOG_JSON', False),
            name=settings.get('SC_LOGGER_NAME', 'sc-logger'),
            stdout=settings.get('SC_LOG_STDOUT', True),
            level=settings.get('SC_LOG_LEVEL', 'INFO'),
            dir=settings.get('SC_LOG_DIR', 'logs'),
            file=settings.get('SC_LOG_FILE', 'main.log'),
            bytes=settings.get('SC_LOG_MAX_BYTES', '10MB'),
            backups=settings.get('SC_LOG_BACKUPS', 5),
        )
        return cls(logger)

    def process_item(self, item, spider):
        self.logger.debug("Processing item in LoggingBeforePipeline")
        if isinstance(item, RawResponseItem):
            data = dict(item)
            for field in ('body', 'links', 'response_headers', 'request_headers'):
                data.pop(field, None)
            extra = {
                'logger': self.logger.name,
                'action': 'emit',
                'spiderid': spider.name
            }
            self.logger.info('Scraped page', extra={**data, **extra})
        else:
            self.logger.warning('LoggingBeforePipeline: skipping non-RawResponseItem')
        return item


class KafkaPipeline(object):
    """
    Pushes items to Kafka topics: main topic and per-appid.
    The main topic is read from spider settings (KAFKA_TOPIC) or falls back to 'crawled_documents'.
    """
    MAX_ATTEMPTS = 5
    BACKOFF_BASE = 2

    def __init__(self, producer, kafka_hosts, topic_prefix, appid_topics, use_base64, logger, main_topic):
        self.producer = producer
        self.kafka_hosts = kafka_hosts
        self.topic_prefix = topic_prefix
        self.appid_topics = appid_topics or []
        self.use_base64 = use_base64
        self.logger = logger
        self.main_topic = main_topic
        self.logger.debug(f"KafkaPipeline initialized with main_topic: {self.main_topic}")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        raw = settings.get('KAFKA_APPID_TOPICS', [])
        if isinstance(raw, str):
            appid_topics = [t.strip() for t in raw.split(',') if t.strip()]
        elif isinstance(raw, (list, tuple)):
            appid_topics = list(raw)
        else:
            appid_topics = []

        logger = LogFactory.get_instance(
            json=settings.get('SC_LOG_JSON', False),
            name=settings.get('SC_LOGGER_NAME', 'sc-logger'),
            stdout=settings.get('SC_LOG_STDOUT', True),
            level=settings.get('SC_LOG_LEVEL', 'INFO'),
            dir=settings.get('SC_LOG_DIR', 'logs'),
            file=settings.get('SC_LOG_FILE', 'main.log'),
            bytes=settings.get('SC_LOG_MAX_BYTES', '10MB'),
            backups=settings.get('SC_LOG_BACKUPS', 5),
        )

        kafka_hosts = settings.get('KAFKA_BOOTSTRAP_SERVERS')
        if not kafka_hosts:
            raise NotConfigured('KAFKA_BOOTSTRAP_SERVERS not set')

        # Création du producteur Kafka avec uniquement les paramètres de base
        attempts = 0
        producer = None
        while attempts < cls.MAX_ATTEMPTS:
            try:
                producer = KafkaProducer(
                    bootstrap_servers=kafka_hosts,
                    value_serializer=lambda m: json.dumps(m).encode('utf-8')
                )
                logger.info(f"Connected to Kafka → {kafka_hosts}")
                break
            except Exception as e:
                wait = cls.BACKOFF_BASE ** attempts
                logger.warning(
                    f"Kafka unavailable (attempt {attempts+1}/{cls.MAX_ATTEMPTS}): {e}. Retrying in {wait}s..."
                )
                time.sleep(wait)
                attempts += 1

        if not producer:
            raise NotConfigured("Unable to connect to Kafka")

        topic_prefix = settings.get('KAFKA_TOPIC_PREFIX', 'crawl')
        use_base64 = settings.get('KAFKA_BASE_64_ENCODE', False)

        # Détermination du topic principal :
        #  1. KAFKA_TOPIC défini dans les custom_settings du spider
        #  2. KAFKA_MAIN_TOPIC (paramètre historique)
        #  3. fallback 'crawled_documents'
        main_topic = (
            settings.get('KAFKA_TOPIC') or
            settings.get('KAFKA_MAIN_TOPIC') or
            'crawled_documents'
        )

        return cls(producer, kafka_hosts, topic_prefix, appid_topics, use_base64, logger, main_topic)

    def close_spider(self, spider):
        self.logger.info("Closing KafkaPipeline")
        try:
            self.producer.flush()
            self.producer.close()
        except Exception as e:
            self.logger.error(f"Error closing Kafka producer: {e}")

    def _timestamp(self):
        return dt.datetime.utcnow().isoformat()

    def _clean(self, item):
        if not item:
            return {}
        try:
            data = dict(item)
        except Exception:
            data = item if isinstance(item, dict) else {}
        for f in ('body', 'links', 'response_headers', 'request_headers', 'status_code', 'status_msg'):
            data.pop(f, None)
        data.update(action='ack', logger=self.logger.name)
        return data

    def _on_success(self, record_metadata, item=None, spider=None):
        try:
            extra = self._clean(item)
        except Exception:
            extra = {}
        meta = {
            'topic': getattr(record_metadata, 'topic', None),
            'partition': getattr(record_metadata, 'partition', None),
            'offset': getattr(record_metadata, 'offset', None)
        }
        extra.update(meta)
        self.logger.info("Kafka send succeeded", extra=extra)

    def _on_error(self, exc, item=None, spider=None):
        try:
            extra = self._clean(item)
        except Exception:
            extra = {}
        extra.update({'error': str(exc)})
        self.logger.error("Kafka send failed", extra=extra)

    def _extract_text_from_body(self, body, encoding=None):
        try:
            if isinstance(body, bytes):
                body = body.decode(encoding or 'utf-8', errors='ignore')
            sel = Selector(text=body)
            text = sel.xpath('string(.)').get()
            if text:
                return ' '.join(part.strip() for part in text.splitlines() if part.strip())
        except Exception:
            return None
        return None

    def process_item(self, item, spider):
        self.logger.debug(f"Processing item in KafkaPipeline for spider {spider.name}")
        self.logger.info(f"🔄 KafkaPipeline started processing: {item.get('url', 'unknown URL')}")

        try:
            data = dict(item)
        except Exception:
            data = item if isinstance(item, dict) else {}

        data['timestamp'] = self._timestamp()

        # Gestion du champ body si bytes
        if 'body' in data:
            raw = data['body']
            if isinstance(raw, bytes):
                if self.use_base64:
                    data['body'] = base64.b64encode(raw).decode('ascii')
                    data['body_is_base64'] = True
                else:
                    data['body'] = raw.decode(data.get('encoding', 'utf-8'), errors='ignore')

        # Construction du payload (on enlève les champs lourds)
        payload = data.copy()
        for key in ['body', 'response_headers', 'request_headers']:
            payload.pop(key, None)

        self.logger.info(f"PAYLOAD keys: {list(payload.keys())}")

        # Envoi sur le topic principal
        try:
            future = self.producer.send(self.main_topic, payload)
            future.add_callback(self._on_success, payload, spider)
            future.add_errback(self._on_error, payload, spider)
            self.logger.info(f"✅ Successfully queued message to {self.main_topic} for {data.get('url', 'unknown URL')}")
        except Exception as e:
            self.logger.error(f"❌ Failed to send to Kafka topic {self.main_topic}: {str(e)}")

        # Envoi optionnel sur topic par appid
        appid = data.get('appid')
        if appid and appid in self.appid_topics:
            topic2 = f"{self.topic_prefix}.outbound_{appid}"
            try:
                future2 = self.producer.send(topic2, payload)
                future2.add_callback(self._on_success, payload, spider)
                future2.add_errback(self._on_error, payload, spider)
                self.logger.debug(f"Also sent to appid topic: {topic2}")
            except Exception as e:
                self.logger.error(f"Failed to send to appid topic {topic2}: {str(e)}")

        # ---- Envoi des demandes YouTube (conservé) ----
        youtube_ids = data.get('youtube_video_ids', [])
        if youtube_ids:
            for vid in youtube_ids:
                youtube_msg = {
                    "video_id": vid,
                    "doc_id": data.get('url'),
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }
                try:
                    self.producer.send("youtube.metadata.requests", youtube_msg)
                    self.logger.debug(f"Sent YouTube metadata request for {vid}")
                except Exception as e:
                    self.logger.error(f"Failed to send YouTube request for {vid}: {e}")
            try:
                self.producer.flush()
            except Exception as e:
                self.logger.error(f"Error flushing YouTube requests: {e}")

        return item