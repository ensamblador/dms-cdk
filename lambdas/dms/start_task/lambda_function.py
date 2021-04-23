import json
import os
import boto3
import datetime

def lambda_handler(event, context):
    print (event)
    client = boto3.client('dms')
    
    response = client.start_replication_task(
        ReplicationTaskArn=os.environ.get('REPLICATION_TASK_ARN'),
        StartReplicationTaskType='reload-target'
    )

    print (response)
