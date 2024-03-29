import requests
from bs4 import BeautifulSoup
import json


def search_page_crawler(search_link, pages_to_crawl: int = 1) -> dict:
    search_results = {}

    for page_no in range(1, pages_to_crawl + 1):
        response = requests.get(search_link + f'&page={page_no}')
        soup = BeautifulSoup(response.text, 'html.parser')

        script = soup.find('script', id='__NEXT_DATA__')

        # get the json data from the script
        json_data = json.loads(script.string)

        articles_dict = json_data['props']['pageProps']['apis']['plpInitialProps']['productListApi']['articles']

        search_results.update(articles_dict)

    return search_results


# To Test the function
if __name__ == '__main__':
    starting_url = "https://shop.adidas.jp/item/?gender=mens&limit=120"
    results = search_page_crawler(starting_url, 2)
    print(results)
    print("Total Products: ", len(results))
