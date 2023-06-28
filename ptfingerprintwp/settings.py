# Scrapy settings for portugal wordpes fingerprint project
BOT_NAME = 'PTfingerprintWP'

SPIDER_MODULES = ['ptfingerprintwp.spiders']
NEWSPIDER_MODULE = 'ptfingerprintwp.spiders'

# Add Your ScrapeOps API key
# get free API key at https://scrapeops.io/app/register
SCRAPEOPS_API_KEY = '4bebbb96-46a1-4e66-aa60-58408d5854a3'

# Add In The ScrapeOps Extension
EXTENSIONS = {
    'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500,
}
# Update The Download Middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

RETRY_TIMES = 5
