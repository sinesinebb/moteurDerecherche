import logging
import redis
import socket
import time
import sys
import os
from scrapy.utils.response import response_status_message
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web._newclient import ResponseFailed
from twisted.internet import defer
from redis.exceptions import ConnectionError



try:
    # accommodate older Twisted
    from twisted.web._newclient import ResponseFailed
except ImportError:
    from twisted.internet.error import ResponseFailed

class LogRetryMiddleware(object):

    EXCEPTIONS_TO_RETRY = (
        defer.TimeoutError, TimeoutError, DNSLookupError,
        ConnectionRefusedError, ConnectionDone, ConnectError,
        ConnectionLost, TCPTimedOutError, ResponseFailed, IOError
    )

    def __init__(self, settings):
        self.settings = settings
        # chemin du dossier de logs (ou le tirer de settings)
        self.log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        # taille max du fichier avant rotation (en octets)
        self.max_bytes = settings.getint('LOG_RETRY_MAX_BYTES', 10 * 1024 * 1024)
        # nombre de sauvegardes à garder
        self.backup_count = settings.getint('LOG_RETRY_BACKUP_COUNT', 5)
        self._init_logger()
        self._init_retry_codes()
        self._init_redis_stats()
        # if settings.getbool('STATS_STATUS_CODES'):
        #     self._init_redis_stats()

    @classmethod
    def from_crawler(cls, crawler):
        crawler.settings.frozen = False
        crawler.settings.set('SPIDER_NAME', crawler.spider.name)
        return cls(crawler.settings)

    def _init_logger(self):
        # créer le dossier de logs s’il n’existe pas
        os.makedirs(self.log_dir, exist_ok=True)

        log_file = os.path.join(self.log_dir, 'sc_crawler.log')
        fh = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        name = self.settings.get('SC_LOGGER_NAME', 'sc-logger')
        level = self.settings.get('SC_LOG_LEVEL', 'INFO')
        to_stdout = self.settings.getbool('SC_LOG_STDOUT', True)
        log_dir = self.settings.get('SC_LOG_DIR', 'logs')
        log_file = self.settings.get('SC_LOG_FILE', 'main.log')
        max_bytes = self.settings.get('SC_LOG_MAX_BYTES', 10 * 1024 * 1024)
        backups = self.settings.getint('SC_LOG_BACKUPS', 5)
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        
        if to_stdout:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        
        # file handler
        fh = logging.handlers.RotatingFileHandler(
            filename=f"{log_dir}/{log_file}",
            maxBytes=max_bytes,
            backupCount=backups
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = logger

    def _init_retry_codes(self):
        self.retry_http_codes = set(
            int(x) for x in self.settings.getlist('RETRY_HTTP_CODES')
        )

    def _init_redis_stats(self):
        """
        Initialise la connexion à Redis pour collecter des stats de retry.
        Si Redis n'est pas joignable, on se contente de désactiver la partie stats
        au lieu de quitter brutalement.
        """
        try:
            # ton code actuel pour connecter à Redis, par ex :
            from redis import StrictRedis
            host = self.settings.get('REDIS_HOST', 'localhost')
            port = self.settings.getint('REDIS_PORT', 6379)
            self.redis_client = StrictRedis(host=host, port=port)
            # fais un ping-test
            if not self.redis_client.ping():
                raise Exception("ping failed")
        except Exception as e:
            self.logger.warning(f"Impossible de connecter à Redis ({e}), stats de retry désactivées.")
            # Au lieu de sys.exit(1), on désactive juste la collecte de stats
            self.redis_client = None
            self.stats_key = None


    def _init_redis_stats(self):
        host = self.settings.get('REDIS_HOST')
        port = self.settings.get('REDIS_PORT')
        db = self.settings.get('REDIS_DB')
        pwd = self.settings.get('REDIS_PASSWORD')
        timeout = self.settings.get('REDIS_SOCKET_TIMEOUT')
        self.redis_conn = redis.Redis(
            host=host, port=port, db=db,
            password=pwd,
            decode_responses=True,
            socket_timeout=timeout,
            socket_connect_timeout=timeout
        )
        try:
            self.redis_conn.ping()
            self.logger.debug("Connected to Redis in LogRetryMiddleware")
        except ConnectionError:
            self.logger.error("Failed to connect to Redis, exiting.")
            sys.exit(1)

        # initialize your stats dict here (omitting StatsCollector)
        self.stats_dict = {}
        # ... additional stats setup if needed

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            self._log_retry(request, exception)
            # optionally increment stats

    def _log_retry(self, request, exception):
        self.logger.error(
            f"Retrying {request.url} after error: {exception}",
            extra={
                'retry_count': request.meta.get('retry_times', 0),
                'appid': request.meta.get('appid'),
                'crawlid': request.meta.get('crawlid')
            }
        )

    # stub methods for stats
    def _increment_504_stat(self, request):
        pass
