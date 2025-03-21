import requests

from ..models import JiraConfig, TaskIntegration, ProjectExternalKey, ProjectPlatform


def create_jira_issue(task,user_platform_account):
    jira_config = JiraConfig.objects.get(group=task.project.group)
    jira_url = jira_config.jira_url
    auth = (jira_config.jira_email, jira_config.jira_api_key)
    headers = {"Content-Type": "application/json"}
    jira_account_id = user_platform_account.platform_user_id if user_platform_account else None
    jira_platform = ProjectPlatform.objects.filter(name="Jira").first()
    project_external_key = ProjectExternalKey.objects.filter(project=task.project, platform=jira_platform).first()

    issue_data = {
        "fields": {
            "project": {"key": project_external_key.key},
            "summary": task.title,
            "description": task.description,
            "issuetype": {"name": "Task"},
            "priority": {"name": task.priority.capitalize()},
            "assignee": {"accountId": jira_account_id} if jira_account_id else None,
            "duedate": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
            "customfield_10015": task.start_date.strftime('%Y-%m-%d') if task.start_date else None
        }
    }

    response = requests.post(f"{jira_url}/rest/api/2/issue", json=issue_data, auth=auth, headers=headers)

    if response.status_code == 201:
        issue = response.json()
        return issue['key'], jira_account_id
    return None, None

def update_jira_issue(task, updated_fields):
    jira_config = JiraConfig.objects.get(group=task.project.group)
    jira_url = jira_config.jira_url
    auth = (jira_config.jira_email, jira_config.jira_api_key)
    jira_task = TaskIntegration.object.get_object_or_404(task=task)
    url = f"{jira_url}/rest/api/3/issue/{jira_task.key}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {"fields": updated_fields}

    response = requests.put(url, json=payload, headers=headers, auth=auth)

    if response.status_code == 204:
        print(f"✅ Zaktualizowano zadanie {jira_task.key} w Jira!")
    else:
        print(f"❌ Błąd aktualizacji Jira: {response.status_code} {response.text}")
    return response

