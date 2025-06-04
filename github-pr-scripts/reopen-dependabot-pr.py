import os
from github import Github

token = os.environ.get('GITHUB_TOKEN')
dependabot_user_id = 49699333
dbz_bot_user_id = 60386729

g = Github(token)

user = g.get_user()
repos = user.get_repos()


pr_list = []
final_list = []


def is_duplicate_pr(pr, repo):
    # Check for duplicate PR in closed PRs
    for pull_request in pr_list:
        if pr.title.split()[1] == pull_request.title.split()[1] and pr.title.split()[-1] == pull_request.title.split()[-1]:
            print(f'=== {pr.title} {repo} created at : {pr.created_at} is a duplicate of {pull_request.title} created at : {pull_request.created_at}\n')
            return True

    # Check for duplicate PR in open PRs
    r = g.get_repo(repo.full_name)

    for p in r.get_pulls(state='open'):
        if pr.title.split()[1] == p.title.split()[1] and pr.title.split()[-1] == p.title.split()[-1]:
            print(f'||| {pr.title} {repo} created at : {pr.created_at} is a duplicate of {p.title} created at : {p.created_at}')
            return True

    return False

def reopen_unmerged_dependabot_pr(pr, repo, branch_deleted):
    # If branch is deleted, restore the branch
    if branch_deleted:
        try:
            print(f'Restoring branch: {pr.head.ref}')
            repo.create_git_ref("refs/heads/"+pr.head.ref, sha=pr.head.sha)
        except Exception as ex:
            print(ex)
    
    # Reopen PR
    try:
        print(f'Re-opening: {pr.title} #{pr.id}, created by : {pr.user.login} in Repo: {repo.full_name}')
        pr.edit(state='open')
    except Exception as e:
        print(e)



def get_unmerged_dependabot_pr():
    count = 0
    branch_deleted = False
    for repo in repos:
        print(f'\n Processing {repo.name}')
        
        for pr in repo.get_pulls(state='closed'):
            
            # check if PR was opened by dependabot and unmerged
            if pr.user.id==dependabot_user_id and not pr.merged_at:
                issue_url = pr.issue_url
                pr_as_issue = pr.as_issue()
                closed_by = pr_as_issue.closed_by
                
                # check if PR was closed by dbz-git-stats-bot and is not a duplicate PR for same dependency in same repo
                if closed_by.id == dbz_bot_user_id:
                    is_duplicate = is_duplicate_pr(pr, repo)
                    if not is_duplicate:
                        pr_list.append(pr)
                        pr_events = pr_as_issue.get_events()
                        for i in pr_events:
                            if i.event =='head_ref_deleted':
                                branch_deleted = True
                        reopen_unmerged_dependabot_pr(pr, repo, branch_deleted)
                        count = count + 1
                        final_list.append([repo.name, pr.title, pr.id])
        
        # clear temporary list of PRs within current repo
        pr_list.clear()

    print(f'Total PRs reopened :{count}')
    print("Following PRs were reopened : ")
    for i in final_list:
        print(i)



get_unmerged_dependabot_pr()




