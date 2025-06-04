#!/bin/bash

# Setting environment variables
region="${REGION:-eu-west-1}"
host="${HOST:-https://vpc-logman-internal-l3d4uiss2yjg2c4vqbve7bzkma.eu-west-1.es.amazonaws.com}"
index="${INDEX:-dev-automation-audit}"
message="${MESSAGE}"
user="${USER}"
service_name="${SERVICE_NAME:-null}"
workflow_executed="${WORKFLOW_EXECUTED}"
input_parameters="${INPUT_PARAMETERS}"
link_to_execution="${LINK_TO_EXECUTION}"
environment="${ENVIRONMENT:-prod}"

# URL for OpenSearch
url="${host}/${index}/_doc"

# Current timestamp in ISO 8601 format
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# JSON payload
json_payload=$(cat <<EOF
{
    "message": "$message",
    "timestamp": "$timestamp",
    "user": "$user",
    "environment": "$environment",
    "service_name": "$service_name",
    "workflow_executed": "$workflow_executed",
    "input_parameters": "$input_parameters",
    "link_to_execution": "$link_to_execution"
}
EOF
)

# Send request and log response status code
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" \
-H "Content-Type: application/json" \
-d "$json_payload")

echo "Response status code: $response"
