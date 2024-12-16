import os
import re
import requests
import sys
import uuid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot_test.bot_config.db_config import get_db_connection

def save_chat_to_db(channel_id, channel_name):

    db = get_db_connection()
    c = db.cursor()

    # Sprawdzenie, czy czat już istnieje
    c.execute("SELECT uuid FROM chat WHERE chat_main_id = %s", (channel_id,))
    row = c.fetchone()

    if row:
        token = row[0]
        print(f"Czat już istnieje, uuid: {token}")
        message=f"Czat już istnieje, uuid: {token}"
    else:
        # Tworzenie nowego czatu
        token = str(uuid.uuid4())
        c.execute("INSERT INTO chat (uuid, chat_main_id, name, chat_platform_id) VALUES (%s, %s, %s, %s)",
                  (token, channel_id, channel_name, 1))

        db.commit()
        print(f"Nowy czat utworzony, UUID: {token}")
        message=f"Nowy czat utworzony, UUID: {token}"

    db.close()
    return message

def save_file_to_db(file_name, file_content, channel_id):
    try:
        db = get_db_connection()  # Get the connection to the database
        c = db.cursor()

        # Start a transaction for large object operations
        db.autocommit = False  # Disable autocommit to manage transaction manually

        # Create a new large object
        lo = db.lobject(0, 'w')  # Use the connection object to create a large object

        lo.write(file_content)  # Write the content to the large object
        lo.close()  # Close the large object to finalize it

        c.execute("SELECT id FROM chat WHERE chat_main_id = %s", (channel_id,))
        row = c.fetchone()

        if row:
            chat_id = row[0]
            c.execute("INSERT INTO File (name, data, Chat_id) VALUES (%s, %s, %s)",
                      (file_name, lo.oid, chat_id))
            db.commit()

        db.close()
        print(f"Plik {file_name} został zapisany w bazie.")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        print(f"Błąd zapisu pliku do bazy danych: {e}")
