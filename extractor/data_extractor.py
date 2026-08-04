from bs4 import BeautifulSoup
import re

class DataExtractor:
    def _decoder(self, string, offset=1):
        result = bytearray(string, 'latin1', 'ignore')
        
        for i, c in enumerate(result):
            if c == 97 or c == 64:
                result[i] = 122# 90, Z
            elif c == 95:
                continue
            else:
                result[i] -= offset
                
        return result.decode('latin1')
        
    def extract_listings(self, raw_listings):
        if not raw_listings:
            raise ValueError('Expected an array of html')
            
        self.data = {'hotel': [], 'rating': [], 'link': []}
        for listings_page in raw_listings:
            for e in BeautifulSoup(listings_page, 'lxml').find_all('a', 'Card small'):
                self.data['hotel'].append(e.text.split('\n')[7].strip())
                self.data['link'].append(e.get('href').split('/')[-1])
                self.data['rating'].append(found['class'][2] if (found := e.find('span', class_=re.compile(r'Stars*'))) else '0')

        return self.data
        
    def extract_emails(self, raw_emails):
        if not raw_emails:
            raise ValueError('Expected an array of encoded emails')

        return [self._decoder(soup["data-mailto-token"][7:])
                if (soup := BeautifulSoup(email, 'lxml').find(attrs={"data-mailto-token": True}))
                else '0' 
                for email in raw_emails]
