import boto3
ec2_client = boto3.client('ec2')

def handler(event, context):
    #Get list of regions
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    #Iterate over each Region
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        print("Region: ", region)
        #Get only running instances
        instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values':['running']}]
        )

        #Stop the instances
        for instance in instances:
            instance.stop()
            print('Stopped instance: ', instance.id)

"""
Note: Need to configure cloudwatch event rule to trigger the lambda function at a particular time.
"""
