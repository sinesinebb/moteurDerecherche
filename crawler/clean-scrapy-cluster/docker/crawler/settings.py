# # -*- coding: utf-8 -*-
# from __future__ import absolute_import
# import os

# def str2bool(v):
#     return str(v).lower() in ('true', '1') if isinstance(v, str) else bool(v)

# # — Scheduler Redis + Scrapy Cluster Distributed —
# REDIS_URL           = os.getenv("REDIS_URL", "redis://redis:6379")
# DUPEFILTER_CLASS    = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER           = "crawling.distributed_scheduler.DistributedScheduler"
# SCHEDULER_PERSIST   = True

# # — Kafka & Zookeeper —
# KAFKA_BOOTSTRAP_SERVERS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
# ZOOKEEPER_HOSTS        = os.getenv('ZOOKEEPER_HOSTS', 'zookeeper:2181')

# # — Pipelines —
# ITEM_PIPELINES = {
#     'crawling.pipelines.LoggingBeforePipeline':  1,
#     'crawling.pipelines.KafkaPipeline':        100,
# }

# # — Spiders modules —
# BOT_NAME         = 'crawling'
# SPIDER_MODULES   = ['crawling.spiders']
# NEWSPIDER_MODULE = 'crawling.spiders'

# # — Concurrency & Crawl Settings —
# CONCURRENT_REQUESTS        = int(os.getenv('CONCURRENT_REQUESTS', 16))
# DOWNLOAD_DELAY             = float(os.getenv('DOWNLOAD_DELAY', 1))
# RANDOMIZE_DOWNLOAD_DELAY   = str2bool(os.getenv('RANDOMIZE_DOWNLOAD_DELAY', True))
# DEPTH_LIMIT                = int(os.getenv('DEPTH_LIMIT', 3))

# # — HTTP & Retry —
# DOWNLOAD_TIMEOUT   = int(os.getenv('DOWNLOAD_TIMEOUT', 15))
# RETRY_TIMES        = int(os.getenv('RETRY_TIMES', 3))
# HTTPERROR_ALLOW_ALL = True
# DNSCACHE_ENABLED    = True

# # — Logging —
# LOG_ENABLED   = str2bool(os.getenv('LOG_ENABLED', False))
# LOG_LEVEL     = os.getenv('LOG_LEVEL', 'INFO')

# # N’ajoutez **aucun** autre SCHEDULER ou ITEM_PIPELINES plus bas.
