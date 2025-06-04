import requests
import json

url = "https://git.naspersclassifieds.com/api/v4/projects"

payload = ""
headers = {
    'PRIVATE-TOKEN': "FdTWd-jKYgVngEyKUFRS",
    'cache-control': "no-cache",
    'Postman-Token': "075b0ae2-8f9a-41ec-867a-7d0c95a8b67f"
    }

response = requests.request("GET", url, data=payload, headers=headers)
projects = json.loads(response.text)
for p in projects:
    print(p["name"])
