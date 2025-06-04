import csv
import boto3
import jira
import gitprime
import datetime

TEAMS = {
    'AdTech': {
        'jira_board_id': 1125,
        'gitprime_team_id': 10203,
    },
    'Avengers': {
        'jira_board_id': 743,
        'gitprime_team_id': 9378,
    },
    'Pro-Tools': {
        'jira_board_id': 501,
        'gitprime_team_id': 9352,
    },
    'Property Buyer Side': {
        'jira_board_id': 852,
        'gitprime_team_id': 9367,
    },
    'Property Health': {
        'jira_board_id': 525,
        'gitprime_team_id': 9365,
    },
    'Motors C2C': {
        'jira_board_id': 1059,
        'gitprime_team_id': 7723,
    },
    'Motors B2C': {
        'jira_board_id': 1166,
        'gitprime_team_id': 11190,
    },
}

S3_BUCKET_NAME = 'dbz-tech-dashboard-data'
S3_FILE_NAME = 'cadence'
S3_LATEST = '_latest'
S3_FILE_EXTENSION = '.csv'
S3_BACKUP_PATH = 'backup/cadence/'
LAMBDA_WRITABLE_PATH = '/tmp/'

TMP_FILE = '{path}{file_name}{ext}'.format(
    path=LAMBDA_WRITABLE_PATH, 
    file_name=S3_FILE_NAME, 
    ext=S3_FILE_EXTENSION
)

def generate_csv_to_local_temp_file():

    gitprime_start_date_col_2, gitprime_end_date_col_2 = gitprime.get_gitprime_date_range(2)
    gitprime_start_date_col_1, gitprime_end_date_col_1 = gitprime.get_gitprime_date_range(1)

    headers = [
        "Team",
        "Most recent {sprints} sprints Delivered / Committed (%)".format(sprints=jira.NUMBER_OF_SPRINTS),
        "Active Developer days (/5) average of last 14 days {start_date} - {end_date}".format(
            start_date=gitprime_start_date_col_2,
            end_date=gitprime_end_date_col_2
        ),
        "Active Developer days (/5) average of last 7 days {start_date} - {end_date}".format(
            start_date=gitprime_start_date_col_1,
            end_date=gitprime_end_date_col_1
        )
    ]

    with open(TMP_FILE, 'w') as ds:
        out = csv.writer(ds, delimiter=',', quoting=csv.QUOTE_ALL)
        out.writerow(headers)
        for name, params in TEAMS.items():
            out.writerow([
                name, 
                jira.get_velocity_formatted_sting_for_last_sprints(params['jira_board_id']),
                gitprime.get_active_developer_days(params['gitprime_team_id'], 2),
                gitprime.get_active_developer_days(params['gitprime_team_id'], 1),
            ])

def send_to_s3():
    s3 = boto3.resource('s3')
    # Store as latest version, used for dashboard
    s3.Bucket(S3_BUCKET_NAME).put_object(
        Key='{file_name}{latest}{ext}'.format(file_name=S3_FILE_NAME, latest=S3_LATEST, ext=S3_FILE_EXTENSION), 
        Body=open(TMP_FILE, 'rb')
    )

    # Store copy with datestamp in name, for backup if needed
    s3.Bucket(S3_BUCKET_NAME).put_object(
        Key='{path}{file_name}_{date:%Y_%m_%d_%H_%M_%S}{ext}'.format(
            path=S3_BACKUP_PATH, 
            file_name=S3_FILE_NAME, 
            date=datetime.datetime.now(),
            ext=S3_FILE_EXTENSION
        ), 
        Body=open(TMP_FILE, 'rb')
    )

def run_script(event, context):
    generate_csv_to_local_temp_file()
    send_to_s3()

# - Debug: write to local csv file
def debug():
    generate_csv_to_local_temp_file()

#debug()