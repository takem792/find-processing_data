import requests
from lxml import html
import regex
import datetime


def request_to_site(site):
    '''
    Получение ответа от сайта
    :param site: Сайт
    :return: Ответ от сайта в виде html для парсинга и сайт
    '''
    headers = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36'
                                              ' (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

    request = requests.get(f'{site}', headers=headers, timeout=120)
    root = html.fromstring(request.text)
    return root, site


def yandex_content(news_list):
    '''
    Для яндекса
    :param news_list: контейнер с новостями
    :return: обновленный контейне
    '''
    root, site = request_to_site('https://yandex.ru')
    data_res = root.xpath("//span[@class='datetime text_gray_yes i-bem']")
    date = ''.join(regex.findall(r'\":\"([a-zA-Z0-9 ,]+:)', str(html.tostring(data_res[0]))))[:-5]

    news = root.xpath("//a[@class='home-link list__item-content list__item-content_with-icon home-link_black_yes']")
    for n in news:
        l_month = {'September': '09'} #Лень было все прописывать :)
        yandex_news = {}
        yandex_news['site'] = site
        yandex_news['name'] = n.attrib['aria-label']
        yandex_news['link'] = n.attrib['href']
        yandex_news['date'] = date[len(date)-4:] + '/' + l_month[''.join(regex.findall(r'([a-zA-Z]+)', date))] + \
                              '/' + ''.join(regex.findall(r'([0-9]+),', date))
        news_list.append(yandex_news)
    return news_list


def lenta_content(news_list):
    '''
    Для Ленты
    :param news_list: контейнер с новостями
    :return: обновленный контейне
    '''
    root, site = request_to_site('https://lenta.ru')

    news = root.xpath("//section[@class='b-yellow-box js-yellow-box']//div[@class='item']/a[not(@class)]")
    for n in news:
        lenta_news = {}
        lenta_news['site'] = site
        lenta_news['name'] = n.text
        lenta_news['link'] = site + n.attrib['href']
        lenta_news['date'] = n.attrib['href'][:16][6:]
        news_list.append(lenta_news)


def mail_content(news_list):
    '''
    Для мейла
    :param news_list: контейнер с новостями
    :return: обновленный контейне
    '''
    root, site = request_to_site('http://mail.ru')
    news = root.xpath("//div[@class='news']//a")
    print(news[0])
    with open('test.txt', 'w', encoding='utf-8') as file:
        file.write(str(html.tostring(news[1])))
    for n in news:
        lenta_news = {}
        lenta_news['site'] = site
        lenta_news['name'] = n.text
        lenta_news['link'] = n.attrib['href']
        lenta_news['date'] = str(datetime.datetime.now().year) + "/" + str(datetime.datetime.now().month) + \
                             "/" + str(datetime.datetime.now().day)
        news_list.append(lenta_news)

def news_print(news_list):
    '''
    Вывод на печать
    :param news_list: контейнер с новостями
    :return:
    '''
    for news_line in news_list:
        print(f'*****************\n'
              f'Название публикации - {news_line["name"]} \n'
              f'Ссылка на публикацию - {news_line["link"]}\n'
              f'Дата публикации - {news_line["date"]}\n'
              f'Новостной сайт - {news_line["site"]}')


if __name__ == '__main__':
    news_list = []
    yandex_content(news_list)
    lenta_content(news_list)
    mail_content(news_list)
    news_print(news_list)
