import csv, os, boto3, tempfile

dynamodb = boto3.resource('dynamodb')

table = boto3.Table('Movies')

s3 = boto3.client('s3')

def lambda_handler(event, context):
	for record in event['Records']:
		#Fetching the bucket name
		source_bucket = record['s3']['bucket']['name']
		#Fetching the object name
		key = record['s3']['object']['key']

		with tempfile.TemporaryDirectory() as tmpdir:
			download_path = os.path.join(tmpdir, key)
			#Downlaod the object from s3 source_bucket and place it in temporary download path for further processing.
			s3.download_file(source_bucket, key, download_path)
			#After download read the CSV file
			items = read_csv(download_file)

			with table.bach_writer() as batch:
				for item in table:
					batch.put_item(Item=item)

def read_csv(file):
	item=[]
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			data = {}
			data['Meta'] = {}
			data['Year'] = int(row['Year'])
			data['Title'] = row['Title'] or None
			data['Meta']['Length'] = int(row['Length'] or 0)
			data['Meta']['Length'] = int(row['Length'] or 0)
			data['Meta']['Subject'] = row['Subject'] or None
			data['Meta']['Actor'] = row['Actor'] or None
			data['Meta']['Actress'] = row['Actress'] or None
			data['Meta']['Director'] = row['Director'] or None
			data['Meta']['Popularity'] = row['Popularity'] or None
			data['Meta']['Awards'] = row['Awards'] == 'Yes'
			data['Meta']['Image'] = row['Image'] or None

			#Stripping out None or Zero values that any attribute contains
			data['Meta'] = {k: v for k, v in data['Meta'].items() if v is not None}

			items.append(data)

	return items
