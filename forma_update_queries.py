import sys
import os

import requests

APIKEY = os.environ['CARTODB_API_KEY']
URL = 'http://wri-01.cartodb.com/api/v2/sql'


def successful(response):
    count = 'rows' in response.json().keys()
    status = response.status_code == 200
    no_error = 'error' not in response.content

    if count and status and no_error:
        return True
    else:
        return False


def run_query(url, query, api_key):
    if query.startswith('#') or query == '':
        print 'Skipping "%s"' % query
        return None

    payload = dict(api_key=api_key, q=query)
    attempts = 0

    print "Executing %s" % query

    r = requests.get(url, params=payload)

    while not successful(r) and attempts < 5:
        print 'Failed attempt: %s' % r.content
        print 'Retry #%i' % attempts
        r = requests.get(url, params=payload)
        attempts += 1
    if successful(r):
        print "Success: %s" % r.content
        return r
    else:
        raise Exception("Could not run %s" % query)


def main(path):
    for query in open(path, 'r'):
        run_query(URL, query.strip(), APIKEY)


if __name__ == '__main__':
    path = sys.argv[1]
    main(path)
