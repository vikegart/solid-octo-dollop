import logging
import time
from random import randint
from threading import Thread

import requests
from bs4 import BeautifulSoup
from math import ceil

AVITO_URL = 'https://m.avito.ru/'
AD_PER_PAGE = 20


class ParserError(Exception):
    message = 'No message has been provided'
    code = 400


class ParserRunningError(ParserError):
    message = "You can't do this action, when parser is running"


class ParserNotRunningError(ParserError):
    message = "You can't do this action, when parser isn't running"


class Parser:
    __slots__ = ['url', 'count', 'current']
    parsed = set()
    task = Thread()

    @classmethod
    def _download_html(cls, url):
        try:
            html = requests.get(url)
            html_text = html.text
            soup = BeautifulSoup(html_text, 'html5lib')
            return soup
        except Exception as e:
            logging.exception(e)
            time.sleep(60)
            return cls._download_html(url)

    @classmethod
    def _get_all_ads(cls, page_url):
        soup = cls._download_html(page_url)
        articles = soup.find_all('article', class_='b-item js-catalog-item-enum ')
        if articles:
            ads = []
            for ad in articles:
                ad_link = ad.find('a').get('href')
                ads.append(ad_link)
            return ads
        else:
            logging.error('Failed to parse articles')
            time.sleep(60)
            return cls._get_all_ads(page_url)

    @classmethod
    def _get_phone(cls, url):
        soup = cls._download_html(url)
        try:
            link = cls._find_button_href(soup)
            return cls._make_request(link)
        except Exception as e:
            logging.exception(e)
            time.sleep(60)
            return cls._get_phone(url)

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

            ads = cls._get_all_ads(page_url)

            for _, ad in enumerate(ads[:cls.count - cls.current]):
                cls.current += 1
                full_url = AVITO_URL + ad
                phone = cls._get_phone(full_url)
                cls.parsed.add(phone)
                logging.info('{} {} {} / {}'.format(phone, page_url, cls.current, cls.count))
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
            raise ParserRunningError()

    @classmethod
    def stop_parsing(cls):
        if cls.parser_running():
            cls.task = Thread()
        else:
            raise ParserNotRunningError()

    @classmethod
    def get_status(cls):
        if cls.parser_running():
            return cls.current, cls.count
        else:
            raise ParserNotRunningError()

    @classmethod
    def clear(cls):
        if cls.parser_running():
            raise ParserRunningError()
        else:
            cls.parsed.clear()
