import math
import requests
import re
from bs4 import BeautifulSoup


def get_html_part_from_response(response):
    response_text = response.text

    pattern = re.compile(r'var materials=.*}', re.DOTALL)
    match = pattern.search(response_text)
    matched = match.group()

    html = matched.split(':', 1)[1]

    html = html.replace("\\n", "")

    html = html.replace('\\', '')

    html = html.replace('"', '', 1).strip()

    return html


def parse_reviews(html: str) -> (list[dict], dict):
    """
    Parse all the reviews from the html and also get the review for each type
    :param html:
    :return: (list of reviews, review for each type)
    """

    soup = BeautifulSoup(html, 'html.parser')

    review_list = []
    review_for_each_type = {}

    reviews = soup.find_all('div', class_=re.compile('BVRRContentReview'))

    for review in reviews:
        star_rating = review.find('img', class_='BVImgOrSprite')['title'].split("/")[0]

        review_date = review.find('meta', itemprop='datePublished')['content']

        review_title = review.find('span', class_='BVRRReviewTitle').text

        review_text = review.find('div', class_='BVRRReviewTextContainer').text

        reviewer_username = review.find('span', class_='BVRRNickname').text

        review_list.append({
            'star_rating': star_rating,
            'review_date': review_date,
            'review_title': review_title,
            'review_text': review_text,
            'reviewer_username': reviewer_username
        })

    review_by_category_box = soup.find('div', class_='BVRRRatingContainerRadio')
    if review_by_category_box is not None:
        review_types = review_by_category_box.find_all('div', class_='BVRRRatingEntry')
    else:
        review_types = []

    for review_type in review_types:
        review_type_name = review_type.find('div', class_='BVRRRatingHeader').text

        review_type_value = review_type.find('img', class_='BVImgOrSprite')['title'].split("/")[0]

        review_for_each_type[review_type_name + " Rating"] = review_type_value

    overall_rating = soup.find('span', class_='BVRRRatingNumber').text.split("/")[0].strip()
    recommendation_rate = soup.find('span', class_="BVRRBuyAgainPercentage").text.strip()
    number_of_reviews = soup.find('span', class_='BVRRBuyAgainTotal').text.strip()

    review_for_each_type['Overall Rating'] = overall_rating
    review_for_each_type['Recommendation Rate'] = recommendation_rate
    # review_for_each_type['Number of Reviews'] = number_of_reviews

    return review_list, review_for_each_type


def reviews_crawler(product_id, model_id, number_of_reviews: int = 10):
    reviews = []
    review_for_each_type = {}

    number_of_pages = math.ceil(number_of_reviews / 10)

    request_url = f"https://adidasjp.ugc.bazaarvoice.com/7896-ja_jp/{model_id}/reviews.djs"

    params = {
        'format': 'embeddedhtml',
        'page': 1,
        'productattribute_itemKcod': product_id,
        'scrollToTop': 'true'
    }

    for page_no in range(1, number_of_pages + 1):
        params['page'] = page_no
        response = requests.get(request_url, params=params)

        html_part = get_html_part_from_response(response)

        reviews_list, review_for_each_type = parse_reviews(html_part)

        reviews.extend(reviews_list)

    return reviews, review_for_each_type


# To test the function
if __name__ == '__main__':
    reviews, review_for_each_type = reviews_crawler('B75807', 83)
    print(reviews)
    print(review_for_each_type)
