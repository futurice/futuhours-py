from __future__ import absolute_import

from celery import group, Task
from connector.celery import app

from connector.planmill import PlanMill

import os
import boto3
import requests

from connector.amazon import aws_config
from connector.reports import to_hash, get_configured_reports

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
    rows.append(CSV_SEPARATOR.join([maybe_quote(k['name']) for k in res['meta']['columns']]))
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
    kw = {}
    res = pc.get_report(report['name'], params=params, **kw)

    # convert json to csv
    text = json_to_csv(res)

    # store
    s3_put(opts=dict(Body=text, Key=to_hash(report['name']), Bucket=os.getenv('S3_BUCKET'), ContentType=report['content_type']),
            encrypt=False)
@app.task
def download_report(report):
    res = requests.get(report['url'], timeout=600)
    if res.status_code==200:
        s3_put(opts=dict(Body=res.content,
                        Key=to_hash(report['name']),
                        Bucket=os.getenv('S3_BUCKET'),
                        ContentType=report['content_type']),
                        encrypt=False)

@app.task
def fetch_reports():
    for report in get_configured_reports():
        if report.get('url'):
            download_report.delay(report)
        else:
            fetch_report.delay(report)

@app.task
def s3_put(opts={}, encrypt=False):
    session = boto3.session.Session(**aws_config())
    s3 = session.client('s3')

    opts.setdefault('GrantRead', 'uri=http://acs.amazonaws.com/groups/global/AllUsers')
    if encrypt:
        opts.setdefault('ServerSideEncryption', 'AES256')
    s3.put_object(**opts)
