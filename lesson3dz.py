from requests import get
from bs4 import BeautifulSoup as BS
import regex
import time

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///list_of_vacancy.db', echo=False)
Base = declarative_base()


class ListOfVacancy(Base):
    __tablename__ = 'list_of_vacancy'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    site = Column(String)

    def __init__(self, name, link, salary_min, salary_max, site):
        self.name = name
        self.link = link
        self.salary_min = int(salary_min)
        self.salary_max = int(salary_max)
        self.site = site

    def __repr__(self):
        return "<User('%s','%s', '%s',  '%s', '%s')>" % (self.name, self.link, self.salary_min,
                                                         self.salary_max, self.site)


def get_data_from_url(pages, base_url, div_class):
    '''
    :param pages: Глубина поиска
    :param base_url: базовая ссылка (зависит от сайта)
    :param div_class: класс, по которому берется информация о вакансии
    :return: строка со всеми div по параметрам, для дальнейшего индивидуального парсинга
    '''
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
    '''
    :param vacancy_list: Список вакансий
    :param name: имя вакансии
    :param link: ссылка на вакансию
    :param salary_min: минимальная ЗП вакансии
    :param salary_max: максимальная ЗП вакансии
    :param site: сайт вакансии
    :return: обновленный список вакансий
    '''
    vacancy_data = {}
    vacancy_data['name'] = name
    vacancy_data['link'] = link
    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['site'] = site
    vacancy_list.append(vacancy_data)


def search_vacancy_min_salary(vacancy_salary_min):
    '''
    :param vacancy_salary_min: минимальная ЗП
    :return: список вакансий
    '''
    result_list_vacancy = []
    for instance in session.query(ListOfVacancy).filter(ListOfVacancy.salary_min > vacancy_salary_min):
        result_list_vacancy.append({'name': instance.name, 'link': instance.link, 'salary_min': instance.salary_min,
                                    'salary_max': instance.salary_max, 'site': instance.site})
    return result_list_vacancy


vacancy_list = []
vacancy = input('Укажите название вакансии: ')
while True:
    pages = input('Укажите, кол-во странниц для поиска : ')
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
            salary_min = 0
            salary_max = 0
        else:
            vacancy_price = vacancy_price.text.replace(u'\xa0', '')
            if regex.findall(r'от', vacancy_price):
                salary_min = ''.join(regex.findall(r'от ([0-9]+)', vacancy_price))
                if regex.findall(r'до', vacancy_price):
                    salary_max = ''.join(regex.findall(r'до ([0-9]+)', vacancy_price))
                else:
                    salary_max = 0
            else:
                if regex.findall(r'до', vacancy_price):
                    salary_min = 0
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
            salary_min = 0
            salary_max = 0
        else:
            vacancy_price = vacancy_price.replace(u'\xa0', '')
            if regex.findall(r'от', vacancy_price):
                salary_min = ''.join(regex.findall(r'от([0-9]+)', vacancy_price))
                if regex.findall(r'до', vacancy_price):
                    salary_max = ''.join(regex.findall(r'до([0-9]+)', vacancy_price))
                else:
                    salary_max = 0
            else:
                if regex.findall(r'до', vacancy_price) :
                    salary_min = 0
                    salary_max = ''.join(regex.findall(r'до([0-9]+)', vacancy_price))
                else:
                    if regex.findall(r'—', vacancy_price):
                        salary_min = ''.join(regex.findall(r'([0-9]+)—', vacancy_price))
                        salary_max = ''.join(regex.findall(r'—([0-9]+)', vacancy_price))
                    else:
                        salary_min = ''.join(regex.findall(r'([0-9]+)', vacancy_price))
                        salary_max = ''.join(regex.findall(r'([0-9]+)', vacancy_price))
        vacancy_list_forming(vacancy_list, vacancy_name, vacancy_link, salary_min, salary_max, site)

# Работа с базой данный
Base.metadata.create_all(engine) # без этого выдавало ошибку в вашем примере
list_of_vacancy = ListOfVacancy.__table__
metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()

for vacancy_line in vacancy_list:
    vacancy_next = ListOfVacancy(vacancy_line['name'], vacancy_line['link'], vacancy_line['salary_min'],
                                 vacancy_line['salary_max'], vacancy_line['site'])
    session.add(vacancy_next)
session.commit()

while True:
    vacancy_salary_min = input('Введите минимальную ЗП вакансии :> ')
    try:
        vacancy_salary_min = int(vacancy_salary_min)
        break
    except ValueError:
        print('Ошибка! Введите, пожалуйста, число')

for vacancy_line in search_vacancy_min_salary(vacancy_salary_min):
    print(f'*****************\n'
          f'Название вакансии - {vacancy_line["name"]} \n'
          f'Ссылка - {vacancy_line["link"]}\n'
          f'Минимальная ЗП из вилки - {vacancy_line["salary_min"]}\n'
          f'Максимальная ЗП из вилки - {vacancy_line["salary_max"]}\n'
          f'Сайт вакансии - {vacancy_line["site"]}')

session.close()
