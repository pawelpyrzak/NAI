from datetime import datetime

import requests
from django.db import transaction
from django.utils import timezone
from jira import JIRA

from ..models import Task, JiraConfig, UserPlatformAccount, Change, ProjectExternalKey, ProjectPlatform, TaskIntegration


def get_user_by_jira_user_id(jira_user_id):
    user_platform_account = UserPlatformAccount.objects.filter(platform_user_id=jira_user_id).first()
    return user_platform_account.user if user_platform_account else None


def get_jira_tasks_for_project(jira, project_ext):
    """Pobiera zadania z Jiry dla danego projektu."""
    issues = jira.search_issues(f'project = "{project_ext.key}"')
    tasks = []

    for issue in issues:
        fields = issue.fields
        start_date = fields.customfield_10015
        due_date = fields.duedate
        assignee_id = fields.assignee.accountId if fields.assignee else None
        updated_at = datetime.strptime(fields.updated, "%Y-%m-%dT%H:%M:%S.%f%z")
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else updated_at.date()
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else updated_at.date()
        creator_id = fields.creator.accountId if fields.creator else None
        assignee = get_user_by_jira_user_id(assignee_id) or get_user_by_jira_user_id(creator_id)

        task = {
            'title': fields.summary,
            'description': fields.description,
            'jira_key': issue.key,
            'status': fields.status.name,
            'priority': fields.priority.name.lower() if fields.priority else 'medium',
            'due_date': due_date,
            'start_date': start_date,
            'jira_user_id': assignee_id,
            'assignee': assignee,
            'created_by': get_user_by_jira_user_id(creator_id),
            'task_manager': get_user_by_jira_user_id(creator_id),
            'updated_at': updated_at,
            'created_at': datetime.strptime(fields.created, "%Y-%m-%dT%H:%M:%S.%f%z"),
        }
        tasks.append(task)

    return tasks


def update_or_create_tasks_from_jira():
    jira_platform = ProjectPlatform.objects.get(name="Jira")
    project_keys = ProjectExternalKey.objects.filter(platform=jira_platform).select_related("project")

    with transaction.atomic():
        for project_ext in project_keys:
            try:
                jira_config = JiraConfig.objects.get(group=project_ext.project.group)
                jira = JIRA(server=jira_config.jira_url, basic_auth=(jira_config.jira_email, jira_config.jira_api_key))
                create_tasks(jira, project_ext)
                update_tasks(jira_config, project_ext.project)
            except JiraConfig.DoesNotExist:
                print(f'Brak konfiguracji Jiry dla projektu {project_ext.project.name}')


def update_tasks(jira_config, project):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    task_integrations = TaskIntegration.objects.filter(
        task__project=project, external_id__isnull=False
    )
    for task_integration in task_integrations:
        jira_key = task_integration.external_id
        url = f"{jira_config.jira_url}/rest/api/2/issue/{jira_key}/changelog"
        response = requests.get(url, headers=headers, auth=(jira_config.jira_email, jira_config.jira_api_key))

        if response.status_code == 200:
            values = response.json().get("values", [])

            for value in values:
                author = value['author']['accountId']

                for item in value.get('items', []):
                    change = Change.objects.filter(
                        task=task_integration.task,
                        project=project,
                        field=item['field'],
                        from_value=item['fromString'],
                        to_value=item['toString'],
                        author=get_user_by_jira_user_id(author)
                    ).first()

                    if not change:
                        Change.objects.create(
                            task=task_integration.task,
                            project=project,
                            field=item['field'],
                            from_value=item.get('fromString', ''),
                            to_value=item['toString'],
                            author=get_user_by_jira_user_id(author),
                            date_changed=datetime.strptime(value['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
                        )
def create_tasks(jira, project_ext):
    tasks_from_jira = get_jira_tasks_for_project(jira, project_ext)

    for task_data in tasks_from_jira:
        # Sprawdzamy, czy Task już istnieje
        task = Task.objects.filter(
            project=project_ext.project,
            title=task_data['title'],
            due_date=task_data['due_date']
        ).first()

        if not task:
            # Jeśli Task nie istnieje, tworzymy nowe zadanie
            task = Task.objects.create(
                project=project_ext.project,
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                start_date=task_data['start_date'],
                due_date=task_data['due_date'],
                assignee=task_data['assignee'],
                priority=task_data['priority'],
                updated_at=task_data['updated_at'],
                created_at=task_data['created_at'],
                created_by=task_data['created_by'],
                task_manager=task_data['task_manager']
            )

        # Sprawdzamy, czy istnieje już integracja z Jira
        task_integration = TaskIntegration.objects.filter(
            task=task,
            external_id=task_data['jira_key']
        ).first()

        if not task_integration:
            # Jeśli integracja z Jira nie istnieje, tworzymy ją
            TaskIntegration.objects.create(
                task=task,
                external_id=task_data['jira_key'],
                external_user_id=task_data['jira_user_id']
            )
