import json
from aws_cdk import (
    aws_dms as dms,
    aws_ec2 as ec2,
    core,
)

from project_config import (
    DMS_INSTANCE_CLASS,
    DMS_STORAGE,
    VPC_NAME,
    SQLSERVER_IP_OR_NAME,
    SQLSERVER_PORT,
    SQLSERVER_USER,
    SQLSERVER_PASSWORD,
    DATABASE_NAME,
    BUCKET_PATH,
    MIGRATION_TYPE
)

#basado en https://stackoverflow.com/questions/63616384/creating-an-aws-dms-task-using-aws-cdk

class DMSTask(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, dms_instance, source_endpoint, target_endpoint, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.task = dms.CfnReplicationTask(
            self, 
            "task",
            migration_type=MIGRATION_TYPE,
            replication_instance_arn = dms_instance.ref,
            source_endpoint_arn=source_endpoint.ref,
            target_endpoint_arn=target_endpoint.ref,
            replication_task_identifier='full-load-sql-2-s3',
            # https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html
            table_mappings= json.dumps({
                "rules": [{
                "rule-type": "selection",
                "rule-id": "1",
                "rule-name": "1",
                "object-locator": {
                    "schema-name": "dbo",
                    "table-name": "sport%"
                },
                "rule-action": "include"
                }]
            }),
            #https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.Saving.html
            replication_task_settings = json.dumps({
                "FullLoadSettings": {
                    "TargetTablePrepMode": "DROP_AND_CREATE",
                },
                "Logging": {
                    "EnableLogging": True
                },

            })

        )