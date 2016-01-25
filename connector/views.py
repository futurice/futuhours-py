from django.http import HttpResponse

import boto3
from connector.amazon import aws_config

def s3_get(opts={}):
    session = boto3.session.Session(**aws_config())
    s3 = session.client('s3')
    return s3.get_object(**opts)

def report(request, name):
    ct = request.GET.get('ct', None) # optional ContentType override
    res = s3_get(opts=dict(Key=name, Bucket=os.getenv('S3_BUCKET')))
    return HttpResponse(res['Body'].read(), content_type=ct or res['ContentType'])
