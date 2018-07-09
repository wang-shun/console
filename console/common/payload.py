# coding=utf-8
import json
from django.conf import settings

__author__ = 'chenlei'


class Payload(object):
    def __init__(self, request, action, **queries):
        self.request = request
        self.action = action
        self.api_version = settings.API_VERSION
        self.queries = queries

    def __setitem__(self, key, val):
        self.queries[key] = val

    def __getitem__(self, key):
        return self.queries[key]

    def __contains__(self, key):
        return key in self.queries

    def dumps(self, json_serialize=False):
        payload = self.queries
        payload.update({"version": self.api_version})
        payload.update(
            {
                "owner": self.request.owner,
                "zone": self.request.zone,
                "action": self.action,
                "account_channel": self.request.session.get('login_channel',
                                                            'guest')
            }
        )
        if json_serialize:
            return json.dumps(payload)
        return payload
