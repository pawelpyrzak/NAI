import requests
from datetime import datetime
from decouple import config
JIRA_USER = "inzynierkabot@int.pl"
JIRA_TOKEN = config("JIRA_API_KEY2")
JIRA_INSTANCE = "int-team-hvyepex0.atlassian.net"
JIRA_URL = f"https://{JIRA_INSTANCE}/rest/api/2/search"

def fetch_jira_tasks():
    try:
        # Nagłówki i uwierzytelnienie
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Zapytanie JQL do JIRA
        jql = "status != Done ORDER BY updated DESC"  # Filtr: zadania nieukończone, sortowane według daty aktualizacji
        params = {
            "jql": jql,
        }

        # Wysyłanie żądania do API JIRA
        response = requests.get(JIRA_URL, headers=headers, params=params, auth=(JIRA_USER, JIRA_TOKEN))
        response.raise_for_status()  # Rzuć wyjątek, jeśli wystąpi błąd

        # Przetwarzanie wyników
        issues = response.json().get("issues", [])
        if not issues:
            print("Brak zadań do wyświetlenia.")
            return

        # Wyświetlenie zadań
        print(f"{'ID':<10} {'Title':<30} {'Start Date':<12} {'Due Date':<12} {'Priority':<10} {'Status':<15} {'Assignee':<20} {'Updated At':<20}")
        print("-" * 130)
        for issue in issues:
            fields = issue["fields"]
            print(f"{issue['id']:<10} {fields['summary']:<30} "
                  f"{fields.get('startdate', 'N/A'):<12} {fields.get('duedate', 'N/A'):<12} "
                  f"{fields['priority']['name'] if fields['priority'] else 'N/A':<10} "
                  f"{fields['status']['name']:<15} "
                  f"{fields['assignee']['displayName'] if fields['assignee'] else 'Unassigned':<20} "
                  f"{fields['updated']:<20}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {str(e)}")

# Główna funkcja
if __name__ == "__main__":
    fetch_jira_tasks()
