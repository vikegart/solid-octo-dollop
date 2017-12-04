import configparser
import logging
import time

import requests
from bs4 import BeautifulSoup

AVITO_URL = 'https://m.avito.ru/'


def get_parser_config():
    if hasattr(get_parser_config, 'conf'):
        return getattr(get_parser_config, 'conf')

    conf = configparser.RawConfigParser()
    conf.read(['parser.properties'])
    setattr(get_parser_config, 'conf', conf['parser'])
    return get_parser_config()


def download_html(url) -> BeautifulSoup:
    html = requests.get(url)
    html_text = html.text
    soup = BeautifulSoup(html_text, 'html5lib')
    return soup


def get_all_ads(soup) -> list:
    articles = soup.find_all('article', class_='b-item js-catalog-item-enum ')
    adds = []
    for add in articles:
        add_link = add.find('a').get('href')
        adds.append(add_link)
    return adds


def get_phone(url) -> str:
    soup = download_html(url)
    link = find_button_href(soup)
    return make_request(link)


def find_button_href(soup) -> str:
    button_a = soup.find('a', attrs='person-action')
    button_href = button_a.get('href')
    return button_href


def make_request(link) -> str:
    url = AVITO_URL + link
    headers = {
        'Referer': url
    }

    url_for_request = f'{url}?async'
    request = requests.get(url_for_request, headers=headers)
    answer = request.text
    phone = get_phone_number_from_answer(answer)
    return phone


def get_phone_number_from_answer(answer) -> str:
    text = answer.replace('"', ' ').replace('{', '').replace('}', ' ').strip()
    text_list = text.split(':')
    phone = text_list[1].strip()
    return phone


def main(start, end):
    logging.info('Parsing {} ads (from {} to {})'.format(end - start, start, end))

    file = open(get_parser_config()['out_file'], 'a')

    url = '{}?user=2'.format(get_parser_config()['scan_url'])
    p = 0
    while start < end:
        p += 1
        page_url = url + '&p=' + str(p)

        try:
            main_soup = download_html(url)

            ads = get_all_ads(main_soup)

            for j, ad in enumerate(ads[:end - start]):
                time.sleep(int(get_parser_config()['delay']))
                full_url = AVITO_URL + ad
                phone = get_phone(full_url)

                file.write('{}. {} {}\n'.format(start + j + 1, phone, full_url))
                logging.info('{} {} {} / {}'.format(phone, page_url, start + j + 1, end))

            start += len(ads)
        except Exception as e:
            logging.exception(e)
            time.sleep(int(get_parser_config()['error_delay']))
            main(p, end)

    file.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(int(get_parser_config()['from']), int(get_parser_config()['to']))
