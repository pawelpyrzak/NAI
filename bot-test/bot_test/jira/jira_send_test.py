import json
import requests
from decouple import config
from requests.auth import HTTPBasicAuth

url = "https://projektdomki.atlassian.net/rest/api/3/issue"
user = "s24293@pjwstk.edu.pl"
pwd = config("JIRA_API_KEY")

auth = HTTPBasicAuth(user, pwd)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Atlassian Document Format (ADF) for the description field
payload = json.dumps({
    "fields": {
        "project": {
            "key": "KAN"
        },
        "summary": "New task summary",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Description of the new task in ADF format"
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "Task"
        }
    }
})

response = requests.post(url, data=payload, headers=headers, auth=auth)

if response.status_code == 201:
    print("Task created successfully!")
else:
    print(f"Failed to create task: {response.status_code}")
    print(response.json())