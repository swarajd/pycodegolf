import boto3
import os
import json

from dotenv import load_dotenv
load_dotenv()

client = boto3.resource(
    'sqs',
    endpoint_url=os.getenv('ENDPOINT_URL'),
    region_name=os.getenv('REGION')
)

queue = client.get_queue_by_name(QueueName='submissions')

send = 0

if (send == 1):
    response = queue.send_message(
        MessageBody=json.dumps({
            'test': 1
        })
    )
    print(response)
else:
    messages = queue.receive_messages()
    print(messages)
    if (len(messages) > 0):
        msg = messages[0]
        print(msg.body)
        msg.delete()