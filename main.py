import time

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from product_details_crawler import product_details_crawler
from search_page_crawler import search_page_crawler
from concurrent.futures import ThreadPoolExecutor

search_url = 'https://shop.adidas.jp/item/?gender=mens&category=wear&order=10&limit=120'
pages_to_crawl = 2

search_result = search_page_crawler(search_url, pages_to_crawl)

scraped_data = []


def thread_function(product_id):
    print("Scraping product: ", product_id)
    try:
        product_details_ = product_details_crawler(product_id)
        scraped_data.append(product_details_)
    except Exception as err:
        print(f"Error scraping product: {product_id}: {err}")


with ThreadPoolExecutor(max_workers=10) as executor:
    for product_id, data in search_result.items():
        executor.submit(thread_function, product_id)

    executor.shutdown(wait=True)

time.sleep(30)
df = pd.DataFrame(scraped_data)
df.to_excel('crawled_data.xlsx', index=False)
