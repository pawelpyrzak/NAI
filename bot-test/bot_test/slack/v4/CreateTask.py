import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from bot_test.bot_config.jiraConfig import *
import re

def create_jira_task(base_url, username, token, project_key, title, description,
                     start_date=None, due_date=None, priority=None, assignee=None):
    url = f"{base_url}issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    auth = HTTPBasicAuth(username, token)

    # Budowanie pola payload
    fields = {
        "project": {"key": project_key},
        "summary": title,
        "description": description,
        "issuetype": {"name": "Task"},  # Domyślny typ zadania
    }

    # Dodanie opcjonalnych pól
    if start_date:
        fields["customfield_10015"] = start_date
    else:
        fields["customfield_10015"] = datetime.now()
    if due_date:
        fields["duedate"] = due_date
    else:
        fields["duedate"] = datetime.now()
    if priority:
        fields["priority"] = {"name": priority}
    if assignee:
        fields["assignee"] = {"displayName": assignee}

    payload = {"fields": fields}
    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code == 201:
        print(f"Zadanie '{title}' zostało pomyślnie utworzone!")
        print(f"Szczegóły zadania: {response.json().get('self')}")
    else:
        print("Wystąpił błąd podczas tworzenia zadania.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")


def checkPattern(command, say):
    pattern = (
        r'^Utwórz zadanie: title:(?P<title>.*?), description:(?P<description>.*?),?'
        r'( start_date:(?P<start_date>.*?),?)?'
        r'( due_date:(?P<due_date>.*?),?)?'
        r'( priority:(?P<priority>.*?),?)?$'
    )
    match = re.match(pattern, command)
    if match:
        parsed= match.groupdict()
    else:
        print("Niepoprawny format komendy. Użyj formatu:")
        print(
            "Utwórz zadanie: title:tytuł, description:opis, start_date:data_startu, due_date:data_końca, priority:priorytet")
        parsed = None

    if parsed:
        create_jira_task(
            base_url=JIRA_URL,
            username=JIRA_USER,
            token=JIRA_TOKEN,
            project_key=project_key,
            title=parsed['title'],
            description=parsed['description'],
            start_date=parsed.get('start_date'),
            due_date=parsed.get('due_date'),
            priority=parsed.get('priority'),
            assignee=parsed.get('assignee')
        )