from datetime import datetime, timedelta

from sympy.polys.polyconfig import query

from bot_test.bot_config.jiraConfig import *
import requests
import json
from decouple import config

# URL do utworzenia zgłoszenia w projekcie Jira
base_url =JIRA_URL+ "search"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
today = datetime.now().strftime("%Y-%m-%d")
jql_query =f' duedate >= "{today}" AND status != "Done"'
queryj={
    "jql": jql_query
}
api_url = f"{base_url}"
print(api_url)
print(jql_query)
response = requests.get(base_url, headers=headers,params=queryj, auth=(JIRA_USER,JIRA_TOKEN))

if response.status_code == 200:
    issues = response.json()["issues"]
    for issue in issues:
        print(issue["key"], issue["fields"]["summary"],issue["fields"]["customfield_10015"], issue["fields"]["duedate"])
        if issue["fields"]["assignee"]:
            print(issue["fields"]["assignee"]["displayName"],"\n")
else:
    print(f"Error: {response.status_code} - {response.text}")
