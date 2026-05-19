import psycopg2


def connect_db():
    return psycopg2.connect(
        dbname="furniture_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )