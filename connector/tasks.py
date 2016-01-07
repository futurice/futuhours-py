from __future__ import absolute_import

from celery import group, Task
from connector.celery import app

from connector.planmill import PlanMill

import os
import boto3
import hashlib

def aws_config():
    return dict(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID',''),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY',''),
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_session_token=os.getenv('AWS_SESSION_TOKEN',''),)

def json_to_csv(res):
    CSV_ENCODING = os.getenv('CSV_ENCODING', 'iso-8859-1')
    CSV_QUOTE = os.getenv('CSV_QUOTE', '"').encode(CSV_ENCODING)
    CSV_SEPARATOR = os.getenv('CSV_SEPARATOR', ',').encode(CSV_ENCODING)
    rows = []
    def maybe_quote(s):
        if s is None:
            res = ""
        else:
            res = u'{}{}{}'.format(CSV_QUOTE, s, CSV_QUOTE) if (CSV_SEPARATOR in s) else s
        if CSV_ENCODING in ['iso-8859-1',] and isinstance(type(res), str):
            return res
        else:
            return res.encode(CSV_ENCODING, 'ignore')
    # head
    rows.append(CSV_SEPARATOR.join([maybe_quote(k['name']) for k in rep['meta']['columns']]))
    # data
    for row in res['data']:
        clean_row = []
        for k in row:
            clean_row.append(maybe_quote(k))
        rows.append(CSV_SEPARATOR.join(clean_row))
    return "\r\n".join(rows)

@app.task
def fetch_report(report):
    pc = PlanMill(api_server=os.getenv('PLANMILL_URI'),
            api_user_id=os.getenv('PLANMILL_USER'),
            api_auth_key=os.getenv('PLANMILL_TOKEN'),)
    params = report['params'] or {}
    res = pc.get_report(report['name'], **params)

    # convert json to csv
    text = json_to_csv(res)

    # store in S3
    name = hashlib.sha256("{}{}".format(report['name'], os.getenv('SALT'))).hexdigest()
    save_to_s3(data=text, name=name, bucket=os.getenv('S3_BUCKET'))

def get_configured_reports():
    """ name&param=y,param=z<>... """
    reports = []
    for report in filter(None, os.getenv('PLANMILL_REPORTS').split('<>')):
        data = report.split('&')
        reports.append({'name': data[0],
                        'params': filter(None, data[1].split(','))})
    return reports

@app.task
def fetch_reports():
    for report in get_configured_reports():
        fetch_report.delay(report)

@app.task
def save_to_s3(data, name, bucket):
    session = boto3.session.Session(**aws_config())
    s3 = session.client('s3')
    s3.put_object(Body=data, Key=name, Bucket=bucket, GrantRead='uri=http://acs.amazonaws.com/groups/global/AllUsers')

