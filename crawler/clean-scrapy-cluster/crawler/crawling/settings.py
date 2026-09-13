# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

def str2bool(v):
    return str(v).lower() in ('true', '1') if isinstance(v, str) else bool(v)

# -------------------------------------------------------------------------------
#                                CLUSTER NAME
# -------------------------------------------------------------------------------
CLUSTER_NAME = os.getenv('CLUSTER_NAME', 'demo')

# -------------------------------------------------------------------------------
#                           Scheduler & Redis (scrapy-redis)
# -------------------------------------------------------------------------------
REDIS_URL            = os.getenv("REDIS_URL", "redis://redis:6379")
REDIS_HOST           = os.getenv("REDIS_HOST", "redis")
REDIS_PORT           = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB             = int(os.getenv("REDIS_DB", 0))
REDIS_START_URLS_KEY = "sc:start_urls"

DUPEFILTER_CLASS     = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER            = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST    = True

# -------------------------------------------------------------------------------
#                         Kafka & Zookeeper configuration
# -------------------------------------------------------------------------------
ZOOKEEPER_HOSTS         = os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181')
KAFKA_BOOTSTRAP_SERVERS = [h.strip() for h in os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX      = CLUSTER_NAME
KAFKA_APPID_TOPICS      = os.getenv('KAFKA_APPID_TOPICS', '').split(',')
KAFKA_BASE_64_ENCODE    = str2bool(os.getenv('KAFKA_BASE_64_ENCODE', 'False'))


KAFKA_MAIN_TOPIC        = os.getenv('KAFKA_MAIN_TOPIC', 'crawled_documents')


# -------------------------------------------------------------------------------
#                            Pipelines declaration
# -------------------------------------------------------------------------------
ITEM_PIPELINES = {
    'crawling.pipelines.LoggingBeforePipeline': 50,
    'crawling.pipelines.KafkaPipeline':        100,
}

# -------------------------------------------------------------------------------
#                             Spiders modules
# -------------------------------------------------------------------------------
BOT_NAME         = 'crawling'
SPIDER_MODULES   = ['crawling.spiders']
NEWSPIDER_MODULE = 'crawling.spiders'

SPIDER_MIDDLEWARES = {
    # RedisSpiderMiddleware a bougé dans scrapy_redis.middlewares
    "crawling.redis_middlewares.RedisSpiderMiddleware": 543,
    "crawling.middlewares.DomainLimitMiddleware": 550,
    "scrapy.spidermiddlewares.offsite.OffsiteMiddleware": 500,
    
}

#--------------------------------------------------------------------------------
#                               Minio configuration
#--------------------------------------------------------------------------------
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'documents')
MINIO_SECURE = str2bool(os.getenv('MINIO_SECURE', 'False'))


#-------------------------------------------------------------------------------
#                               Seuil des pages à crawler
#------------------------------------------------------------------------------
MAX_PAGES_PER_DOMAIN = 150
TARGET_SCORE_PER_DOMAIN = 12.0


# -------------------------------------------------------------------------------
#                    Concurrency & Crawl behaviour settings
# -------------------------------------------------------------------------------
CONCURRENT_REQUESTS      = int(os.getenv('CONCURRENT_REQUESTS', 16))
DOWNLOAD_DELAY           = float(os.getenv('DOWNLOAD_DELAY', 1))
RANDOMIZE_DOWNLOAD_DELAY = str2bool(os.getenv('RANDOMIZE_DOWNLOAD_DELAY', 'True'))
DEPTH_LIMIT              = int(os.getenv('DEPTH_LIMIT', 3))

DOWNLOAD_TIMEOUT         = int(os.getenv('DOWNLOAD_TIMEOUT', 30))
RETRY_TIMES              = int(os.getenv('RETRY_TIMES', 3))
HTTPERROR_ALLOW_ALL      = True
DNSCACHE_ENABLED         = True

DOWNLOADER_MIDDLEWARES = {
    # anciennement scrapy_redis.downloadermiddlewares.RedisTimeoutMiddleware
    "crawling.redis_middlewares.RedisTimeoutMiddleware": 350,
}

# -------------------------------------------------------------------------------
#                                  Logging
# -------------------------------------------------------------------------------
LOG_ENABLED = str2bool(os.getenv('LOG_ENABLED', 'True'))
LOG_LEVEL   = os.getenv('LOG_LEVEL', 'INFO')