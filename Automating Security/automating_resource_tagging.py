"""
to automate the tagging of EC2 instances and their corresponding resources using a Lambda function with CloudTrail and CloudWatch. 
The function will ensure that users can work only on those resources that they have created based on resource tags. 
This is enforced via an IAM policy.
"""

import json, boto3

ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
	print('Event: ' + str(event))
	print(json.dumps(event))

	#Containe all the identifiers of EC2 resource found in given event.
	#IDs could be EC2 instance, EBS volume, ENI, EBS Snapshot, or AMIs
	id = []

	try:
		region = event['region']
		details = event['detail']
		eventname = detail['eventName']
		arn = detail['userIdentity']['arn']
		principal = details['userIdentity']['principalId']
		user_type = detail['userIdentity']['type']

		if user_type == 'IAMUser':
			user = detail['userIdentity']['userName']
		else:
			#Cloud be web federated user or assumed role
			user = principal.split(': ')[1]

		print("arn: " + arn)
		print("principalId: " + principal)
		print("region: " + region)
		print("eventName: " + eventname)
		print("detail: " + str(detail))
		print("user: " + user)

		#Handling varous events
		if eventname == 'CreateVolume':
			ids.append(detail['responseElements']['volumeId'])
			print(ids)
		elif eventname == 'RunInstances':
			items = detail['responseElements']['instanceSet']['items']
			for item in items:
				ids.append(item['instanceId'])
			print(ids)
			print('number of instances are : ' + str(len(ids)))

			base = ec2.instances.filter(instanceIds=ids)

			#Loop through the instances
			for instance in base:
				for vol in instance.volumes.all():
					ids.append(vol.id)
				for eni in instance.network_interfaces:
					ids.append(eni.id)
		elif eventname == 'CreateImage':
			ids.append(detail['responseElements']['imageId'])
			print(ids)
		elif eventname == 'CreateSnapshot':
			ids.append(detail['responseElements']['snapshotId'])
			print(ids)
		else:
			print('Not supported action.')


		if ids:
			for resourceid in ids:
				print('Tagging resource: ' + resourceid)
				ec2.create_tags(Resources=ids, Tag=[
						{'Key': 'Owner', 'Value': user},
						{'Key': 'PrincipalId', 'Value': principal}
					])

		print("Done tagging.")

		return True
	except Exception as e:
		print('Something went wrong: ' + str(e))
		return False

