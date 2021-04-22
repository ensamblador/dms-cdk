
from aws_cdk import (
    aws_dms as dms,
    aws_iam as iam,
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
    BUCKET_PATH
)

#basado en https://stackoverflow.com/questions/63616384/creating-an-aws-dms-task-using-aws-cdk

class DMSEndpoints(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, target_bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        self.source = dms.CfnEndpoint(
            self, "source-dp",
            endpoint_type = 'source', 
            engine_name='sqlserver', 
            server_name=SQLSERVER_IP_OR_NAME,
            database_name=DATABASE_NAME,
            port=SQLSERVER_PORT,
            username=SQLSERVER_USER,
            password=SQLSERVER_PASSWORD
            )

        s3_access_statement = iam.PolicyStatement(actions=["s3:*"], resources=[target_bucket.bucket_arn, "{}/*".format(target_bucket.bucket_arn)])

        service_role = iam.Role(
            self, 's3-access', assumed_by=iam.ServicePrincipal('dms.amazonaws.com'),
            inline_policies = [iam.PolicyDocument(statements=[s3_access_statement])]
        )

        self.target = dms.CfnEndpoint(
            self, "target-ep",
            endpoint_type = 'target', 
            engine_name='s3',
            s3_settings= dms.CfnEndpoint.S3SettingsProperty(
                service_access_role_arn = service_role.role_arn,
                bucket_name = target_bucket.bucket_name,
                bucket_folder=BUCKET_PATH)
        )