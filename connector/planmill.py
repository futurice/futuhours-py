# coding=UTF-8
import json
import base64
import hmac
import calendar
import random
import time
import hashlib
import requests
"""
https://online.planmill.com/pmtrial/schemas/v1_5/index.html
- API key: https://online.planmill.com/pmtrial/schemas/v1_5/authexample.html
"""

class PlanMill(object):
    def __init__(self, api_server, api_user_id, api_auth_key):
        self.api_server = api_server
        self.api_user_id = api_user_id
        self.api_auth_key = api_auth_key
        self.response = None

    def generate_nonce(self):
        """
        Generate a new 'nonce' for the HTTP Authentication Header.
        """
        # Apparently the 'nonce' can be reused after a few minutes.
        # Generate 8 characters:
        # second minute hour day month (1 char each) + 3 random chars
        b62digits = ''
        for low, high in [('0', '9'), ('a', 'z'), ('A', 'Z')]:
            for i in range(ord(low), ord(high) + 1):
                b62digits += chr(i)

        nonce = ''
        t = time.gmtime()
        for i in (t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon):
            # tm_sec <= 61, still a valid index
            nonce += b62digits[i]
        for i in range(3):
            nonce += random.choice(b62digits)

        return nonce

    def get_auth_header(self):
        """
        Compute a Planmill Authentication HTTP Header.

        According to the JavaScript code on this page:
        https://online.planmill.com/pmtrial/schemas/v1_5/authexample.html
        """
        nonce = self.generate_nonce()
        tstamp = calendar.timegm(time.gmtime())
        msg = '{}{}{}'.format(self.api_user_id, nonce, tstamp)

        h = hmac.new(self.api_auth_key, msg, digestmod=hashlib.sha256)
        signature = base64.b64encode(h.digest())

        result = 'user:{};nonce:{};timestamp:{};signature:{}'.format(
                self.api_user_id, nonce, tstamp, signature)
        return result
        
    def make_request(self, path=None, verb='get', data={}, params={}, fmt='json'):
        """
        Make the request, parse the response as JSON and return it.

        On errors, returns a dictionary holding error information.
        """
        url = self.api_server + path
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'x-PlanMill-Auth': self.get_auth_header(),
        }
        verb = verb.lower()

        request = getattr(requests, verb)
        self.response = request(url, data=json.dumps(data) if data else {}, headers=headers, params=params)
        if fmt == 'json':
            if self.response.status_code in [204]:
                return ''
            elif str(self.response.status_code).startswith("2"):
                # json.loads used, as encoding not specified to requests-library
                return json.loads(self.response.content)
            else:
                return {'error': self.response.json()}

    def get_users(self, **kwargs):
        attrs = {'rowcount': 0}
        attrs.update(**kwargs)
        return self.make_request('users', params=attrs)

    def get_report(self, report, params={}, **kwargs):
        return {'data': self.make_request("reports/%s" % (report), params=params), 'meta': self.make_request("reports/%s/meta" % (report))}

    def get_reports(self):
        return self.make_request("reports")

    def get_timereports(self, params={}, **kwargs):
        return self.make_request('timereports', params=params)

    def get_timereport(self, timereport_id):
        return self.make_request('timereports/{}'.format(timereport_id))

    def post_timereport(self, data):
        return self.make_request('timereports', data=data, verb='post')

    def update_timereport(self, data):
        return self.make_request('timereports/{}', data=data, verb='post')

    def get_timereport_meta(self):
        return self.make_request('timereports/meta')

    def delete_timereport(self, id):
        return self.make_request('timereports/{}'.format(id), verb='delete')

    def get_teams(self, params={}, **kwargs):
        return self.make_request('teams', params=params)

    def get_team(self, id):
        return self.make_request('teams/{}'.format(id))

    def get_user(self, id):
        return self.make_request('users/{}'.format(id))

