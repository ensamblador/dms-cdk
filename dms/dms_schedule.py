

from aws_cdk import (
    aws_dms as dms,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_iam as iam, 
    aws_events_targets as targets,
    aws_events as events,
    core,
)

from project_config import (
    DMS_INSTANCE_CLASS,
    DMS_STORAGE,
    VPC_NAME
)



class Schedule(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str,  task,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        lambda_start_dms_task = _lambda.Function(
            self, "post_crawler", 
            handler='lambda_function.lambda_handler',
            code=_lambda.Code.asset("./lambdas/dms/start_task"),
            timeout=core.Duration.seconds(20),       
            memory_size=128,
            runtime=_lambda.Runtime.PYTHON_3_8, 
            environment = {
                'REPLICATION_TASK_ARN': task.ref,
            }
        )
        
        lambda_start_dms_task.add_to_role_policy( iam.PolicyStatement(actions=["dms:StartReplicationTask"], resources=['*']))


        event_rule_daily = events.Rule(self, "cada-dia",schedule=events.Schedule.cron(day='*',hour='03', minute='00'))
        event_rule_daily.add_target(targets.LambdaFunction(lambda_start_dms_task))