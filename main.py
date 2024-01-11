import configparser
import time

from furl import furl

from checkers import check_price_changes, check_sold_cars, check_is_url_in_db
from db_tools import create_db
from scrap_tools import get_all_hrefs, scrap


def main():
    config = configparser.ConfigParser()
    config.read('conf.config')

    auto_ria_start_url = config.get('AUTORIA', 'START_URL')
    headers = {'user-agent': config.get('HEADERS', 'USER_AGENT')}

    create_db()

    while True:
        furl_auto_ria_url = furl(auto_ria_start_url)
        urls = get_all_hrefs(headers, furl_auto_ria_url)
        fresh_urls = check_is_url_in_db(urls)

        scrap(fresh_urls, headers)

        check_sold_cars(urls)
        check_price_changes(headers, urls)

        time.sleep(600)


if __name__ == '__main__':
    main()
