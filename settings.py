import boto3

ssm = boto3.client('ssm', region_name='us-east-2')

def get_parameter(name):
    return ssm.get_parameter(
        Name=f"/rollplay-scion/{name}",
        WithDecryption=True
    )['Parameter']['Value']
# Fetch bot token
SECRET_KEY = get_parameter('SECRET_KEY')

# Fetch test server ID
TESTING_SERVER = get_parameter('TESTING_SERVER')