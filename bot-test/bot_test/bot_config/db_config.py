import psycopg2
from psycopg2 import OperationalError
from decouple import config

def get_db_connection():
    try:
        dbname = config('DB_NAME')
        user = config('DB_USER')
        password = config('DB_PASSWORD')
        host = config('DB_HOST')
        port = config('DB_PORT', cast=int)

        # Nawiąż połączenie z bazą danych
        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise


def get_db_connection2():
    try:
        dbname = "boty-db-secondary"
        user = config('DB_USER')
        password = config('DB_PASSWORD')
        host = config('DB_HOST')
        port = 5434

        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise