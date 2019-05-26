"""
Below automation through lambda required to implement due to following limitations as mentioned below:
1. A tag can be assigned to only one Snapshot Life Cycle Policy.
2. Snapshot Life Cycle Policy takes an hour to become effective.
3. Using Snapshot Life Cycle Policy you can take snpashot in every 12 or 24 hours.
4. Snapshot Life Cycle Policy will not delete any older snapshot. You have to do it manually.

"""
from datetime import datetime
import boto3

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
	#Fetching all the regions
	regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions'] ]

	for region in regions:
		print('EC2 instances in region {0}: '.format(region))
		ec2 = boto3.resource('ec2', region_name=region)
		#Filtering EC2 instances which all are having tage 'backup' and value 'true'
		instances = ec2.instances.filter(
			Filters=[{'Name':'tag:backup', 'Values':['true']}]
			)

		#Fetching the time stamp
		timestamp = datetime.utcnow().replace(microsecond=0).isoformat()

		#Iterating through all filtered instances
		for i in instances.all():
			#Iterating through attached volumes to an instance
			for v in i.volumes.all():
				desc = "Backup of {0}, volume {1}, created {2}".format(i.id, v.id, timestamp)
				print(desc)
				
				#Creating Snapshot
				snapshot = v.create_snapshot(Description=desc)

				print("Created snapshot: ", snapshot.id)

"""
After code task:
You need to configure Cloudwatch Event rule to trigger the lambda function at a particular time.
"""
