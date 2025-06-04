import gitlab

gl = gitlab.Gitlab('https://git.naspersclassifieds.com/', private_token='FdTWd-jKYgVngEyKUFRS')
gl.auth()

# list all the projects
projects = gl.projects.list()
for project in projects:
    print(project.name)