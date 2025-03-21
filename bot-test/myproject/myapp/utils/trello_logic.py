import requests

from ..models import TrelloConfig, ProjectExternalKey, ProjectPlatform, UserPlatformAccount, TaskIntegration


def get_platform_user_id(user, platform):
    user_platform_account = UserPlatformAccount.objects.filter(user=user, platform=platform).first()
    return user_platform_account.platform_user_id if user_platform_account else None


def create_trello_card(task, user_platform_account):
    trello_config = TrelloConfig.objects.filter(group=task.project.group).first()
    trello_platform = ProjectPlatform.objects.filter(name="Trello").first()
    project_external_key = ProjectExternalKey.objects.filter(project=task.project, platform=trello_platform).first()

    status = "Do zrobienia"
    if not trello_config:
        return None, None
    trello_api_key = trello_config.api_key
    trello_token = trello_config.token
    trello_board_id = project_external_key.key
    trello_list_id = get_list_id(trello_board_id, status, trello_api_key, trello_token)
    if not trello_list_id:
        return
    trello_user_id = get_platform_user_id(task.assignee, trello_platform) if task.assignee else None

    url = "https://api.trello.com/1/cards"
    query = {
        "name": task.title,
        "desc": task.description,
        "idList": trello_list_id,
        "due": task.due_date,
        "start": task.start_date,
        "idMembers": trello_user_id,
        "key": trello_api_key,
        "token": trello_token
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        data = response.json()
        return data.get("id"), task.assignee.id if task.assignee else None
    return None, None


def get_list_id(board_id, list_name, api_key, token):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {"key": api_key, "token": token}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            if lst["name"].lower() == list_name.lower():
                return lst["id"]
        print("Nie znaleziono listy o podanej nazwie.")
    else:
        print(f"Błąd: {response.status_code}, {response.text}")
    return None


def update_trello_card(task, updated_fields):
    trello_config = TrelloConfig.objects.filter(group=task.project.group).first()
    trello_platform = ProjectPlatform.objects.filter(name="Trello").first()
    trello_task = TaskIntegration.objects.get_object_or_404(task=task)
    project_external_key = ProjectExternalKey.objects.filter(project=task.project, platform=trello_platform).first()

    if not trello_config or not project_external_key:
        return None

    trello_api_key = trello_config.api_key
    trello_token = trello_config.token
    trello_card_id = trello_task.key  # Zakładam, że external_id przechowuje Trello card ID

    url = f"https://api.trello.com/1/cards/{trello_card_id}"

    query = {
        "key": trello_api_key,
        "token": trello_token
    }
    if "status" in updated_fields:
        trello_list_id = get_list_id(project_external_key.key, updated_fields["status"].name, trello_api_key,
                                     trello_token)
        if trello_list_id:
            query["idList"] = trello_list_id
            updated_fields.pop('status')
    query.update(updated_fields)

    response = requests.put(url, params=query)

    if response.status_code == 200:
        print(f"✅ Zaktualizowano kartę {trello_card_id} w Trello!")
    else:
        print(f"❌ Błąd aktualizacji Trello: {response.status_code} {response.text}")

    return response
