import requests
from bot_test.bot_config.jiraConfig import *
base_url =  JIRA_URL+"search"

def get_jira_tasks(JQL_QUERY: str) -> str:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {"jql": JQL_QUERY}

    try:
        response = requests.get(base_url, headers=headers, params=params, auth=(JIRA_USER, JIRA_TOKEN))

        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])
            if not issues:
                return "Brak zadań do wykonania na dziś."

            tasks = []
            for issue in issues:
                key = issue.get("key", "Brak klucza")
                summary = issue["fields"].get("summary", "Brak opisu")
                assignee = issue["fields"].get("assignee", {}).get("displayName", "Nieprzypisany")
                duedate = issue["fields"].get("duedate", "Brak daty")
                tasks.append(f"- [{key}] {summary} (Przypisane do: {assignee}, Data: {duedate})")

            return "\n".join(tasks)

        else:
            return f"Błąd: {response.status_code}, {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Błąd podczas komunikacji z Jira: {e}"
