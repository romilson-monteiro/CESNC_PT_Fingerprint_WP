import scrapy
import json
from urllib.parse import urlencode
from urllib.parse import urlparse
from scrapy import Spider, Request

API_KEY = '8933396e1dcb28b7beffb12a05c5e341'

WP_dominios = []

def get_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'autoparse': 'true', 'country_code': 'pt'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

def create_google_url(query, site=''):
    google_dict = {'q': query, 'num': 100}
    if site:
        web = urlparse(site).netloc
        google_dict['as_sitesearch'] = web
        return 'http://www.google.com/search?' + urlencode(google_dict)
    return 'http://www.google.com/search?' + urlencode(google_dict)

class DomainSpider(scrapy.Spider):
    name = 'domain'
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'RETRY_TIMES': 5
    }

    def __init__(self, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.unique_links = set()

    def start_requests(self):
        queries = [
            'site:*.pt inurl:wp-content',
            'site:*.pt inurl:wp-login.php',
            'site:*.pt inurl:wp-admin',
            'site:*.pt "Powered by WordPress"'
        ]
        for query in queries:
            url = create_google_url(query)
            yield scrapy.Request(get_url(url), callback=self.parse, meta={'pos': 0})

    def parse(self, response):
        di = json.loads(response.text)
        pos = response.meta['pos']
        for result in di['organic_results']:
            link = result['link']
            dominio = urlparse(link).netloc
            if dominio not in self.unique_links:
                self.unique_links.add(dominio)
                WP_dominios.append(dominio)
        pos += 1
        if 'pagination' in di and 'next_page_url' in di['pagination']:
            next_page = di['pagination']['next_page_url']
            if next_page:
                yield scrapy.Request(get_url(next_page), callback=self.parse, meta={'pos': pos})

    def closed(self, reason):
        with open('dominios.json', 'w') as file:
            json.dump(WP_dominios, file)
