import scrapy
from urllib.parse import urlencode
import json
import socket
import whois
API_KEY = '8933396e1dcb28b7beffb12a05c5e341'


def get_url(url):
    payload = {'api_key': API_KEY, 'url': url,
               'autoparse': 'true', 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class ScanWp(scrapy.Spider):
    name = 'scanWp'
    allowed_domains = []

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'RETRY_TIMES': 5
    }

    def __init__(self, domain=None, *args, **kwargs):
        super(ScanWp, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://{domain}']
        self.domain = domain

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(get_url(url), self.parse, meta={'domain': url})

    def parse(self, response):

        if response.status == 200:
            domain = self.domain
            whois_info = whois.whois(domain)
            ip = socket.gethostbyname(domain)
            host = ''
            name_servers = whois_info
            try:
                host = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                host = ''
            except whois.parser.PywhoisError:
                print("Error!! Não foi possível obter informações sobre o domínio.")

            # Testa se o website usa Wordpress e se sim, busca a sua versão na página principal
            if "wp-content" in response.text:
                version = self.extract_wordpress_version_source(response.text)
                item = {'wp': True, 'title': '', 'domain': domain, 'ip': ip, 'version': version,
                        'host': host, 'nameServers': name_servers}
                yield item
            else:
                url_feed = f'https://{domain}/feed/'
                yield scrapy.Request(get_url(url_feed), self.parse_feed, meta={'domain': domain})
        else:
            url_feed = f'https://{domain}/feed/'
            yield scrapy.Request(get_url(url_feed), callback=self.parse_source, meta={'domain': domain})

    def parse_feed(self, response):
        if response.status == 200:
            domain = self.domain
            whois_info = whois.whois(domain)

            ip = ''
            host = ''
            name_servers = whois_info
            try:
                ip = socket.gethostbyname(domain)
                host = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                host = ''
                ip = ''
            except whois.parser.PywhoisError:
                print("Error!! Não foi possível obter informações sobre o domínio.")

            # Testa se o website usa Wordpress e se sim, busca a sua versão no feed
            if "wp-content" in response.text:
                version = self.extract_wordpress_version_feed(response.text)
                item = {'wp': True, 'title': '', 'domain': domain, 'ip': ip, 'version': version,
                        'host': host, 'nameServers': name_servers}
                yield item
            else:
                item = {'wp': False, 'title': '', 'domain': domain, 'ip': ip,
                        'host': host, 'nameServers': name_servers}
                yield item
        else:
            yield {'wp': 'notFound', 'domain': domain}

    def extract_wordpress_version_feed(self, response):
        start_marker = '<generator>https://wordpress.org/?v='
        end_marker = '</generator>'

        start_index = response.find(start_marker)
        if start_index != -1:
            end_index = response.find(end_marker, start_index)
            if end_index != -1:
                version = response[start_index +
                                   len(start_marker):end_index].strip()
                return version
            return "N/A"
        return "N/A"

    def extract_wordpress_version_source(self, response):
        start_marker = '<meta name="generator" content="WordPress '
        end_marker = '" />'

        start_index = response.find(start_marker)
        if start_index != -1:
            end_index = response.find(end_marker, start_index)
            if end_index != -1:
                version = response[start_index +
                                   len(start_marker):end_index].strip()
                return version
            return "N/A"
        return "N/A"
