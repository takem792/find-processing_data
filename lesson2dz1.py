from requests import get
from bs4 import BeautifulSoup as BS
import regex
import time
import pandas as pd


def get_data_from_url(pages, base_url, div_class):
    headers = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36'
                                              ' (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    lineres = ''  # результат в str для файла
    for i in range(int(pages)):
        request = get(base_url + str(i), headers=headers, timeout=120)
        if request.status_code == 404:
            break
        else:
            parsed_html = BS(request.text, 'lxml')
            vacancy_block = parsed_html.find_all('div', div_class)
        for line in vacancy_block:
            lineres = lineres + line.__str__()
        time.sleep(1)
    return lineres


def vacancy_list_forming(vacancy_list, name, link, salary_min, salary_max, site):
    vacancy_data = {}
    vacancy_data['name'] = name
    vacancy_data['link'] = link
    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['site'] = site
    vacancy_list.append(vacancy_data)


pd.options.display.max_columns = 5
pd.set_option('display.width', 2000)
vacancy_list = []

vacancy = input('Укажите название вакансии: ')
while True:
    pages = input('Укажите, кол-во странниц для поиска -> ')
    try:
        pages_is_int = int(pages)
        break
    except ValueError:
        print('Ошибка, введите, пожалуйста, число')

#hh
site = 'hh.ru'
base_url = f'https://hh.ru/search/vacancy?area=1&search_period=30&text={vacancy}&page='
div_class = {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'}
data = get_data_from_url(pages, base_url, div_class)
if data == '':
    print(f'по вакансии {vacancy} предложений нет')
else:
    parsed_html = BS(data, 'lxml')
    vacancy_block = parsed_html.find_all('div', div_class)
    for vacancy_id in vacancy_block:
        vacancy_link = vacancy_id.find('a').get('href')[:30]
        vacancy_name = vacancy_id.find('a').text
        # Определяем цену вакансии
        vacancy_price = vacancy_id.find('div', {'class': 'vacancy-serp-item__compensation'})
        if vacancy_price is None:
            salary_min = None
            salary_max = None
        else:
            vacancy_price = vacancy_price.text.replace(u'\xa0', '')
            if regex.findall(r'от', vacancy_price):
                salary_min = ''.join(regex.findall(r'от ([0-9]+)', vacancy_price))
                if regex.findall(r'до', vacancy_price):
                    salary_max = ''.join(regex.findall(r'до ([0-9]+)', vacancy_price))
                else:
                    salary_max = None
            else:
                if regex.findall(r'до', vacancy_price):
                    salary_min = None
                    salary_max = ''.join(regex.findall(r'до ([0-9]+)', vacancy_price))
                else:
                    salary_min = ''.join(regex.findall(r'([0-9]+)-', vacancy_price))
                    salary_max = ''.join(regex.findall(r'-([0-9]+)', vacancy_price))
        vacancy_list_forming(vacancy_list, vacancy_name, vacancy_link, salary_min, salary_max, site)
## superjob.ru
site = 'superjob.ru'
base_url = f'https://www.superjob.ru/vacancy/search/?keywords={vacancy}&page='
div_class = {'class': '_3syPg _1_bQo _2FJA4'}
data = get_data_from_url(pages, base_url, div_class)
if data == '':
    print(f'по вакансии {vacancy} предложений нет')
else:
    parsed_html = BS(data, 'lxml')
    vacancy_block = parsed_html.find_all('div', div_class)
    for vacancy_id in vacancy_block:
        vacancy_link = 'https://www.superjob.ru' + vacancy_id.find('a').get('href')
        vacancy_name = vacancy_id.find('div', {'class', '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).text
        vacancy_price = vacancy_id.find('span', {'class', '_3mfro _2Wp8I f-test-text-company-item-salary '
                                                       'PlM3e _2JVkc _2VHxz'}).text
        if vacancy_price == 'По договорённости':
            salary_min = None
            salary_max = None
        else:
            vacancy_price = vacancy_price.replace(u'\xa0', '')
            if regex.findall(r'от', vacancy_price):
                salary_min = ''.join(regex.findall(r'от([0-9]+)', vacancy_price))
                if regex.findall(r'до', vacancy_price):
                    salary_max = ''.join(regex.findall(r'до([0-9]+)', vacancy_price))
                else:
                    salary_max = None
            else:
                if regex.findall(r'до', vacancy_price) :
                    salary_min = None
                    salary_max = ''.join(regex.findall(r'до([0-9]+)', vacancy_price))
                else:
                    if regex.findall(r'—', vacancy_price):
                        salary_min = ''.join(regex.findall(r'([0-9]+)—', vacancy_price))
                        salary_max = ''.join(regex.findall(r'—([0-9]+)', vacancy_price))
                    else:
                        salary_min = ''.join(regex.findall(r'([0-9]+)', vacancy_price))
                        salary_max = ''.join(regex.findall(r'([0-9]+)', vacancy_price))
        vacancy_list_forming(vacancy_list, vacancy_name, vacancy_link, salary_min, salary_max, site)

pd_data = pd.DataFrame(vacancy_list)

print(pd_data.head(40))


