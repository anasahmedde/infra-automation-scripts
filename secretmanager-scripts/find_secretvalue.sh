#!/bin/bash

# Run ./find_secretvalue.sh “YOUR_KEYWORD”
REGION='eu-west-1'

# Your AWS Region
if [ ${AWS_DEFAULT_REGION} ]; then
  REGION=${AWS_DEFAULT_REGION}
fi

# Check if a search value was provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <search-value>"
    exit 1
fi

# The specific value you're searching for
SEARCH_VALUE="$1"

echo Looking for secrets that contain \"${SEARCH_VALUE}\" in the region $REGION

# List all secrets and get their names
aws secretsmanager list-secrets --region "$REGION" --output json | jq -r '.SecretList[].Name' | while read -r secretName; do
    # Get the secret value safely, catching any errors
    secretValue=$(aws secretsmanager get-secret-value --secret-id "$secretName" --region "$REGION" --query SecretString --output text 2>/dev/null)

    # Use jq to iterate over all values; direct errors to /dev/null in case of non-JSON content
    if echo "$secretValue" | jq -e -r 'select(.!=null) | .[]' 2>/dev/null | grep -q "$SEARCH_VALUE"; then
        echo "Found '$SEARCH_VALUE' in secret: $secretName"
    fi
done