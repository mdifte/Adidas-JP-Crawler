import requests
from bs4 import BeautifulSoup
import json
from reviews_crawler import reviews_crawler
import csv


def get_size_chart(model_id) -> dict:
    response = requests.get(f"https://shop.adidas.jp/f/v1/pub/size_chart/{model_id}")
    json_response = response.json()

    size_chart = json_response['size_chart']

    if not size_chart:
        return {}
    else:
        size_chart = size_chart['0']

    header_values = [header_label['value'] for key, header_label in size_chart['header']['0'].items()]
    body_values = [[item['value'] for item in row.values()] for row in size_chart['body'].values()]

    result = {
        row[0]: dict(zip(header_values[1:], row[1:]))
        for row in body_values
    }

    return result


def parse_product_details(json_response: dict) -> dict:
    breadcrumbs_list: list[dict] = json_response['page']['breadcrumbs']
    full_breadcrumbs = ' >> '.join([breadcrumb['label'] for breadcrumb in breadcrumbs_list])

    bottom_keywords_category = json_response['page']['categories']
    keywords = [category['label'] for category in bottom_keywords_category]

    product_details = json_response['product']
    article_code = product_details['article']['articleCode']

    skus: list[dict] = product_details['article']['skus']  # Can get available sizes from here
    sizes = [sku['sizeName'] for sku in skus]

    name = product_details['article']['name']
    price = product_details['article']['price']['current']['withTax']

    description_title = product_details['article']['description']['messages']['title']
    description_text = product_details['article']['description']['messages']['mainText']
    description_itemized_list = product_details['article']['description']['messages']['breads']

    image_urls = ['https://shop.adidas.jp'+image['imageUrl']['large'] for image in product_details['article']['image']['details']]
    video_urls = [video['movieUrl'] for video in product_details['article']['image']['videos']]

    coordinates = product_details['article']['coordinates']
    if coordinates:
        coordinates = coordinates['articles']
    else:
        coordinates = []

    coordinates_list = []

    for coordinate in coordinates:
        coordinates_list.append({
            'name': coordinate['name'],
            'image': coordinate['image'],
            'articleCode': coordinate['articleCode'],
            'price': coordinate['price']['current']['withTax'],
            'url': 'https://shop.adidas.jp/products/' + coordinate['articleCode']
        })

    model_details = product_details['model']
    model_code = model_details['modelCode']

    brand_names = model_details['attributes']['brand']
    gender = model_details['attributes']['gender']

    if len(brand_names) > 0 and len(gender) > 0:
        category_brand_name = gender[0]['name'] + ' ' + brand_names[0]['name']
    else:
        category_brand_name = "None"

    size_chart = get_size_chart(model_details['modelCode'])

    number_of_reviews = model_details['review']['reviewCount']

    if number_of_reviews is not None:
        reviews, review_for_each_type = reviews_crawler(article_code, model_code, int(number_of_reviews))
    else:
        number_of_reviews = 0
        reviews = []
        review_for_each_type = {}

    output_dict = {
        'URL': f"https://shop.adidas.jp/products/{article_code}/",
        'name': name,
        'category_brand_name': category_brand_name,
        'image_urls': image_urls,
        'video_urls': video_urls,
        'full_breadcrumbs': full_breadcrumbs,
        'coordinates': coordinates_list,
        'sizes': sizes,
        'size_chart': size_chart,
        'price': price,
        'description_title': description_title,
        'description_text': description_text,
        'description_itemized_list': description_itemized_list,
        'keywords': keywords,
        'number_of_reviews': number_of_reviews,
        'review_list': reviews,
    }
    output_dict.update(review_for_each_type)

    return output_dict


def product_details_crawler(product_id) -> dict:
    response = requests.get(f"https://shop.adidas.jp/f/v2/web/pub/products/article/{product_id}/")
    if response.status_code != 200:
        return {}

    json_response = response.json()

    return parse_product_details(json_response)


if __name__ == '__main__':
    crawled_data = product_details_crawler('IK4982')

    headers = crawled_data.keys()

    # Output the data to a CSV file
    with open('product_details.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(crawled_data)
