# ./crawler/clean-scrapy-cluster/crawler/run.py
#!/usr/bin/env python
import os
import sys
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("Starting infoscraper spider...")
    
    # Load settings
    settings = get_project_settings()
    
    # Update settings if needed
    settings.set('SPIDER_MODULES', ['crawler.crawling.spiders'])
    settings.set('NEWSPIDER_MODULE', 'crawler.crawling.spiders')
    settings.set('LOG_LEVEL', 'INFO')
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Start the spider
    process.crawl('infoscraper')
    process.start()

if __name__ == '__main__':
    main()