# settings.py

import os

BOT_NAME = "crawling"
SPIDER_MODULES = ["crawling.spiders"]
NEWSPIDER_MODULE = "crawling.spiders"

# scheduler Redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# ne pas vider la file entre les runs, si besoin
SCHEDULER_PERSIST = True

# connexion Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# désactivez le scheduler Scrapy par défaut
# (vous pouvez laisser vos autres custom_settings dans le spider)


# la clé où le Scheduler pousse vos seeds
REDIS_START_URLS_KEY = "sc:start_urls"



