
import os
from datetime import datetime, timedelta
from github import Github
import config

GITHUB_TOKEN = config.GITHUBTOKEN 

def main():

    g = Github(GITHUB_TOKEN)
    owner = g.get_user()

    for org in owner.get_orgs():
        if org.login == 'dbz':
            dbz_org = org
            break

# Region Get team repo
    # teams = dbz_org.get_teams()
    # backendteam = [t for t in teams if t.name == 'dbz-backend'][0]
    # backend_repos = backendteam.get_repos()
    # for repo in backend_repos:
    #     print(repo.name)
# EndRegion Get Team Repo

    owner_repos = [repo for repo in dbz_org.get_repos()]
    year = timedelta(days=365)

    for repo in owner_repos:        
        last_updated = datetime.now() - repo.updated_at

        if (last_updated > year):
            print(repo.name)


if __name__ == '__main__':
    main()