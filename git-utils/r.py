import requests
import json

# curl -v -H "Content-Type:application/json" 
# https://gitlab.example.com/api/v3/projects?private_token=12345 
# -d "{ \"name\": \"project_name\",\"namespace_id\": \"555\" }

#namespace = "https://git.naspersclassifieds.com/api/v4/namespaces"
# group  = "https://git.naspersclassifieds.com/api/v4/groups"

project = "https://git.naspersclassifieds.com/api/v4/projects"


headers = { 
            "PRIVATE-TOKEN" : "FdTWd-jKYgVngEyKUFRS",
            "Content-Type" : "application/json"
          }

data = {
        "name": "test3-sample-project",
        "path": "test3-sample-project",
        "namespace_id": "1015",
        "visibility": "internal",
        "issues_enabled": "true",
        "wiki_enabled": "true",
        "snippets_enabled": "true",
        "import_url": "https://shabbirdbz:e387287ba1718e3331fe791ee5f69ec24b042999@github.com/dbz/ops-sample.git/"       
        }
r = requests.post(url=project, headers=headers, data=data)
print(r.status_code)
if r.status_code == 201:
    pretty_json = json.loads(r.text)
    print(json.dumps(pretty_json, indent=2))
else:
    print(r.text)

