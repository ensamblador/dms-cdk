import json
import os
import boto3
import datetime

def lambda_handler(event, context):
    print (event)
    dms_event = json.loads(event['Records'][0]['Sns']['Message'])
    print (dms_event)
    
    if 'FULL_LOAD_ONLY_FINISHED' in dms_event['Event Message']:
        print('DMS Terminó OK, iniciando Crawler...')
        client = boto3.client('glue')
        response = client.start_crawler(
            Name=os.environ.get('GLUE_CRAWLER'),
        )
        print (response)
        
    
    
