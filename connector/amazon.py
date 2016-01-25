import os

def aws_config():
    return dict(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID',''),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY',''),
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_session_token=os.getenv('AWS_SESSION_TOKEN',''),)
