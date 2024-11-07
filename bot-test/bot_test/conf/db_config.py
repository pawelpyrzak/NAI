import psycopg2
from psycopg2 import OperationalError

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="boty-db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5433"
        )
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise
