from __future__ import absolute_import

from celery import group, Task
from connector.celery import app

from connector.planmill import PlanMill

import os
import boto3
import hashlib

from connector.amazon import aws_config

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

    # store
    name = hashlib.sha256("{}{}".format(report['name'], os.getenv('SALT'))).hexdigest()
    s3_put(opts=dict(Body=text, Key=name, Bucket=os.getenv('S3_BUCKET'), ContentType='text/csv'))

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
def s3_put(opts={}):
    session = boto3.session.Session(**aws_config())
    s3 = session.client('s3')

    opts.setdefault('GrantRead', 'uri=http://acs.amazonaws.com/groups/global/AllUsers')
    opts.setdefault('ServerSideEncryption', 'AES256')
    s3.put_object(**opts)
