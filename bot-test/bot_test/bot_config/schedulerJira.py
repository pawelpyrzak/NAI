from decouple import config
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from bot_test.bot_config.db_config import get_db_connection2

JIRA_USER = "inzynierkabot@int.pl"
JIRA_TOKEN = config("JIRA_API_KEY2")
JIRA_INSTANCE = "int-team-hvyepex0.atlassian.net"
JIRA_URL = f"https://{JIRA_INSTANCE}/rest/api/2/search"

conn = get_db_connection2()
cursor = conn.cursor()


# Pobieranie ostatniego czasu synchronizacji
def get_last_sync(jira_instance):
    cursor.execute("""
        SELECT value FROM sync_metadata
        WHERE jira_instance = %s AND key = 'last_sync'
    """, (jira_instance,))
    result = cursor.fetchone()
    return result[0] if result else None


def update_last_sync(jira_instance):
    # Pobranie najpóźniejszej daty z tabeli tasks
    cursor.execute("SELECT MAX(updated_at) FROM tasks")
    max_updated_at = cursor.fetchone()[0]

    # Jeśli brak zadań, użyj aktualnej daty
    if max_updated_at is None:
        max_updated_at = datetime.now()

    # Aktualizacja tabeli sync_metadata
    cursor.execute("""
        INSERT INTO sync_metadata (jira_instance, key, value)
        VALUES (%s, 'last_sync', %s)
        ON CONFLICT (jira_instance, key)
        DO UPDATE SET value = EXCLUDED.value
    """, (jira_instance, max_updated_at))
    conn.commit()


def fetch_jira_tasks(last_sync):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    jql = 'status != Done'
    if last_sync:
        formatted_date = last_sync.strftime('%Y-%m-%d %H:%M')
        jql += f' AND updated > "{formatted_date}"'
    params = {
        'jql': jql,
    }
    response = requests.get(JIRA_URL, headers=headers, params=params, auth=(JIRA_USER, JIRA_TOKEN))
    if response.status_code != 200:
        print(f"Error fetching tasks: {response.status_code}, {response.text}")
        return []
    return response.json().get('issues', [])

def sync_tasks():
    print("Starting JIRA synchronization...")
    last_sync = get_last_sync(JIRA_INSTANCE)
    tasks = fetch_jira_tasks(last_sync)


    changes_made = False
    print(len(tasks))
    for task in tasks:
        task_id = int(task['id'])
        fields = task['fields']
        title = fields.get('summary')
        description = fields.get('description')
        status = fields.get('status', {}).get('name')
        start_date = fields.get('customfield_10015')
        due_date = fields.get('duedate')
        assignee = fields.get('assignee')
        assignee_name = assignee.get('displayName') if assignee else None
        priority = fields.get('priority', {}).get('name')
        updated_at = datetime.strptime(fields['updated'], "%Y-%m-%dT%H:%M:%S.%f%z")
        updated_at = updated_at.replace(tzinfo=None)

        start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else updated_at.date()
        due_date = datetime.strptime(due_date, "%Y-%m-%d") if due_date else updated_at.date()

        cursor.execute('SELECT updated_at FROM tasks WHERE id = %s', (task_id,))
        existing_task = cursor.fetchone()
        if existing_task:
            existing_updated_at = existing_task[0]
            if updated_at > existing_updated_at:
                cursor.execute('''
                    UPDATE tasks 
                    SET title = %s, description = %s, status = %s, start_date = %s, 
                        due_date = %s, assignee = %s, priority = %s, updated_at = %s
                    WHERE id = %s
                ''', (title, description, status, start_date, due_date, assignee_name, priority, updated_at, task_id))
                changes_made=True
        else:
            cursor.execute('''
                INSERT INTO tasks (id, title, description, status, start_date, 
                                   due_date, assignee, priority, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (task_id, title, description, status, start_date, due_date, assignee_name, priority, updated_at))
            changes_made = True

    # Zapis zmian w bazie
    if changes_made:
        conn.commit()
        # Zaktualizuj czas ostatniej synchronizacji
        update_last_sync(JIRA_INSTANCE)
        print("Changes detected. Last sync updated.")
    else:
        print("No changes detected. Last sync not updated.")


# Ustawienia schedulera
scheduler = BlockingScheduler()
scheduler.add_job(sync_tasks, 'interval', minutes=5)
sync_tasks()
# Konfiguracja bazy i uruchomienie schedulera
print("Scheduler started. Synchronizing every 5 minutes...")
scheduler.start()
