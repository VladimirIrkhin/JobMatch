import telebot
import vacancies_search
import vacancies_stats
from io import BytesIO
from telebot import types
from pprint import pprint

bot = telebot.TeleBot('7416479006:AAG7Ks02qawFYpKXfeukicmYS8VXzLRG60M')
users_id = {}


def add_helper_to_message(text):
    text += ('\n\nЧтобы получить инфомацию о нашей системе, отправьте /send_info!\nЧтобы увидеть список команд,'
             ' отправьте /send_commands!')

    return text


@bot.message_handler(commands=['send_general_stat'])
def send_general_stat(message):
    #try:
    period = int(message.text.replace('/send_general_stat', '').strip())
    bot.send_message(message.chat.id, 'Анализирую... Это может занять какое то время...')
    data = vacancies_stats.get_vacancies_from_hh_ru(period)
    b_string, specialities = vacancies_stats.get_stats_from_all(data)
    # users_id[message.chat.id] = specialities
    # users_id[message.chat.id].append(period)

    img = BytesIO(b_string)
    bot.send_photo(message.chat.id, img)

    bot.send_message(message.chat.id, add_helper_to_message('Востребованность специальностей на рынке по количеству'
                                                            ' вакансий, выложенных за указанный период.\n\n Чтобы '
                                                            'посмотреть статистику по выбранной специальности, '
                                                            'введите ее название в точности как на диаграмме'))
    #except Exception as e:
    #    bot.send_message(message.chat.id, add_helper_to_message('Возникла ошибка, приносим свои ивинения'))
    #    print(e)


@bot.message_handler(content_types=['text'])
def send_speciality_stat(message):
    if message.text in users_id[message.chat.id]:
        bot.send_message(message.chat.id, 'Анализирую... Это может занять какое то время...')
        period = users_id[message.chat.id][-1]
        data = vacancies_stats.get_vacancies_from_hh_ru(period)
        stats = vacancies_stats.get_stats_about_speciality(data, message.text)

        salary = stats['salary']
        img = BytesIO(salary)
        bot.send_photo(message.chat.id, img)

        schedule = stats['schedule']
        img = BytesIO(schedule)
        bot.send_photo(message.chat.id, img)

        experience = stats['experience']
        img = BytesIO(experience)
        bot.send_photo(message.chat.id, img)

        regions = stats['regions']
        img = BytesIO(regions)
        bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['send_vacancies'])
def send_vacancies(message):
    try:
        params = {i.split('-')[0]: i.split('-')[1] for i in
                  message.text.replace('/send_vacancies', '').strip().split(' ')}

        vacancies = vacancies_search.get_vacancies(params['название'],
                                                   experience=(params['стаж'] if 'стаж' in params.keys() else None),
                                                   salary=(params['зарплата'] if 'зарплата' in params.keys() else None))
        text = '\n\n'.join([
            f'{i["name"]}\nОпыт работы: {i["experience"]}\nРегион: {i["region"]}\nТип занятости: '
            f'{i["schedule"]}\nЗарплата от: '
            f'{i["salary"]["from"] if "from" in i["salary"].keys() else "не указано"}\nЗарпата до: '
            f'{i["salary"]["to"] if "to" in i["salary"].keys() else "не указано"}'
            f'\nСсылка: {i["link"]}'
            for i in vacancies])
    except Exception as e:
        text = 'Возникла ошибка, приносим свои извинения.'
        print(e)
    finally:
        bot.send_message(message.chat.id, add_helper_to_message(text))


@bot.message_handler(commands=['send_commands'])
def send_commands(message):
    possible_commands = {
        '/send_vacancies': 'Отправит наиболее походящие вакансии по запросу. Формат сообщения: <сама команда> '
                           'название-<специальность(единственный обязательный параметр)> стаж-<ваш опыт работы в сфере> '
                           'зарплата-<желаемое чисо зарплаты в рублях>. Допустимые значения для стажа: noExperience, '
                           'between1And3, between3And6, moreThan6. Очен важно строгое соблюдение формата запроса!'
    }


@bot.message_handler(commands=['send_info'])
def send_info(message):
    text = '''Наша система представляет собой агрегатор, собирающий объявления о вакансиях с различных специализированных сайтов, таких как hh.ru, avito работа, trudvsem.ru, анализирующий актуальную ситуацию на рынке труда и предоставляющий централизованный доступ к ним.\nЕго основная функция - это предоставлять актуальную статистику. Анализ состоит из двух основных аспектов: первый - анализ востребованнсти различных специальностей на рынке, опирающийся на количетство вакансий, выложенных за какой-то промежуток времени, второй - это предоставление различной статистической информации о конкретной специальности, такой как встречаемость определенного графика работ, встречаемость определенного стажа, необходиого для трудоустройства, зарплаты и т.д. Пока что анализ вакансий производится только с сайта hh.ru, но в будущем планируется добавление и других источников, как и добавление новых метрик оценки.\nТакже наша система собирает вакансии с различных сайтов, выбирает наиболее интересные и выдает краткую информацию о них, чтобы у пользователя был централизованный способ поиска работы.\nВ будущем мы планируем расширять и дорабатывать эту систему, чтобы сделать наш сервис более удобным, популярным, быстрым и функциональным'''

    bot.send_message(message.chat.id, add_helper_to_message(text))


@bot.message_handler(commands=['start'])
def start(message):
    global users_id

    if message.chat.id in users_id:
        text = 'Вы уже зарегистрированы в системе!'
    else:
        users_id[message.chat.id] = None
        text = 'Вы успешно зарегистрированы в системе!'

    bot.send_message(message.chat.id, add_helper_to_message(text))


bot.polling(non_stop=True)
