import requests
import json
from decouple import config

# URL do utworzenia zgłoszenia w projekcie Jira
base_url = "https://projektdomki.atlassian.net/rest/api/3/search"
user = "s24293@pjwstk.edu.pl"
pwd = config("JIRA_API_KEY")
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
query={
    "jql": "project=KAN"
}
api_url = f"{base_url}"
print(api_url)
response = requests.get(base_url, headers=headers,params=query, auth=(user,pwd))

if response.status_code == 200:
    issues = response.json()["issues"]
    for issue in issues:
        print(issue["key"], issue["fields"]["summary"], issue["fields"]["duedate"])
        if issue["fields"]["assignee"]:
            print(issue["fields"]["assignee"]["displayName"],"\n")
else:
    print(f"Error: {response.status_code} - {response.text}")
