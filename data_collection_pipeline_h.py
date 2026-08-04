from fetcher.data_fetcher import DataFetcher
from extractor.data_extractor import DataExtractor
from extractor.data_extractor_fast import DataExtractor as DataExtractorFast
from common.common_tools import perf_test

import pandas as pd
from dotenv import load_dotenv
import os
import time
from concurrent.futures import ThreadPoolExecutor

# load_dotenv()
load_dotenv('.env.example')

class DataCollectionPipeline:
    def __init__(self):
        self.DEBUG_MODE = bool(os.getenv('DEBUG_MODE'))
        self.BASE_URL = 'https://www.example.com/' if self.DEBUG_MODE else os.getenv('BASE_URL')
        self.ran = False

        self.fetcher = DataFetcher()
        self.extractor = DataExtractor()
        self.extractor_fast = DataExtractorFast()

    def run(self):
        print("Starting data collection pipeline...")

        print("Begin fetching online hotel listings...")
        # pages = 367
        pages = 3
        self.raw_listings = self.fetcher.get_listings(pages=pages)
        print(f"Successfully fetched {len(self.raw_listings)} page(s) of hotel listings online.")

        print("Begin extracting data from hotel listings...")
        self.data = self.extractor.extract_listings(self.raw_listings)
        print(f"Successfully extracted data from {len(self.data['hotel'])} hotel listings...")

        print("Begin fetching encoded hotel contacts online...")
        self.data['link'] = [f'{self.BASE_URL}{link}' for link in self.data['link']]
        self.raw_emails = self.fetcher.get_emails(self.data['link'])
        print(f"Successfully fetched {len(self.raw_emails)} encoded hotel contacts online.")

        print("Begin extracting and decoding hotel contacts...")
        self.data['email'] = self.extractor.extract_emails(self.raw_emails)
        print(f"Successfully extracted and decoded {len(self.data['email'])} hotel contacts...")

        pd.DataFrame(self.data).to_csv('hotel_details.csv', index=False, encoding='utf-8-sig')
        print('CSV exported hotel data.')

        self.ran = True
        print("Completed running data collection pipeline.")

    def run_extractor_perf_test(self):
        if not self.ran:
            raise RuntimeError('Run the data collection pipeline to fetch the raw html first before running the extractor performance test.')

        raw_emails_size = len(self.raw_emails)
        sample = None

        print("Begin running hotel contact extractor performance test...")
        avg_runtime = perf_test(func=self.extractor.extract_emails, data=self.raw_emails, sample=sample)
        print(f"Average runtime of hotel contact extractor extracting {raw_emails_size} contacts: {round(avg_runtime, 4)} second(s)")

        avg_runtime = perf_test(func=self.extractor_fast.extract_emails, data=self.raw_emails, sample=sample)
        print(f"Average runtime of hotel contact extractor (fast) extracting {raw_emails_size} contacts: {round(avg_runtime, 4)} second(s)")

        # better performance (3x) when dealing with larger sample (above 200)
        avg_runtime = self._parallelized_perf_test(func=self.extractor_fast.extract_email, data=self.raw_emails, sample=sample)
        print(f"Average runtime of parallelized hotel contact extractor (fast) extracting {raw_emails_size} contacts: {round(avg_runtime, 4)} second(s) (requires larger sample to show better performance)")

        print("Hotel contact extractor performance test completed.")

    def _parallelized_perf_test(self, func, data, rounds=30, sample=100, mode=''):
        results = []

        for _ in range(rounds):
            with ThreadPoolExecutor() as executor:
                start = time.perf_counter()
                
                list(executor.map(func, data[:sample]))
                
                end = time.perf_counter()
            
            results.append(end-start)

        return sum(results)/rounds

if __name__ == '__main__':
    pipeline = DataCollectionPipeline()
    pipeline.run()
    pipeline.run_extractor_perf_test()