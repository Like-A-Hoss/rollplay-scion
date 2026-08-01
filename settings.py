import os
from dotenv import load_dotenv

load_dotenv()


""" def get_param(name, default=None):
    value = os.getenv(name)
    if value:
        return value

    try:
        import boto3

        ssm = boto3.client('ssm', region_name='us-east-2')
        return ssm.get_parameter(
            Name=f'/rollplay-scion/{name}',
            WithDecryption=True
        )['Parameter']['Value']
    except Exception:
        if default is not None:
            return default
        raise


# Load config from .env locally, with AWS Parameter Store as a fallback.
SECRET_KEY = get_param('SECRET_KEY', '')
TESTING_SERVER = get_param('TESTING_SERVER', '') """
SECRET_KEY = os.getenv('SECRET_KEY', '')
TESTING_SERVER = os.getenv('TESTING_SERVER', '')