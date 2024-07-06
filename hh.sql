CREATE TABLE vacancies (
    id SERIAL PRIMARY KEY,
    vacancy VARCHAR,
    salary VARCHAR,
    city VARCHAR,
    url TEXT
)


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