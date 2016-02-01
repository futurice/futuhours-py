import os
import hashlib

def to_hash(key):
    return hashlib.sha256("{}{}".format(key, os.getenv('SALT'))).hexdigest()

FMT = {'name':0,'params':1,'url':2,'content_type':3}
def fmt(data, key, default=''):
    try:
        r = data[FMT[key]]
    except:
        r = default
    return r

def get_configured_reports(separator='<>', sepsec='|'):
    """ name|params|url|ctSEPARATOR... """
    reports = []
    for report in filter(None, os.getenv('PLANMILL_REPORTS').split(separator)):
        sections = report.split(sepsec)
        params = filter(None, fmt(sections, 'params').split(','))
        reports.append({'name': fmt(sections, 'name'),
                        'params': [tuple(params)] if params else [],
                        'url': fmt(sections, 'url'),
                        'content_type': fmt(sections, 'content_type', default='text/csv'),
                        })
    return reports
