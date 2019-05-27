"""
Automate the detection and remediation of security vulnerabilities using Amazon Inspector, SNS, and Lambda.
"""

import json, boto3

ssm = boto3.client('ssm')
inspector = boto3.client('inspector')

def lambda_handler(event, context):
	print(json.dumps(event))

	#Extracting message that Inspector sent via SNS
	message = event['Records'][0]['Sns']['Message']

	#Get inspector notification type
	notificationType = json.loads(message)['event']
	print("Inspector SNS message type: ", + notificationType)
	#
	if notificationType != "FINDING_REPORTED":
		print('Skipping notification that is now a new finding' + notificationType)
		return -1

	#Extract finding ARN
	findingArn = json.loads(message)['finding']
	print('Finding ARN: ' + findingArn)

	#Get finding and extract detail
	response = inspector.describe_findings(findingArns=[findingArn], local='EN_US')

	finding = response['findings'][0]

	#Skip uninteresting findings
	title = finding['title']

	if title == "Unsupported Operating System or Version":
		print("Skipping finding " + title)
		return 1

	if title == "No potential security issues found":
		print("Skipping finding " + title)
		return 1

	service = finding['service']

	if service != "Inspector":
		print("Skipping finding from service " + service)
		return 1

	cveId = ""
	for attribute in finding['attribute']:
		if attribute['key'] == "CVE_ID":
			cveId = attribute['value']
			break

	print('CVE ID: ' + cveId)

	if cveId == "":
		print("Skipping non-CVE finding (cloud not find CVE-ID)")
		return 1

	instanceId = finding['assetAttributes']['agentId']
	print("Instance Id: ", instanceId)
	if not instanceId.startswith("i-"):
		print("Invalid instance ID: " + instanceId)
		return 1

	#If we got here, we have valid CVE type finding for EC2 instance with well-formed instanceId

	#Query SSM for the information about this instance
	filterList = [{'key':'InstanceIds', 'valueSet':[instanceId]}]
	response = ssm.describe_instance_information(InstanceInformationFilterList=filterList, MaxResults=50)

	instanceInfo = response['InstanceInformationList'][0]

	pingStatus = instanceInfo['PingStatus']
	print("SSM status of instance: ", pingStatus)

	platformType = instanceInfo['PlatformType']
	print("OS type: ",platformType)

	osName = instanceInfo['PlatformName']
	print("OS Name: ", osName)

	osVersion = instanceInfo['PlatformVersion']
	print("OS version: ", osVersion)


	#Terminate if SSM agent is offline
	if pingStatus != 'Online':
		print('SSM agent for this instance is offline: ', pingStatus)
		return 1

	#Lookup the command to update the OS
	if osName.startswith('Ubuntu'):
		commandLine = "apt-get update -y; agt-get upgrade -y"
	elif osName.startswith('Amazon Liux'):
		commandLine = "yum update -y; yum upgrade -y"
	else:
		print("Unsupported Linux distro: ", osName)
		return 1

	print("Command line to execute:  ", commandLine)

	#Run command using SSM
	response = ssm.send_command(
			InstanceIds=[instanceId],
			DocumentName='AWS run shell-script',
			Comment="Performed by lambda function",
			Parameters={'commands':[commandLine]}
		)

	print(response)

"""
Note: This code is only supported for Linux Destors!
"""
