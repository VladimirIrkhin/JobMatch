import requests
from pprint import pprint
import re

ExchangeRate_API_key = 'c255b7dc81bbc4cf712a2c15'


def get_vacancies(specialty, experience=None, salary=None):
    # подгон данных для запроса в апи, написать словари для конвертации отдельно для каждой функции внутри этой
    # функции!!! изначально в эту функции подаются знаения в текстовом чеовекоитаемом ормате, как на сайте
    hh_ru_data = get_from_hh_ru(specialty, experience, salary)
    trudvsem_data = get_from_trudvsem(specialty, experience, salary)
    all_data = list(hh_ru_data + trudvsem_data)
    result_data = list(sorted(all_data, key=lambda vacancy: convert_into_RUB(vacancy['salary']), reverse=True))[:15]

    return result_data


def get_from_hh_ru(specialty, experience=None, salary=None):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'search_field': 'name',
        'text': specialty,
        'salary': salary,
        'experience': experience,
        'order_by': 'relevance',

        'page': 1,
        'per_page': 15
    }
    response = requests.get(url, params=params).json()
    data = response['items']

    results = []
    for i in data:
        vacancy = {
            'link': i['alternate_url'],
            'name': i['name'],
            'experience': (i['experience']['name'] if 'experience' in i.keys() else None),
            'salary': ({'from': i['salary']['from'], 'to': i['salary']['to'],
                        'currency': i['salary']['currency']} if 'salary' in i.keys() and i[
                'salary'] is not None else None),
            'region': (i['area']['name'] if 'area' in i.keys() else None),
            'schedule': (i['schedule']['name'] if 'schedule' in i.keys() and
                                                  i['schedule'] is not None else None),
            'description': ({'requirement': (
                re.sub('<.*?>', '', i['snippet']['requirement']) if 'requirement' in i['snippet'].keys() and
                                                                    i['snippet']['requirement'] is not None else None),
                                'responsibility': (re.sub('<.*?>', '', i['snippet'][
                                    'responsibility']) if 'responsibility' in i['snippet'].keys() and i['snippet'][
                                    'responsibility'] is not None else None),
                                'duty': None} if 'snippet' in i.keys() else {'requirement': None,
                                                                             'responsibility': None, 'duty': None})
        }

        results.append(vacancy)

    return results


def get_from_trudvsem(specialty, experience=None, salary=None):
    url = 'http://opendata.trudvsem.ru/api/v1/vacancies'
    params = {
        'text': specialty,
        'base_salary_min': salary,
        'experience': experience,

        'limit': 15
    }

    response = requests.get(url, params=params).json()
    data = response['results']['vacancies']

    results = []
    for i in data:
        i = i['vacancy']
        vacancy = {
            'link': i['vac_url'],
            'name': i['job-name'],
            'experience': f'Требуется лет стажа: {i["requirement"]["experience"]}',
            'salary': {'from': (i['salary_min'] if 'salary_min' in i.keys() and i['salary_min'] != 0 else None),
                       'to': (i['salary_max'] if 'salary_max' in i.keys() and i['salary_max'] != 0 else None),
                       'currency': 'RUR'},
            'region': (i['region']['name'] if 'region' in i.keys() else None),
            'schedule': (i['schedule'] if 'schedule' in i.keys() else None),
            'description': {'requirement': (
                re.sub('<.*?>', '', i['requirement']['qualification']) if 'qualification' in i[
                    'requirement'].keys() else None),
                'responsibility': None, 'duty': re.sub('<.*?>', '', i['duty']) if 'duty' in i.keys() else None},
        }

        results.append(vacancy)

    return results


def convert_into_RUB(salary):
    if salary is None:
        result = 0
    elif salary['currency'] != 'RUR':
        url = f'https://api.exchangerate-api.com/v4/latest/{salary["currency"]}?access_key={ExchangeRate_API_key}'
        response = requests.get(url)
        if str(response.status_code).startswith('2'):
            result = int(
                response.json()['rates']['RUB'] * (salary['from'] if salary['from'] is not None else salary['to']))
        else:
            result = 0
    else:
        result = (salary['from'] if salary['from'] is not None else salary['to'])

    return result


if __name__ == '__main__':
    pprint(get_vacancies('Аналитик'))
