from botocore.vendored import requests
import datetime
import os

GITPRIME_TOKEN = os.environ['GITPRIME_TOKEN']
GITPRIME_API_URL = 'https://app.gitprime.com/v3/customer/core/{path}'
API_TIMEOUT_SECONDS = 30

def get_gitprime_api_response(path, params=None):
    response = requests.get(
        url=GITPRIME_API_URL.format(path=path), 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {gitprime_token}".format(gitprime_token=GITPRIME_TOKEN)
        },
        params=params,
        timeout=API_TIMEOUT_SECONDS
    )
    if response.ok:
        return response.json()
    else:
        raise Exception("Can't get response from Gitprime API")

def get_team_members_ids(team_id):
    try:
        response = get_gitprime_api_response(
            path='users/', 
            params={
                'limit': 1000,
                'team__id': team_id,
                'apex': 'true',
                'fields': 'id',
            }
        )
        team_members_ids = [result['id'] for result in response['results']]
        return team_members_ids
    except:
        return 'Could not get team member ids'

def get_gitprime_date_range(number_of_weeks):
    number_of_days = number_of_weeks * 7
    date_format = '%Y-%m-%d'
    start_date = (datetime.datetime.now() + datetime.timedelta(-1*number_of_days)).strftime(date_format)
    end_date = datetime.datetime.now().strftime(date_format)

    return start_date, end_date

def get_git_prime_data(start_date, end_date, team_members_ids):
    # FIXME: 
    # Support for 1000 records only
    # Should be fine as long as the product of number of days queried and number of team members is less than a 1000
    # e.g. for a 30 days timeframe, this supports teams of up to 33 members

    try:
        response = get_gitprime_api_response(
            path='commits.agg/?group_by[apex_user_id,author_local_date__date]',
            params={
                'limit': 1000,
                'apex_user_id__in': ','.join(map(str, team_members_ids)),
                'is_merge': 'false',
                'is_pr_orphan': 'false',
                'is_haloc__lt': 1000,
                'smart_dedupe': 'true',
                'author_local_date__gte': start_date,
                'author_local_date__lt': end_date,
                'aggregate[count]': 'id',
                'aggregate[sum]': 'haloc,churn',
            }
        )
        return response
    except:
        return 'Could not get data'

# - Get active developer days
def get_active_developer_days(team_id, number_of_weeks):
    team_members_ids = get_team_members_ids(team_id)
    start_date, end_date = get_gitprime_date_range(number_of_weeks)
    try:
        data = get_git_prime_data(start_date, end_date, team_members_ids)
        results = data['results']
        active_days = len(results)
        average_active_developer_days = (float(active_days) / float(len(team_members_ids))) / float(number_of_weeks)

        formatted_average_active_developer_days = "%.1f" % average_active_developer_days
        return formatted_average_active_developer_days
    except Exception as e:
        return 'Could not get active developer days', e
