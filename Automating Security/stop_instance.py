"""
Scenario:
Below lambda function code will get trigger by SNS which will be trigger by CloudWatch Alarm when there will more than 2 invalid login in BastionHost
Instance.
The below lambda function will stop the instance. 
"""

import json, boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
	sns = event['Records'][0]['Sns']
	json_msg = json.loads(sns['Message'])

	#Extracting instance id
	instance = json_msg['AlarmDescription'].split()[-1]

	ec2.stop_instances(InstanceIds=[instance])

	print("Stopped instance %s" % instance)
