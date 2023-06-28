import scrapy
from urllib.parse import urlencode
import json
import socket
import whois
import mysql.connector

API_KEY = '8933396e1dcb28b7beffb12a05c5e341'


def get_url(url):
    payload = {'api_key': API_KEY, 'url': url,
               'autoparse': 'true', 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class Version(scrapy.Spider):
    name = 'version2'
    allowed_domains = []

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'RETRY_TIMES': 5
    }

    def start_requests(self):
        with open('./dominios.json') as file:
            domains = json.load(file)

        create_database_if_not_exists()
        create_table_if_not_exists()

        for domain in domains:
            url = f'https://{domain}'
            yield scrapy.Request(get_url(url), self.parse, meta={'domain': domain})

    def parse(self, response):
        domain = response.meta['domain']
        if response.status == 200:
            whois_info = whois.whois(domain)
            name_servers = whois_info.name_servers
            host = ''
            ip = ''
            try:
                ip = socket.gethostbyname(domain)
                host = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                host = ''
                ip = ''
            except whois.parser.PywhoisError:
                print("Error!! Não foi possível obter informações sobre o domínio.")

            if "wp-content" in response.text:
                version = self.extract_wordpress_version_source(response.text)
                item = {'wp': True, 'title': '', 'domain': domain, 'ip': ip, 'version': version,
                        'host': host, 'nameServers': name_servers}
                insert_domain_info(item)
                yield item
            else:
                url_feed = f'https://{domain}/feed/'
                yield scrapy.Request(get_url(url_feed), self.parse_feed, meta={'domain': domain})
        else:
            url_feed = f'https://{domain}/feed/'
            yield scrapy.Request(get_url(url_feed), callback=self.parse_feed, meta={'domain': domain})

    def parse_feed(self, response):
        domain = response.meta['domain']
        if response.status == 200:
            whois_info = whois.whois(domain)

            name_servers = whois_info.name_servers
            host = ''
            ip = ''
            try:
                ip = socket.gethostbyname(domain)
                host = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                host = ''
                ip = ''
            except whois.parser.PywhoisError:
                print("Error!! Não foi possível obter informações sobre o domínio.")

            if "wp-content" in response.text:
                version = self.extract_wordpress_version_feed(response.text)
                item = {'wp': True, 'title': '', 'domain': domain, 'ip': ip, 'version': version,
                        'host': host, 'nameServers': name_servers}
                insert_domain_info(item)
                yield item
            else:
                item = {'wp': False, 'title': '', 'domain': domain, 'ip': ip,
                        'host': host, 'nameServers': name_servers}

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


def create_database_if_not_exists():
    db_connection = mysql.connector.connect(
        host='172.16.179.36',
        user='WP',
        password='123WP'
    )
    db_cursor = db_connection.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS pt_WordPress1")
    db_connection.close()


def create_table_if_not_exists():
    db_connection = mysql.connector.connect(
        host='172.16.179.36',
        user='WP',
        password='123WP',
        database='pt_WordPress1'
    )
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_info2 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            domain VARCHAR(255) UNIQUE,
            ip VARCHAR(255),
            version VARCHAR(20),
            host VARCHAR(255),
            name_servers VARCHAR(255)
        )
    """)
    db_connection.close()


def insert_domain_info(item):
    db_connection = mysql.connector.connect(
        host='172.16.179.36',
        user='WP',
        password='123WP',
        database='pt_WordPress1'
    )
    db_cursor = db_connection.cursor()

    domain = item['domain']
    ip = item['ip']
    version = item['version']
    host = item['host']
    name_servers = ', '.join(item['nameServers'])

    select_query = "SELECT domain FROM domain_info2 WHERE domain = %s"
    db_cursor.execute(select_query, (domain,))
    existing_domain = db_cursor.fetchone()

    if existing_domain:
        update_query = """
            UPDATE domain_info2
            SET ip = %s, version = %s, host = %s, name_servers = %s
            WHERE domain = %s
        """
        db_cursor.execute(update_query, (ip, version,
                          host, name_servers, domain))
    else:
        insert_query = """
            INSERT INTO domain_info2 (domain, ip, version, host, name_servers)
            VALUES (%s, %s, %s, %s, %s)
        """
        db_cursor.execute(
            insert_query, (domain, ip, version, host, name_servers))

    db_connection.commit()
    db_connection.close()
