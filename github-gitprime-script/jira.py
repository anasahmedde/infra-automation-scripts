from botocore.vendored import requests
import os

JIRA_USERNAME = os.environ['JIRA_USERNAME']
JIRA_API_KEY = os.environ['JIRA_API_KEY']

JIRA_API_URL = 'https://naspersclassifieds.atlassian.net/rest/greenhopper/1.0/rapid/charts/velocity?rapidViewId={jira_board_id}'
API_TIMEOUT_SECONDS = 30

NUMBER_OF_SPRINTS = 3


def get_velocity_data(jira_board_id):
    response = requests.get(
        url=JIRA_API_URL.format(jira_board_id=jira_board_id), 
        headers={"Content-Type": "application/json"}, 
        auth=(JIRA_USERNAME, JIRA_API_KEY),
        timeout=API_TIMEOUT_SECONDS
    )
    if response.ok:
        return response.json()
    else:
        raise Exception("Can't get the Sprint from JIRA for Board", jira_board_id)

def get_velocity_formatted_sting_for_last_sprints(jira_board_id):
	try:
		velocity_chart_data = get_velocity_data(jira_board_id)
	except:
		return "Could not get Velocity Data"

	sprints = velocity_chart_data["sprints"]
    
	team_velocity = ''

	total_committed = 0.0
	total_delivered = 0.0

	for index, sprint in enumerate(sprints):

        # FIXME: This is unordered dictionary, so it's not necessery would be 3 last sprints
        # Either need to sort by date, or id, assuming id is incrementing from sprint to sprint
		if index == NUMBER_OF_SPRINTS:
			#Reached the maximum number of sprints to be included
			break

		sprint_id = sprint["id"]
		sprint_name = sprint["name"]
        
		try:
			# Get committed
			committed = velocity_chart_data["velocityStatEntries"][str(sprint_id)]["estimated"]["value"]
			total_committed += committed

			# Get delivered
			delivered = velocity_chart_data["velocityStatEntries"][str(sprint_id)]["completed"]["value"]
			total_delivered += delivered

		except KeyError:
            # Can be raised in case of sprint not being closed yet
			continue


		rounded_velocity = 0

		if committed:
			velocity = delivered / committed
			rounded_velocity = str(int(velocity * 100)) + " %"
        
		if team_velocity:
			team_velocity += "\n"

		delivered_committed = str(int(delivered)) + " / " + str(int(committed))
		team_velocity += "{sprint_name} {delivered_committed} ({rounded_velocity})".format(sprint_name=sprint_name, delivered_committed=delivered_committed, rounded_velocity=rounded_velocity)

	try: 
		average_velocity = total_delivered / total_committed
		roundedaverage_velocity = str(int(average_velocity * 100)) + " %"
    
		team_velocity += "\n-------"
		team_velocity += "\nTotal: {total_delivered} / {total_committed}".format(total_delivered=str(int(total_delivered)), total_committed=str(int(total_committed)))
		team_velocity += "\nAverage: {roundedaverage_velocity}".format(roundedaverage_velocity=roundedaverage_velocity)

	except: 
		team_velocity += "0 story points committed over last {number_of_sprints}".format(number_of_sprints=NUMBER_OF_SPRINTS)

	return team_velocity
