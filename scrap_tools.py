import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from db_tools import put_to_db, DatabaseManager
from tg_tools import send_message_with_photos


def get_all_hrefs(headers: Dict, furl_start_url) -> List:
    all_hrefs = []
    while True:
        url = furl_start_url
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        hrefs = soup.find_all('a', class_='m-link-ticket')
        if len(hrefs) == 0:
            break
        for h in hrefs:
            all_hrefs.append(h.get('href'))
        url.args['page'] = str(int(url.args['page']) + 1)
    return all_hrefs


def scrap(fresh_hrefs: List, headers: Dict):
    with DatabaseManager() as cursor:

        for auto_ria_url in fresh_hrefs:

            resp = requests.get(url=auto_ria_url, headers=headers)
            soup = BeautifulSoup(resp.content, "lxml")

            photo_gal = soup.find('div', class_='preview-gallery').find_all('source')
            all_photo = []
            for photo in photo_gal:
                photo_small = photo.get('srcset')
                photo_full = re.sub(r'(\d+)s', r'\1f', photo_small)
                all_photo.append(photo_full)

            price = soup.find('div', class_='price_value').find('strong').get_text(strip=True)

            auction_url = None
            try:
                auction_url = soup.find('div', class_='vin-checked mb-15 _grey').find('a').get('href', auction_url)
            except AttributeError:
                pass

            match = re.search(r'(\d+).html', auto_ria_url)
            car_id = match.group(1)

            brand = 'Toyota'

            message = f"Марка: {brand}\nЦіна: {price}\nПосилання: {auto_ria_url}\nПосилання на аукціон: {auction_url}"
            send_message_with_photos(message, all_photo)
            put_to_db(cursor, auto_ria_url, all_photo, brand, price, auction_url, car_id)
