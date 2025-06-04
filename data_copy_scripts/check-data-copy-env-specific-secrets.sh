#!/bin/bash

# This script assumes that you are on right kubernetes context.
# And your AWS_VAULT variable is set to right aws profile. 

echo "checking kubernetes current context and AWS_VAULT profile"
kubectl config get-contexts | grep "*"
echo $AWS_VAULT

# change env name if required. 
Environment="beta-me"

MYSQL_CLIENT_POD_NAME_PREFIX="data-copy-mysql-client"
POSTGRESQL_CLIENT_POD_NAME_PREFIX="data-copy-postgresql-client"
POD_WAIT_TIME_IN_SECONDS=10

services=(
    "chat-service"
    "favorites-service"
    "horizontal-buyer-service"
    "location-service"
    "monolith"
    "property-lpv-service"
    "savedsearch-service"
    "seller-service"
    "tx-service"
)

for service in "${services[@]}"; do
    echo "Service Name is $service"
    
    # Get data-copy env specific secrets
    rds_secret_result=$(aws secretsmanager get-secret-value --secret-id data-copy-secrets/${Environment}/${service} | jq -r '.SecretString| fromjson')
    rds_host=$(echo $rds_secret_result | jq -r '.DATABASE_HOST')
    rds_username=$(echo $rds_secret_result | jq -r '.DATABASE_USER')
    rds_password=$(echo $rds_secret_result | jq -r '.DATABASE_PASSWORD')
    rds_db=$(echo $rds_secret_result | jq -r '.DATABASE_NAME')
    rds_engine=$(echo $rds_secret_result | jq -r '.DATABASE_ENGINE')

    MYSQL_CLIENT_POD_NAME=${MYSQL_CLIENT_POD_NAME_PREFIX}-${Environment}
    POSTGRESQL_CLIENT_POD_NAME=${POSTGRESQL_CLIENT_POD_NAME_PREFIX}-${Environment}

    if [[ "$rds_engine" = "mysql" ]]; then

        # Create MySQL Client Pod
        pod_exist=$(kubectl get pods -n infra | grep $MYSQL_CLIENT_POD_NAME | { grep -v grep || true; } )
        if [[ -z "$pod_exist" ]]; then
            kubectl run -n infra $MYSQL_CLIENT_POD_NAME --image=mysql --restart=Never --env=MYSQL_ALLOW_EMPTY_PASSWORD=true
            sleep $POD_WAIT_TIME_IN_SECONDS
        fi

        kubectl exec -n infra -it $MYSQL_CLIENT_POD_NAME -- mysql --host=$rds_host --user=$rds_username --password=$rds_password --verbose --execute="SHOW DATABASES;"

    elif [[ "$rds_engine" = "postgresql" ]]; then
        
        # Create PostgreSQL Client Pod
        pod_exist=$(kubectl get pods -n infra | grep $POSTGRESQL_CLIENT_POD_NAME | { grep -v grep || true; } )
        if [[ -z "$pod_exist" ]]; then
            kubectl run -n infra $POSTGRESQL_CLIENT_POD_NAME --image=postgres --restart=Never --env=POSTGRES_PASSWORD=mysecretpassword
            sleep $POD_WAIT_TIME_IN_SECONDS
        fi

        kubectl exec -n infra -it $POSTGRESQL_CLIENT_POD_NAME -- psql -h $rds_host -U $rds_username -W -d postgres -a -v VERBOSITY=verbose -c "SELECT datname FROM pg_database;" <<< "$rds_password"

    fi

done