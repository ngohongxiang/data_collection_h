import time
import random
import requests

from dotenv import load_dotenv
import os

import json

# load_dotenv()
load_dotenv('.env.example')

class DataFetcher:
    def __init__(self):
        self.DEBUG_MODE = bool(os.getenv('DEBUG_MODE'))
        if not self.DEBUG_MODE:
            self.BASE_URL = os.getenv('BASE_URL')
            self.FILTER_URL = os.getenv('FILTER_URL')
        else:
            try:
                with open('data/sample_responses.json', 'rb') as f:
                    self.sample_responses = json.loads(f.read())
            except Exception as e:
                print(e)

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                       'Accept-Language': 'de-CH'}
        self.ip = '150.107.140.238:3128' # free public proxy
        self.proxies = None
        # self.proxies = {'http': f'http://{self.ip}', 'https': f'http://{self.ip}'}

    def rotate_identity(self):# to be implemented
        pass 
        #self.headers['User-Agent'] = ua.random
        #self.ip = random.choice(ips)
        #self.used_identity[ip] = self.headers['User-Agent']

    def get_listings(self, pages):
        if self.DEBUG_MODE:
            return self.sample_responses['listings']
        self.raw_listings = []

        try:
            for n in range(1, pages + 1):
                url = f'{self.BASE_URL}hotel-page-{n}{self.FILTER_URL}'
                response = requests.get(url, headers=self.headers, proxies=self.proxies)
                response.raise_for_status()
                self.raw_listings.append(response.text)
                time.sleep(max(random.gauss(3, 1), 2))
            
            return self.raw_listings
        except Exception as e:
            print(e)

    def get_emails(self, links):
        if self.DEBUG_MODE:
            return self.sample_responses['contacts']
        self.email_pages = []

        try:
            for link in links:
                response = requests.get(link, headers=self.headers, proxies=self.proxies)
                response.raise_for_status()
                self.email_pages.append(response.text)
                time.sleep(max(random.gauss(3, 1), 2))

            return self.email_pages
        except Exception as e:
            print(e)
