from selectolax.lexbor import LexborHTMLParser

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
            for d1, d2 in zip((parser := LexborHTMLParser(listings_page)).css('[class="Card--title"]'), parser.css('[class="Card small"]')):
                self.data['hotel'].append(d1.text(strip=True))
                self.data['rating'].append(found.attributes['class'][18:25] if (found := d1.css_first('span.StarsRating')) else '0')
                self.data['link'].append(d2.attributes['href'][66:])
        
        return self.data
    
    def extract_emails(self, raw_emails):
        if not raw_emails:
            raise ValueError('Expected an array of encoded emails')
            
        return [self._decoder(parser.attributes['data-mailto-token'][7:])
                if (parser := LexborHTMLParser(email).css_first('[data-mailto-token]')) else '0'
                for email in raw_emails]
      
    def extract_email(self, raw_email):
        if not isinstance(raw_email, str):
            raise ValueError('Expected encoded email string')
            
        return self._decoder(parser.attributes['data-mailto-token'][7:]) if (parser := LexborHTMLParser(raw_email).css_first('[data-mailto-token]')) else '0'