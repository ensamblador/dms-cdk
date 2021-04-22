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

class DMSEventSubscription(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, sns_topic, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        subs = dms.CfnEventSubscription(
            self,
            "subscription",
            sns_topic_arn=sns_topic.topic_arn,
            enabled=True,
            source_type= 'replication-task',
            event_categories= ['state change', 'failure']
        )        