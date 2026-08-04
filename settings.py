import boto3

ssm = boto3.client('ssm', region_name='us-east-2')

def get_parameter(name):
    return ssm.get_parameter(
        Name=f"/rollplay-scion/{name}",
        WithDecryption=True
    )['Parameter']['Value']


def get_optional_parameter(name, default=None):
    try:
        return get_parameter(name)
    except Exception:
        return default
# Fetch bot token
SECRET_KEY = get_parameter('SECRET_KEY')

# Fetch test server ID
TESTING_SERVER = get_parameter('TESTING_SERVER')

# Optional channel ID for reactive defense debug logs.
# Falls back to the testing channel if the SSM parameter is not set.
REACTIVE_DEFENSE_LOG_CHANNEL = get_optional_parameter(
    'REACTIVE_DEFENSE_LOG_CHANNEL',
    default='1001211424615448607'
)