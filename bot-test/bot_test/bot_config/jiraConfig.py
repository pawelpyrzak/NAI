from decouple import config

project_key = "PROJ"
JIRA_USER = "inzynierkabot@int.pl"
JIRA_TOKEN = config("JIRA_API_KEY2")
JIRA_INSTANCE = "int-team-hvyepex0.atlassian.net"
JIRA_URL = f"https://{JIRA_INSTANCE}/rest/api/2/"