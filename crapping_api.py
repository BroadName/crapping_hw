import requests
from pprint import pprint
from bs4 import BeautifulSoup
from fake_headers import Headers
import time
import re
import json


def gen_headers() -> dict:
    headers = Headers(browser='chrome', os='win')
    return headers.generate()


def contain_links() -> list:
    response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=gen_headers())
    main_html = response.text
    main_soup = BeautifulSoup(main_html, 'lxml')
    time.sleep(5)
    vacancies_list_tag = main_soup.find('div', {'data-qa': 'vacancy-serp__results'})
    vacancy_tags = vacancies_list_tag.find_all('div', 'vacancy-serp-item-body__main-info')
    links = []
    for vacancy_tag in vacancy_tags:
        #  Find link
        h3_tag = vacancy_tag.find('h3', class_='bloko-header-section-3')
        link = h3_tag.find('a')['href']
        if re.findall(r'//adsrv', link):
            resp = requests.get(link)
            final_url = resp.url
            links.append(final_url)
        else:
            links.append(link)
    print('List of links complected')
    return links


def pull_up_main_info(links: list) -> list:
    result_list = []
    count = 1
    for link in links:
        url_id = re.findall(r'vacancy/(\d+)', link)
        api_url = f'https://api.hh.ru/vacancies/{url_id[0]}'
        response = requests.get(api_url, headers=gen_headers())
        response_json = response.json()
        desc = response_json.get('description')
        pattern_1 = r'flask'
        pattern_2 = r'django'

        if re.findall(pattern=pattern_1, string=desc.lower()) and re.findall(pattern=pattern_2, string=desc.lower()):
            name_company = response_json.get('employer').get('name')
            if response_json.get('salary') is None:
                salary = None
            else:
                if response_json.get('salary').get('from') is None and \
                        response_json.get('salary').get('to') and \
                        response_json.get('salary').get('currency') == 'RUR':

                    salary = f'до {response_json.get("salary").get("to")} RUB'

                elif response_json.get('salary').get('from') and \
                        response_json.get('salary').get('to') is None and \
                        response_json.get('salary').get('currency') == 'RUR':
                    salary = f'от {response_json.get("salary").get("from")} RUB'

                elif response_json.get('salary').get('from') and \
                        response_json.get('salary').get('to') and \
                        response_json.get('salary').get('currency') == 'RUR':

                    salary = f'от {response_json.get("salary").get("from")}' \
                             f' до {response_json.get("salary").get("to")} RUB'

                elif response_json.get('salary').get('from') is None and \
                        response_json.get('salary').get('to') and \
                        response_json.get('salary').get('currency') == 'USD':

                    salary = f'до {response_json.get("salary").get("to")} $'

                elif response_json.get('salary').get('from') and \
                        response_json.get('salary').get('to') and \
                        response_json.get('salary').get('currency') == 'USD':

                    salary = f'от {response_json.get("salary").get("from")}' \
                             f' до {response_json.get("salary").get("to")} $'

                else:
                    salary = f'от {response_json.get("salary").get("from")} $'

            city = response_json.get('area').get('name')
            main_info = {
                'link': link,
                'name_company': name_company,
                'salary': salary,
                'city': city
            }
            result_list.append(main_info)
            print(f'{count} block of information about company is completed')
            count += 1
        else:
            continue

    return result_list


def create_json(info: list):
    with open('result_api.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    create_json(pull_up_main_info(contain_links()))
