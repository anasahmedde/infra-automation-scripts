# Data Copy Pipeline Base Workflows

1. Dump schema only from prod (Whole DB for all identified services).   --> `data_copy_prod_dump_db_schema.yml`
2. Dump identified tables data from prod (For all identified services). --> `data_copy_prod_dump_tables_data.yml`
3. Drop db in lower env.                                                --> `data_copy_lower_env_drop_db.yml`
4. Restore schema only from prod to lower env.                          --> `data_copy_lower_env_restore_db_schema.yml`
5. Restore identified tables data in lower env.                         --> `data_copy_lower_env_restore_tables_data.yml`

# Data Copy Pipeline Orchestrator Workflows

Single Orchestrator pipeline for dump and restore:
* Single Orchestrator pipeline for [dump + restore]. --> `data_copy_orchestrator.yml`

There are also two additional Orchestrator pipelines:
1. Orchestrator pipeline for creating dump.     --> `data_copy_prod_dump_orchestrator.yml`
2. Orchestrator pipeline for restoring dump.    --> `data_copy_lower_env_restore_orchestrator.yml`

For dumping [schema + data] from prod to lower env, choose `prod` as an input **Environment** in orchestrator pipeline for creating dump (`data_copy_prod_dump_orchestrator.yml`) and run the workflow.

For restoring [schema + data] in lower env, choose `beta-cc` or `any other lower env` as an input **Environment** and select prod dump bucket `dbz-data-copy-prod` as input **SOURCE_S3_BUCKET** in orchestrator pipeline for restoring dump (`data_copy_lower_env_restore_orchestrator.yml`) and run the workflow.


# Data Copy Pipeline CSV Structure, File Naming Convention and AWS Secerets Naming Convention

* **Services** defined in csv file located in folder `data_copy_inputfiles/dbs/targeted_services.csv`
* **Tables** defined in csv file located in folder `data_copy_inputfiles/tables/${service}_tables.csv`

Services naming convention follow exact naming convention as defined in [helmfiles-apps apps directory](https://github.com/dbz/helmfiles-apps/tree/master/apps).

Tables are defined in csv having prefix exactly as service define in `data_copy_inputfiles/dbs/targeted_services.csv`
e.g. `${service}_tables.csv` --> `chat-service_tables.csv`

The pipeline uses DB secrets defined with pattern data-copy-secrets/${Environment}/${service} in AWS Secrets Manager.
e.g. `data-copy-secrets/${Environment}/${service}` --> `data-copy-secrets/beta-cc/chat-service`

AWS Secrets structure is:
```
{
    "DATABASE_NAME": "horizontal_buyer",
    "DATABASE_HOST": "beta-cc-batch2-rds.dbzbeta.internal",
    "DATABASE_USER": "dbzbatch2",
    "DATABASE_PASSWORD": "xxxxxxxxxxxxx",
    "DATABASE_ENGINE": "mysql"
}
```

Important key is **DATABASE_ENGINE** which must be define and it can either be `mysql` or `postgresql` depending on the service and the database engine used in the service.

## Dump/Restore all data to/from S3 using MySQL Shell 8.0
MySQL Shell is an advanced client and code editor for MySQL which provides scripting capabilities for JavaScript and Python and includes APIs for working with MySQL.


### Steps to dump data directly to S3 using MySQL Shell.

The MySQL Shell along with AWS CLI must be installed to perform the dump

```
# Create MySQL Client Pod

kubectl run -n infra dbz-data-copy-mysql-client-beta-cc --image=mysql --restart=Never --env=MYSQL_ALLOW_EMPTY_PASSWORD=true


# install AWS CLI

kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- microdnf install unzip less
kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- unzip ./awscliv2.zip
kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- ./aws/install

# Configure AWS CLI

kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- /bin/sh -c "aws configure set aws_access_key_id XXXXXXXXXXXXXXXXXXXXX && aws configure set aws_secret_access_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX && aws configure set default.region eu-west-1"
kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- aws sts get-caller-identity

# Run util.dumpSchemas() to directly dump data to S3 bucket 'dbz-data-copy-test' in folder 's3-tx-database-dump'
# Additionally we can add options like ddlOnly: true or dataOnly: true 

kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- mysqlsh --host=beta-cc-batch2-rds.dbzbeta.internal --user=dbzbatch2 --password=XXXXXXXXXX --js --execute="util.dumpSchemas(['tx'], 's3-tx-database-dump', {s3BucketName: 'dbz-data-copy-test', threads: 8, compatibility: ['strip_definers'], consistent: false, dryRun: false});" --verbose

```

For more options, See [Dump Utility Docs](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-shell-utilities-dump-instance-schema.html).

### Steps to restore data directly from S3 using MySQL Shell.
The MySQL Shell along with AWS CLI must be installed to perform the restore

Note: `performance_schema` should be on in order to load data in destination db.
Set `performance_schema` in destination rds's db parameter group value to `1`. This will require the restart of the rds server.

```
# Run util.loadDump() to load data from S3 bucket 'dbz-data-copy-test' and from folder 's3-tx-database-dump'

kubectl exec -n infra -it data-copy-mysql-client-beta-cc -- mysqlsh --host=beta-cc-batch2-rds.dbzbeta.internal --user=dbzbatch2 --password=XXXXXXXXXX --js --execute="util.loadDump('s3-tx-database-dump', {s3BucketName: 'dbz-data-copy-test', schema: 'tx2', threads: 8, progressFile: '', dryRun: false})

```

For more options, See [Restore Utility Docs](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-shell-utilities-load-dump.html).


The AWS CLI credentials used above must have policy like this:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::dbz-data-copy-test/*",
                "arn:aws:s3:::dbz-data-copy-test"
            ]
        }
    ]
}
```