import time
import requests
import configparser
from bs4 import BeautifulSoup


AVITO_URL = 'https://m.avito.ru/'


def get_parser_config():
    if hasattr(get_parser_config, 'conf'):
        return getattr(get_parser_config, 'conf')

    conf = configparser.RawConfigParser()
    conf.read(['parser.properties'])
    setattr(get_parser_config, 'conf', conf['parser'])
    return get_parser_config()


def downloadHTLM(url) -> BeautifulSoup:
    html = requests.get(url)
    htmlText = html.text
    soup = BeautifulSoup(htmlText, 'lxml')
    return soup


def getAllAdds(soup) -> list:
    articles = soup.find_all('article', class_='b-item js-catalog-item-enum ')
    adds = []
    for add in articles:
        addLink = add.find('a').get('href')
        adds.append(addLink)
    return adds


def getPhone(url) -> str:
    soup = downloadHTLM(url)
    link = findButtonHref(soup)
    return makeRequest(link)


def findButtonHref(soup) -> str:
    buttonA = soup.find('a', attrs='person-action')
    buttonHref = buttonA.get('href')
    return buttonHref


def makeRequest(link) -> str:
    url = AVITO_URL + link
    headers = {
        'Referer': url
    }

    urlForRequest = f'{url}?async'
    request = requests.get(urlForRequest, headers=headers)
    answer = request.text
    phone = getPhoneNumberFromAnswer(answer)
    return phone


def getPhoneNumberFromAnswer(answer) -> str:
    text = answer.replace('"', ' ').replace('{', '').replace('}', ' ').strip()
    textList = text.split(':')
    phone = textList[1].strip()
    return phone


def main(start, end):
    urlMain = '{}?user=2'.format(get_parser_config()['scan_url'])
    for i in range(start, end):
        URL = urlMain + '&p=' + str(i)
        try:
            mainSoup = downloadHTLM(URL)
            adds = getAllAdds(mainSoup)
            for j, add in enumerate(adds):
                time.sleep(15)
                url = AVITO_URL + add
                phone = getPhone(url)

                with open(get_parser_config()['out_file'], 'a') as f:
                    f.write(phone + ' ' + url + '\n')
                print(phone, url, '{} / {}'.format(j + 1, len(adds)), i)
        except Exception as e:
            import logging
            logging.getLogger().exception(e)
            time.sleep(60)
            main(i, end)


if __name__ == '__main__':
    main(1, 2)
