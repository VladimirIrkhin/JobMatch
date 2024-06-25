import requests
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import io
from vacancies_search import convert_into_RUB


def get_vacancies_from_hh_ru(period):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'order_by': 'relevance',
        'period': period,

        'per_page': 25
    }

    data = []
    page = 0
    while True:
        params['page'] = page
        response = requests.get(url, params=params).json()
        results = response['items']

        for i in results:
            vacancy = {
                'speciality': i['professional_roles'][0]['name'],
                'experience': (i['experience']['name'] if 'experience' in i.keys() else None),
                'salary': ({'from': i['salary']['from'], 'to': i['salary']['to'],
                            'currency': i['salary']['currency']} if 'salary' in i.keys() and i[
                    'salary'] is not None else None),
                'region': (i['area']['name'] if 'area' in i.keys() else None),
                'schedule': (i['schedule']['name'] if 'schedule' in i.keys() and
                                                      i['schedule'] is not None else None),
            }

            data.append(vacancy)

        page += 1
        if page == response['pages'] - 1:
            break

    return data


def get_stats_from_all(all_data):
    all_data = prepare_data_for_pie(all_data, 'speciality', 2)

    se = pd.Series(
        {i['speciality']: len([j for j in all_data if j['speciality'] == i['speciality']]) for i in all_data})
    plt.pie(se, labels=se.index)

    plt.show(block=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight')
    buf.seek(0)
    b_str_img = buf.getvalue()
    plt.close()
    buf.close()

    return b_str_img, [i for i in se.index if i != 'Другое']


def get_stats_about_speciality(all_data, speciality):
    filtered_data = [i for i in all_data if i['speciality'] == speciality]

    salaries = [convert_into_RUB(i['salary']) for i in filtered_data if
                i['salary'] is not None and convert_into_RUB(i['salary']) != 0]
    plt.hist(salaries, bins=30, alpha=0.5, color='blue', edgecolor='black')
    plt.xlabel('Зарплаты работников')
    plt.ylabel('Частота встречаемости')
    plt.title('График распределения зарплат')
    plt.show(block=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight')
    b_str_img_salary = buf.getvalue()
    buf.close()
    plt.close()

    schedule_occurrence = pd.Series(
        {i['schedule']: len([1 for j in all_data if j['schedule'] == i['schedule']]) for i in
         all_data})
    plt.bar(schedule_occurrence.index, schedule_occurrence.values, align='center', tick_label=schedule_occurrence.index)
    plt.xticks(rotation=10)
    plt.title('Столбчатая диаграмма графика работы')
    plt.xlabel('График работы')
    plt.ylabel('Встречаемость')
    plt.show(block=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight')
    b_str_img_schedule = buf.getvalue()
    buf.close()
    plt.close()

    experience_occurrence = pd.Series(
        {i['experience']: len([1 for j in all_data if j['experience'] == i['experience']]) for i in
         all_data})
    plt.bar(experience_occurrence.index, experience_occurrence.values, align='center',
            tick_label=experience_occurrence.index)
    plt.title('Столбчатая диаграмма необходимого для трудустройства стажа')
    plt.xlabel('Требуемый стаж')
    plt.ylabel('Встречаемость')
    plt.show(block=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight')
    b_str_img_experience = buf.getvalue()
    buf.close()
    plt.close()

    prepared_data = prepare_data_for_pie(all_data, 'region', 1.5)
    regions_occurence = pd.Series({i['region']: len([1 for j in prepared_data if j['region'] == i['region']]) for i in
                                   prepared_data})
    plt.pie(regions_occurence, labels=regions_occurence.index)
    plt.show(block=True)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight')
    b_str_img_regions = buf.getvalue()
    buf.close()
    plt.close()

    return {'salary': b_str_img_salary, 'schedule': b_str_img_schedule, 'experience': b_str_img_experience,
            'regions': b_str_img_regions}


def prepare_data_for_pie(data, field, procent):
    occurrences_procent = {i: len([j for j in data if j[field] == i]) / len(data) * 100 for i in
                           set([k[field] for k in data])}
    prepared_data = []
    for i in data:
        if occurrences_procent[i[field]] < procent:
            i[field] = 'Другое'
        prepared_data.append(i)

    return prepared_data


if __name__ == '__main__':
    data = get_vacancies_from_hh_ru(1)  # указывается количетво последних дней, за которые собирается статистика
    get_stats_from_all(
        data)  # имеется возможность корректировать процент присутствия маловстречаемых значений на круговой диаграмме
    get_stats_about_speciality(data, 'Водитель')  # водитель для примера
