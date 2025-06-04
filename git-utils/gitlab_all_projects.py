import requests
import json

url = "https://git.naspersclassifieds.com/api/v4/groups"

payload = ""
headers = {
    'PRIVATE-TOKEN': "FdTWd-jKYgVngEyKUFRS",
    'cache-control': "no-cache",
    'Postman-Token': "075b0ae2-8f9a-41ec-867a-7d0c95a8b67f"
    }

# Get all groups
allproject = []

response = requests.request("GET", url, data=payload, headers=headers)
groups = json.loads(response.text)
for g in groups:
  id = g["id"]
  fullpath = g["full_path"]
  # print(fullpath)
  # print("*************************")
  if "dbz" in fullpath:
    url = "https://git.naspersclassifieds.com/api/v4/groups/" + str(id) + "/projects"
    response = requests.request("GET", url, data=payload, headers=headers)
    projects = json.loads(response.text)
    for p in projects:
      prjname = p["name"]
      # print(prjname)
      allproject.append(prjname)

uniprojects  = set(allproject)
with open('allprojects.txt', 'w') as f:
  for p in uniprojects:
    print(p)
    f.write("%s\n" % p)
