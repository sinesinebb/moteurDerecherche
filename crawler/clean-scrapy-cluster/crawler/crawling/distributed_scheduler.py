from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str, object
from past.builtins import basestring
from six import string_types
from scrapy.http import Request
from scrapy.utils.python import to_unicode
from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.utils.project import get_project_settings
import redis, random, time, tldextract, urllib.request, re, yaml, sys, uuid, socket, ujson
from crawling.redis_dupefilter import RFPDupeFilter
from crawling.redis_global_page_per_domain_filter import RFGlobalPagePerDomainFilter
from crawling.redis_domain_max_page_filter import RFDomainMaxPageFilter
from scutils.redis_queue import RedisPriorityQueue
from scutils.redis_throttled_queue import RedisThrottledQueue
from scutils.log_factory import LogFactory
from scutils.zookeeper_watcher import ZookeeperWatcher



class DistributedScheduler(object):
    """
    Scrapy scheduler using Redis priority & throttled queues, plus optional Zookeeper config.
    """
    def __init__(self, server, persist, update_interval, dupe_timeout, item_retries, logger,
                 hits, window, moderated, ip_refresh, add_type, add_ip, ip_regex,
                 backlog_blacklist, queue_timeout, global_limit, global_limit_timeout, domain_max_timeout):
        self.my_ip = None
        self.old_ip = None
        # core settings
        self.redis_conn = server
        self.persist = persist
        self.update_interval = update_interval
        self.rfp_timeout = dupe_timeout
        self.item_retries = item_retries
        self.hits = hits
        self.window = window
        self.moderated = moderated
        self.ip_update_interval = ip_refresh
        self.add_type = add_type
        self.add_ip = add_ip
        self.ip_regex = re.compile(ip_regex)
        self.backlog_blacklist = backlog_blacklist
        self.queue_timeout = queue_timeout
        self.global_page_per_domain_limit = global_limit
        self.global_page_per_domain_limit_timeout = global_limit_timeout
        self.domain_max_page_timeout = domain_max_timeout
        # logger & identity
        self.logger = logger
        self.extract = tldextract.TLDExtract()
        self.update_ipaddress()
        self.my_uuid = str(uuid.uuid4()).split('-')[4]
        # dynamic config placeholders
        self.queue_dict = {}
        self.queue_keys = []
        self.update_time = 0
        self.update_ip_time = 0
        self.config_flag = False
        self.domain_config = {}
        self.black_domains = []
        

    @classmethod
    def from_settings(cls, settings):
        # Redis connection
        server = redis.Redis(
            host=settings.get('REDIS_HOST'),
            port=settings.get('REDIS_PORT'),
            db=settings.get('REDIS_DB'),
            password=settings.get('REDIS_PASSWORD'),
            decode_responses=True,
            socket_timeout=settings.get('REDIS_SOCKET_TIMEOUT'),
            socket_connect_timeout=settings.get('REDIS_SOCKET_TIMEOUT'),
        )
        # scheduler parameters
        persist = settings.get('SCHEDULER_PERSIST', True)
        up_int = settings.get('SCHEDULER_QUEUE_REFRESH', 10)
        hits = settings.get('QUEUE_HITS', 10)
        window = settings.get('QUEUE_WINDOW', 60)
        mod = settings.get('QUEUE_MODERATED', False)
        timeout = settings.get('DUPEFILTER_TIMEOUT', 600)
        ip_refresh = settings.get('SCHEDULER_IP_REFRESH', 60)
        add_type = settings.get('SCHEDULER_TYPE_ENABLED', False)
        add_ip = settings.get('SCHEDULER_IP_ENABLED', False)
        retries = settings.get('SCHEDULER_ITEM_RETRIES', 3)
        ip_regex = settings.get('IP_ADDR_REGEX', '.*')
        backlog_blacklist = settings.get('SCHEDULER_BACKLOG_BLACKLIST', True)
        queue_timeout = settings.get('SCHEDULER_QUEUE_TIMEOUT', 3600)
        # logger
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
        # page constraints
        global_limit = settings.get('GLOBAL_PAGE_PER_DOMAIN_LIMIT', None)
        global_limit_timeout = settings.get('GLOBAL_PAGE_PER_DOMAIN_LIMIT_TIMEOUT', 600)
        domain_max_timeout = settings.get('DOMAIN_MAX_PAGE_TIMEOUT', 600)
        # instantiate
        inst = cls(
            server, persist, up_int, timeout, retries, logger,
            hits, window, mod, ip_refresh, add_type, add_ip,
            ip_regex, backlog_blacklist, queue_timeout,
            global_limit, global_limit_timeout, domain_max_timeout
        )
        inst.settings = settings
        return inst


    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)
    

    def setup_zookeeper(self):
        # if ZK not configured, skip
        hosts = self.settings.get('ZOOKEEPER_HOSTS')
        path = self.settings.get('ZOOKEEPER_ASSIGN_PATH', '') + self.settings.get('ZOOKEEPER_ID', 'all')
        if not hosts or not path:
            self.logger.warning("Zookeeper not configured – skipping dynamic config")
            return
        try:
            # pass filepath explicitly
            self.zoo_watcher = ZookeeperWatcher(
                hosts=hosts,
                filepath=path,
                config_handler=self.change_config,
                error_handler=self.error_config,
                pointer=False,
                ensure=True,
                valid_init=True
            )
        except Exception as e:
            self.logger.error(f"Could not connect to Zookeeper – ZK features disabled: {e}")
            return
        # ping
        try:
            if self.zoo_watcher.ping():
                self.logger.debug("Zookeeper connection established")
            else:
                self.logger.error("Could not ping Zookeeper – ZK features disabled")
        except Exception:
        # Désactivé : ignore l’échec ZK
            return
        # except Exception:
        #     self.logger.error("Error pinging Zookeeper – ZK features disabled")

    def open(self, spider):
        self.spider = spider
        self.spider.settings = self.settings
        self.create_queues()
        self.setup_zookeeper()
        # dupe filters and rate limits
        self.dupefilter = RFPDupeFilter(self.redis_conn,
                                        f"{spider.name}:dupefilter",
                                        self.rfp_timeout)
        self.global_page_per_domain_filter = RFGlobalPagePerDomainFilter(
            self.redis_conn,
            f"{spider.name}:global_page_count_filter",
            self.global_page_per_domain_limit,
            self.global_page_per_domain_limit_timeout
        )
        self.domain_max_page_filter = RFDomainMaxPageFilter(
            self.redis_conn,
            f"{spider.name}:domain_max_page_filter",
            self.domain_max_page_timeout
        )


    def close(self, reason):
        self.logger.info("Closing Spider", {'spider': self.spider.name})
        if not self.persist:
            self.dupefilter.clear()
            self.global_page_per_domain_filter.clear()
            self.domain_max_page_filter.clear()
            for key in list(self.queue_keys):
                self.queue_dict[key][0].clear()


    def change_config(self, config_string):
        if config_string:
            loaded = yaml.safe_load(config_string)
            self.logger.info("ZK config changed", extra=loaded)
            self.load_domain_config(loaded)
            self.update_domain_queues()
        else:
            self.error_config("ZK config wiped")
        self.create_queues()

    def error_config(self, message):
        extras = {
            'message': message,
            'revert_window': self.window,
            'revert_hits': self.hits,
            'spiderid': self.spider.name
        }
        self.logger.info("Lost ZK config, reverting to defaults", extra=extras)
        # revert any existing per-domain overrides
        for domain in self.domain_config:
            key = f"{self.spider.name}:{domain}:queue"
            if key in self.queue_dict:
                self.queue_dict[key][0].window = self.window
                self.queue_dict[key][0].limit = self.hits
        self.domain_config.clear()


    def load_domain_config(self, cfg):
        self.domain_config = {}
        self.black_domains = []
        if 'domains' in cfg:
            for dom, cfg_item in cfg['domains'].items():
                if 'window' in cfg_item and 'hits' in cfg_item:
                    self.domain_config[dom] = cfg_item
        if 'blacklist' in cfg:
            self.black_domains = cfg['blacklist']
        self.config_flag = True


    # Queue management
    def create_queues(self):
        new_conf = self.check_config()
        self.queue_keys = self.redis_conn.keys(f"{self.spider.name}:*:queue")
        for key in self.queue_keys:
            domain = key.split(':')[1]
            throttle = ''
            if self.add_type:
                throttle += f"{self.spider.name}:"
            if self.add_ip:
                throttle += f"{self.my_ip}:"
            throttle += domain
            if key not in self.queue_dict or new_conf:
                q = RedisPriorityQueue(self.redis_conn, key, encoding=ujson)
                cfg = self.domain_config.get(domain)
                if not cfg:
                    w, h = self.window, self.hits
                else:
                    w = cfg['window']
                    h = cfg['hits'] * (cfg.get('scale', 1.0))
                self.queue_dict[key] = [
                    RedisThrottledQueue(
                        self.redis_conn, q, w, h,
                        self.moderated, throttle, throttle, True
                    ),
                    time.time()
                ]

    def update_domain_queues(self):
        for dom, cfg in self.domain_config.items():
            key = f"{self.spider.name}:{dom}:queue"
            if key in self.queue_dict:
                queue, _ = self.queue_dict[key]
                queue.window = float(cfg['window'])
                queue.limit = float(int(cfg['hits'] * self.fit_scale(cfg.get('scale', 1))))##

    def fit_scale(self, scale):
        return max(0.0, min(scale, 1.0))

    def expire_queues(self):
        now = time.time()
        for key, (_, ts) in list(self.queue_dict.items()):
            if now - ts > self.queue_timeout:
                del self.queue_dict[key]
                if key in self.queue_keys:
                    self.queue_keys.remove(key)

    # IP address
    def update_ipaddress(self):
        self.old_ip = self.my_ip
        self.my_ip = '127.0.0.1'
        try:
            url = self.settings.get('PUBLIC_IP_URL', 'http://ip.42.pl/raw')
            resp = urllib.request.urlopen(url).read().decode()
            ips = self.ip_regex.findall(resp)
            if ips:
                self.my_ip = ips[0]
        except Exception:
        # Désactivé : on force une IP locale pour ne plus boucler
            return "127.0.0.1"
        # except Exception:
        #     self.logger.error("Could not retrieve public IP")
        # if self.old_ip != self.my_ip:
        #     self.logger.info(f"Changed Public IP: {self.old_ip} -> {self.my_ip}")

    def check_config(self):
        if self.config_flag:
            self.config_flag = False
            return True
        return False

    def report_self(self):
        key = f"stats:crawler:{socket.gethostname()}:{self.spider.name}:{self.my_uuid}"
        self.redis_conn.set(key, time.time())
        self.redis_conn.expire(key, self.ip_update_interval * 2)

    # Crawling
    def enqueue_request(self, request):
        if not request.dont_filter and self.dupefilter.request_seen(request):
            return
        req = request_to_dict(request, self.spider)
        # per-domain
        if req['meta'].get('domain_max_pages'):
            if self.domain_max_page_filter.request_page_limit_reached(request, self.spider):
                return
        # global
        if self.global_page_per_domain_limit:
            if self.global_page_per_domain_filter.request_page_limit_reached(request, self.spider):
                return
        # blacklist
        if not self.dupefilter.request_seen(request):
            ex = self.extract(req['url'])
            key = f"{req['meta']['spiderid']}:{ex.domain}.{ex.suffix}:queue"
            now = time.time()
            dom = f"{ex.domain}.{ex.suffix}"
            valid = (self.backlog_blacklist or dom not in self.black_domains)
            if valid and (req['meta']['expires']==0 or now<req['meta']['expires']):
                if key in self.queue_keys:
                    self.queue_dict[key][0].push(req, req['meta']['priority'])
                else:
                    self.redis_conn.zadd(key, {ujson.dumps(req): -req['meta']['priority']})

    def find_item(self):
        random.shuffle(self.queue_keys)
        for _ in range(self.item_retries+1):
            for key in self.queue_keys:
                dom = key.split(':')[1]
                if dom in self.black_domains: continue
                item = self.queue_dict[key][0].pop()
                if item:
                    self.queue_dict[key][1] = time.time()
                    return item
        return None

    def next_request(self):
        t = time.time()
        if t - self.update_time > self.update_interval:
            self.update_time = t
            self.create_queues()
            self.expire_queues()
        if t - self.update_ip_time > self.ip_update_interval:
            self.update_ip_time = t
            self.update_ipaddress()
            self.report_self()
        item = self.find_item()
        if not item: return None
        if 'meta' in item:
            req = request_from_dict(item, self.spider)
        else:
            req = Request(item['url'])
        # headers/cookies
        if 'useragent' in req.meta:
            req.headers['User-Agent'] = req.meta['useragent']
        if 'cookie' in req.meta:
            if isinstance(req.meta['cookie'], dict):
                req.cookies = req.meta['cookie']
            elif isinstance(req.meta['cookie'], string_types):
                req.cookies = self.parse_cookie(req.meta['cookie'])
        return req

    def parse_cookie(self, cookie_str):
        res = re.findall(r'([^=]+)=([^;]+);?\s?', cookie_str)
        return {k: v for k, v in res}

    def has_pending_requests(self):
        return False
