import unicodedata
import requests
from bs4 import BeautifulSoup
import lxml
from fake_headers import Headers
import json
import time
import re
from pprint import pprint



def gen_headers():
    headers = Headers(browser='chrome', os='win')
    return headers.generate()


response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=gen_headers())
main_html = response.text
main_soup = BeautifulSoup(main_html, 'lxml')

vacancies_list_tag = main_soup.find('main', class_='vacancy-serp-content')
time.sleep(3)
vacancy_tags = vacancies_list_tag.find_all('div', 'vacancy-serp-item-body__main-info')

links = []
result = []
for vacancy_tag in vacancy_tags:
    #  Find link
    h3_tag = vacancy_tag.find('h3', class_='bloko-header-section-3')
    link = h3_tag.find('a')['href']
    # open a vacancy and use its html code
    response = requests.get(link, headers=gen_headers())
    vacancy_card = response.text
    vacancy_soup = BeautifulSoup(vacancy_card, 'lxml')
    time.sleep(1)
    content_tag = vacancy_soup.find('div', class_='g-user-content')
    pattern_1 = r'flask'
    pattern_2 = r'django'
    #  check if a vacancy contain keywords in description
    if re.findall(pattern=pattern_1, string=content_tag.text.lower()) or \
       re.findall(pattern=pattern_2, string=content_tag.text.lower()):
        #  Find the name company
        name_company = vacancy_tag.find('div', class_='vacancy-serp-item-company')
        name_unnorm = BeautifulSoup(str(name_company.find('a')), 'html.parser').text
        name = unicodedata.normalize('NFKC', name_unnorm)
        #  Find the city name
        city_tag = vacancy_soup.find('div', class_='vacancy-company-redesigned')
        if city_tag.find('p', {'data-qa': 'vacancy-view-location'}):
            city = city_tag.find('p', {'data-qa': 'vacancy-view-location'})
        else:
            city = city_tag.find('span', {'data-qa':'vacancy-view-raw-address'})
        #  Find salary
        vacancy_salary_tag = vacancy_soup.find('div', class_='bloko-columns-row')
        salary_tag = vacancy_salary_tag.find('span', {'data-qa': "vacancy-salary-compensation-type-net"})
        if salary_tag is not None:
            sal = (salary_tag.text.strip())
            salary = unicodedata.normalize('NFKC', sal)
        else:
            salary = None

        vacancy_dict = {
            'company_name': name,
            'link': link,
            'salary': salary,
            'city': city.text
        }
        result.append(vacancy_dict)


def create_json(info: list):
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    create_json(result)
