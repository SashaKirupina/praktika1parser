import psycopg2
from psycopg2 import sql, Error

def insert_items_to_db(vacancies):
    try:
        connection = psycopg2.connect(
            database="hh_vacancies",
            user="postgres",
            password="22611971",
            host="db",
            port="5432"
        )
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            vacancy VARCHAR,
            salary VARCHAR,
            city VARCHAR,
            url TEXT
        )
        """)
        connection.commit()

        for vacancy in vacancies:
            try:
                cursor.execute("""
                    INSERT INTO vacancies (vacancy, salary, city, url)
                    VALUES (%s, %s, %s, %s)
                """, (vacancy['vacancy'], vacancy['salary'], vacancy['city'], vacancy['url']))
            except (Exception, Error) as error:
                print(f"Ошибка при вставке данных: {error}")

        connection.commit()
    except (Exception, Error) as error:(
        print(f"Ошибка при подключении к базе данных:{error}"))

def get_items_by_params(vacancy, salary, city):
    vacancies = []
    try:
        connection = psycopg2.connect(
            database="hh_vacancies",
            user="postgres",
            password="22611971",
            host="db",
            port="5432"
        )
        cursor = connection.cursor()
        query = sql.SQL("""
            SELECT vacancy, salary, city, url FROM vacancies
            WHERE city = %s AND salary ILIKE %s AND vacancy ILIKE %s
        """)
        cursor.execute(query, (city, salary, vacancy))
        vacancies = cursor.fetchall()
    except (Exception, Error) as error:
        print(f"Ошибка при выполнении запроса: {error}")
    return vacancies

