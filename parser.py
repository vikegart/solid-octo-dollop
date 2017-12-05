import logging
import time
from random import randint
from threading import Thread

import requests
from bs4 import BeautifulSoup
from math import ceil

AVITO_URL = 'https://m.avito.ru/'
AD_PER_PAGE = 20


class ParserBadRequestError(Exception):
    pass


class Parser:
    __slots__ = ['url', 'count', 'current']
    parsed = set()
    task = Thread()

    @classmethod
    def _download_html(cls, url):
        html = requests.get(url)
        html_text = html.text
        soup = BeautifulSoup(html_text, 'html5lib')
        return soup

    @classmethod
    def _get_all_ads(cls, soup):
        articles = soup.find_all('article', class_='b-item js-catalog-item-enum ')
        adds = []
        for add in articles:
            add_link = add.find('a').get('href')
            adds.append(add_link)
        return adds

    @classmethod
    def _get_phone(cls, url):
        soup = cls._download_html(url)
        link = cls._find_button_href(soup)
        return cls._make_request(link)

    @classmethod
    def _find_button_href(cls, soup):
        button_a = soup.find('a', attrs='person-action')
        button_href = button_a.get('href')
        return button_href

    @classmethod
    def _make_request(cls, link):
        url = AVITO_URL + link
        headers = {
            'Referer': url
        }

        url_for_request = f'{url}?async'
        request = requests.get(url_for_request, headers=headers)
        answer = request.text
        phone = cls._get_phone_number_from_answer(answer)
        return phone

    @classmethod
    def _get_phone_number_from_answer(cls, answer):
        text = answer.replace('"', ' ').replace('{', '').replace('}', ' ').strip()
        text_list = text.split(':')
        phone = text_list[1].strip()
        return phone

    @classmethod
    def _parse(cls):
        page_count = int(ceil(cls.count / AD_PER_PAGE))
        for i in range(page_count):
            page_url = cls.url + '?p=' + str(i + 1)

            try:
                main_soup = cls._download_html(page_url)
                ads = cls._get_all_ads(main_soup)

                for _, ad in enumerate(ads[:cls.count - cls.current]):
                    cls.current += 1
                    full_url = AVITO_URL + ad
                    phone = cls._get_phone(full_url)
                    cls.parsed.add(phone)
                    logging.info('{} {} {} / {}'.format(phone, page_url, cls.current, cls.count))
            except Exception as e:
                logging.exception(e)
                time.sleep(60)
            finally:
                time.sleep(randint(30, 60))

    @classmethod
    def parser_running(cls):
        return cls.task.is_alive()

    @classmethod
    def start_parsing(cls, url, count):
        cls.url = url
        cls.count = count
        cls.current = 0
        if not cls.parser_running():
            cls.task = Thread(target=cls._parse)
            cls.task.daemon = True
            cls.task.start()
        else:
            raise ParserBadRequestError('parser is already running')

    @classmethod
    def stop_parsing(cls):
        if cls.parser_running():
            cls.task = Thread()
        else:
            raise ParserBadRequestError('parser isn\'t running')

    @classmethod
    def clear(cls):
        if cls.parser_running():
            raise ParserBadRequestError('you can\'t clear output while parser is running')
        else:
            cls.parsed.clear()
