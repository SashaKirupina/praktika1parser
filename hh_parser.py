import requests
import logging
import random
import telebot
from database import insert_items_to_db, get_items_by_params

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_URL = 'https://api.hh.ru/vacancies'
AREAS_URL = 'https://api.hh.ru/areas'
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

def get_random_user_agent():
    return random.choice(user_agents)

def get_city_code(city_name):
    try:
        response = requests.get(AREAS_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса списка городов:{e}")
        return None

    areas = response.json()
    for country in areas:
        for area in country.get('areas', []):
            if area.get('name', '').lower() == city_name.lower():
                return area['id']
            for sub_area in area.get('areas', []):
                if sub_area.get('name', '').lower() == city_name.lower():
                    return sub_area['id']
    return None
def parse_items(vacancy, city_name, salary, per_page=75, page=0):
    city_code = get_city_code(city_name)
    if not city_code:
        logging.error(f"Не удалось найти код города для: {city_name}")
        return None

    headers = {
        'User-Agent': get_random_user_agent()
    }

    params = {
        'text': vacancy,
        'area': city_code,
        'salary': salary,
        'per_page': per_page,
        'page': page
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return None

    data = response.json()
    vacancies = []

    for item in data.get('items', []):
        name = item.get('name', 'No title')
        salary = item.get('salary', {})
        salary_from = salary.get('from', 0) if salary else 0
        salary_to = salary.get('to', 0) if salary else 0
        salary_currency = salary.get('currency', 'RUR') if salary else 'RUR'
        salary_info = f"{salary_from} - {salary_to} {salary_currency}" if salary_from and salary_to else 'No salary'
        link = item.get('alternate_url', 'No link')

        vacancies.append({
            'vacancy': name,
            'city': city_name,
            'salary': str(salary_from),
            'url': link
        })

    logging.info(f'Парсинг завершен. Найдено {len(vacancies)} вакансий.')
    return vacancies


API_TOKEN = '7284859519:AAHMog_269QoRzgPZNsR8vYJvzzPmFhDmvw'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет! Я бот для поиска вакансий на HeadHunters. Введите параметры поиска для загрузки вакансий в базу данных в формате: /search <вакансия> <зарплата> <город> ')

@bot.message_handler(commands=['search'])
def search_items(message):
    args = message.text.split()[1:]
    if len(args) != 3:
            bot.reply_to(message, 'Введите параметры в формате: /search <вакансия> <зарплата> <город>')
            return

    vacancy = args[0].strip()
    city = args[1].strip()
    salary = args[2].strip()

    try:
        vacancies = parse_items(vacancy, salary, city)
        if vacancies is None:
            bot.reply_to(message, 'Произошла ошибка при парсинге вакансий.')
            return
        insert_items_to_db(vacancies)
        if vacancies:
            bot.reply_to(message, f'Найдено и сохранено {len(vacancies)} вакансий по параметрам "{vacancy}, {salary}, {city}".')
        else:
            bot.reply_to(message, 'Вакансии по заданным параметрам не найдены.')
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка при поиске вакансий: {e}')

@bot.message_handler(commands=['get'])
def get_items(message):
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, 'Введите параметры в формате: /get <вакансия> <зарплата> <город> ')
        return

    vacancy = args[0].strip()
    city = args[1].strip()
    salary = args[2].strip()

    try:
        vacancies = get_items_by_params(vacancy, city, salary)
        if vacancies:
            for vacancy in vacancies:
                bot.reply_to(message, f"Вакансия: {vacancy[0]}\nЗарплата: {vacancy[1]}\nГород: {vacancy[2]}\nСсылка: {vacancy[3]}\n\n")
        else:
            bot.reply_to(message, 'Вакансии по заданным параметрам не найдены.')
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка при получении вакансий: {e}')

if __name__ == '__main__':
    bot.polling(none_stop=True)

