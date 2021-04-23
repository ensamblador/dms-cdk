

from aws_cdk import (
    aws_dms as dms,
    aws_ec2 as ec2,
    aws_iam as iam, 
    aws_lambda as _lambda,
    aws_events as events,
    aws_glue as glue,
    aws_sns_subscriptions as subscriptions,
    aws_events_targets as targets,
    core,
)

from project_config import (
    BUCKET_PATH,
    GLUE_DATABASE_NAME,
    GLUE_JOB_SCRIPT_LOCATION
)

class Discover(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, sns_topic,  dms_instance, dms_task, bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        

        glue_database = glue.Database(self, 'database', database_name=GLUE_DATABASE_NAME)
        
        
        s3_access_statement = iam.PolicyStatement(actions=["s3:*"], resources=[bucket.bucket_arn, "{}/*".format(bucket.bucket_arn)])

        glue_role = iam.Role(
            self, 'glue_role',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
            inline_policies = [iam.PolicyDocument(statements=[s3_access_statement])],
            managed_policies=[ iam.ManagedPolicy.from_managed_policy_arn(self, 'managedpolicy',managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole')]
        )

        s3_targets = glue.CfnCrawler.S3TargetProperty(path='{}/{}/'.format(bucket.bucket_name, BUCKET_PATH ))

        crawler = glue.CfnCrawler(
            self, "crawler",
            database_name=glue_database.database_name,
            role=glue_role.role_arn,
            targets = glue.CfnCrawler.TargetsProperty(s3_targets=[s3_targets])
        )

        lambda_post_dms = _lambda.Function(
            self, "post_dms", 
            handler='lambda_function.lambda_handler',
            code=_lambda.Code.asset("./lambdas/glue/post_dms"),
            timeout=core.Duration.seconds(20),       
            memory_size=128,
            runtime=_lambda.Runtime.PYTHON_3_8, 
            environment = {
                'DMS_INSTANCE': dms_instance.ref,
                'DMS_TASK': dms_task.ref,
                'GLUE_CRAWLER': crawler.ref
            }
        )

        lambda_post_dms.add_to_role_policy( iam.PolicyStatement(actions=["dms:*"], resources=['*']))
        lambda_post_dms.add_to_role_policy( iam.PolicyStatement(actions=["glue:*"], resources=['*']))



        sns_topic.add_subscription(subscriptions.LambdaSubscription(lambda_post_dms))
        self.crawler = crawler


class Process(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, crawler, source_bucket, processed_bucket,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        s3_access_statement1 = iam.PolicyStatement(actions=["s3:*"], resources=[source_bucket.bucket_arn, "{}/*".format(source_bucket.bucket_arn)])
        s3_access_statement2 = iam.PolicyStatement(actions=["s3:*"], resources=[processed_bucket.bucket_arn, "{}/*".format(processed_bucket.bucket_arn)])

        glue_role = iam.Role(
            self, 'glue_role',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
            inline_policies = [iam.PolicyDocument(statements=[s3_access_statement1, s3_access_statement2])],

            managed_policies=[ iam.ManagedPolicy.from_managed_policy_arn(
                self, 'managedpolicy',managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole')]
        )

        glue_job = glue.CfnJob(
            self, 'job', 
            command=glue.CfnJob.JobCommandProperty(
                name='pythonshell',
                python_version="3",
                script_location=GLUE_JOB_SCRIPT_LOCATION
            ),
            role = glue_role.role_arn)

        s3_targets = glue.CfnCrawler.S3TargetProperty(path='{}/{}/'.format(processed_bucket.bucket_name, 'proccessed' ))

        crawler_processed = glue.CfnCrawler(
            self, "crawler",
            database_name='processed',
            role=glue_role.role_arn,
            targets = glue.CfnCrawler.TargetsProperty(s3_targets=[s3_targets])
        )

        lambda_post_crawler = _lambda.Function(
            self, "post_crawler", 
            handler='lambda_function.lambda_handler',
            code=_lambda.Code.asset("./lambdas/glue/post_crawler"),
            timeout=core.Duration.seconds(20),       
            memory_size=128,
            runtime=_lambda.Runtime.PYTHON_3_8, 
            environment = {
                'CRAWLER': crawler.ref,
                'GLUE_JOB': glue_job.ref
            }
        )

        lambda_post_crawler.add_to_role_policy( iam.PolicyStatement(actions=["glue:*"], resources=['*']))

        event_rule = events.Rule(self, 'gluecrawlerfinish',description='Glue Crawler',
            event_pattern=events.EventPattern(source=['aws.glue'],
            detail_type=['Glue Crawler State Change'],
            detail={               
                "state": ["Succeeded", "Failed"]
            })
        )
        
        event_rule.add_target(targets.LambdaFunction(handler=lambda_post_crawler))