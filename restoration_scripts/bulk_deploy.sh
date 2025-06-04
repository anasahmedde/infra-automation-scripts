#!/bin/bash

set -e

trigger_workflow_dispatch() {
    environment=$1
    application=$2

    if [ "$application" == "dbz" ]; then
        response=$(curl -u "${gh_pat}" \
            -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/dbz/$application/actions/workflows/build_and_deploy.yml/dispatches" \
            -d '{"ref":"main", "inputs": { "dbz_ENVIRONMENT":"'"${environment}"'"}}')
    else
        response=$(curl -u "${gh_pat}" \
            -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/dbz/$application/actions/workflows/build_and_deploy.yml/dispatches" \
            -d '{"ref":"main", "inputs": { "environment":"'"${environment}"'"}}')
    fi

    if [ "$response" -eq 204 ]; then
        echo "Workflow triggered successfully for $application"
    else
        echo "Failed to trigger workflow for $application"
        echo "Response code: $response"
    fi
}

# Default services
services=(
        'motors-paa-c2c-frontend',
        'savedsearch-service',
        'calltracking',
        'pegasus',
        'nomer',
        'sherlock',
        'report-listings-service',
        'notification-scheduler',
        'favorites-service',
        'tx-service',
        'property-lpv-service',
        'content-first-service',
        'dbz',
        'lilith',
        'izin',
        'kraken',
        'bigluu',
        'greedy',
        'kombi',
        'codi',
        'fuloos',
        'authenticator',
        'location-service',
        'motors-paa-service',
        'image-upload-service',
        'chat-service',
        'motors-paa-desktop-frontend',
        'motors-paa-mobile-frontend'
)

# Deploy each service
IFS=',' read -r -a environments <<< "${environments}"
for environment in "${environments[@]}"; do
    for service in "${services[@]}"; do
        trigger_workflow_dispatch "$environment" "$service"
    done
done
