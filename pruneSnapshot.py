"""
Below automation through lambda required to implement due to following limitations as mentioned below:
1. A tag can be assigned to only one Snapshot Life Cycle Policy.
2. Snapshot Life Cycle Policy takes an hour to become effective.
3. Using Snapshot Life Cycle Policy you can take snpashot in every 12 or 24 hours.
4. Snapshot Life Cycle Policy will not delete any older snapshot. You have to do it manually.

"""
import boto3

def lambda_handler(event, context):
	#Fetching the account id
	account_id = boto3.client('sts').get_caller_identity().get('Account')
	ec2_client = boto3.client('ec2')

	#Fetching all the regions
	regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions'] ]
	
	for region in regions:
		print('Region: ',region)
		ec2 = boto3.client('ec2', region_name = region)

		response = ec2.describe_snapshots(OwnerIds=[account_id])
		snapshots = response["Snapshots"]

		#Logic to keep most 3 recent snapshot
		#Sort snapshot in ascending order by date.
		snapshots.sort(key=lambda x:x["StartTime"])

		#Remove snapshots which wwe want to keep (i.e 3 most recent)
		snapshots = snapshots[:-3]

		#Looping thorugh snapshot to grabe the id and to delete it.
		for snapshot in snapshots:
			id = snapshot['SnapshotId']
			try:
				print('Deleting snapshot: ', id)
				ec2.delete_snapshot(SnapshotId=id)
			except Exception as e:
				if 'InvalidSnapshot.InUse' in e.message:
					print('Sanpshot {} is in use, skipping it.'. format(id))
					continue
          
          
"""
Post code task you need configure CloudWatch event rule. 
"""
