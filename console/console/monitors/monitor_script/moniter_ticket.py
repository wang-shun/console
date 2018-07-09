#!/usr/bin/env python
# coding=utf-8
import requests
import httplib
import urllib
import urllib2
import json
import sys
if __name__ == "__main__":
    content = sys.argv[3]
    title = sys.argv[2]

    if title == '1':
        exit(0)
    values = {
        'action': 'AddTicketMonitor',
        'ticket_type': 1,
        'owner': 'system_image',
        'content': content
    }
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.292))'
    headers = {"Content-Type": "application/json", 'User-Agent' : user_agent}
    data = urllib.urlencode(values)
    httpClient = httplib.HTTPConnection("127.0.0.1:8000")
    httpClient.request("POST", "/finance/api/", json.dumps(values), headers)
    response = httpClient.getresponse()
    if httpClient:
        httpClient.close()

