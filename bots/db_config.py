import mysql.connector


def get_db_connection():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="discord_bot"
    )
    return db
