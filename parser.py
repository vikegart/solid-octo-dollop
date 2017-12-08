import logging
import re
import time
import urllib.parse as urlparse
from random import randint
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from threading import Thread


class ParserError(Exception):
    message = 'No message has been provided'
    code = 400


class ParserRunningError(ParserError):
    message = "You can't do this action, when parser is running"


class ParserNotRunningError(ParserError):
    message = "You can't do this action, when parser isn't running"


_AVITO_URL = 'https://m.avito.ru/'


def _make_request(link):
    url = _AVITO_URL + link
    headers = {
        'Referer': url
    }

    url_for_request = f'{url}?async'
    request = requests.get(url_for_request, headers=headers)
    answer = request.text
    text = answer.replace('"', ' ').replace('{', '').replace('}', ' ').strip()
    text_list = text.split(':')
    return text_list[1].strip()


def _download_html(url):
    try:
        html = requests.get(url)
        html_text = html.text
        soup = BeautifulSoup(html_text, 'html5lib')
        return soup
    except Exception as e:
        logging.exception(e)
        time.sleep(randint(30, 60))
        return _download_html(url)


def _get_all_ads(page_url):
    soup = _download_html(page_url)
    articles = soup.find_all('article', class_=re.compile('^b-item js-catalog-item-enum ((?!item-vip).)*$'))
    logging.debug(f'Parsed articles len: {len(articles)}')

    if articles:
        ads = []
        for ad in articles:
            ad_link = ad.find('a').get('href')
            ads.append(ad_link)
        return ads
    else:
        logging.error('Failed to parse articles')
        time.sleep(randint(30, 60))
        return _get_all_ads(page_url)


def _get_phone(url):
    soup = _download_html(url)
    try:
        button_a = soup.find('a', attrs='person-action')
        link = button_a.get('href')
        return _make_request(link)
    except Exception as e:
        logging.exception(e)
        time.sleep(60)
        return _get_phone(url)


class ParserTask:
    def __init__(self, count, url):
        self.count = count
        self.current = 0

        self._url = url
        self._thread = Thread(target=self._parse, daemon=True)
        self._alive = False

    def _parse(self):
        page = 1
        while self.current < self.count:
            params = {'p': page}

            url_parts = list(urlparse.urlparse(self._url))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urlencode(query)

            page_url = urlparse.urlunparse(url_parts)

            ads = _get_all_ads(page_url)

            for _, ad in enumerate(ads[:self.count - self.current]):
                logging.info(f'Parsing {page_url} ({self.current} / {self.count})...')
                full_url = _AVITO_URL + ad
                phone = _get_phone(full_url)
                Parser.parsed.add(phone)

                time.sleep(randint(10, 30))
                self.current += 1

            page += 1

    def start(self):
        self._alive = True
        self._thread.start()

    def stop(self):
        self._alive = False

    def running(self):
        return self._alive


class Parser:
    task = None
    parsed = set()

    @classmethod
    def parser_running(cls):
        return cls.task and cls.task.running()

    @classmethod
    def start_parsing(cls, url, count):
        if not cls.parser_running():
            cls.task = ParserTask(count, url)
            cls.task.start()
        else:
            raise ParserRunningError()

    @classmethod
    def stop_parsing(cls):
        if cls.parser_running():
            cls.task.stop()
        else:
            raise ParserNotRunningError()

    @classmethod
    def get_status(cls):
        if cls.parser_running():
            return cls.task.current, cls.task.count
        else:
            raise ParserNotRunningError()

    @classmethod
    def get_result(cls):
        print(cls.parsed)
        return list(cls.parsed)

    @classmethod
    def clear_result(cls):
        cls.parsed.clear()
