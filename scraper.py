import os
from os.path import join, dirname
from dotenv import load_dotenv
import urllib2
import oauth2 as oauth
import time
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

YAHOO_URL             = "http://yboss.yahooapis.com/ysearch/web"
OAUTH_CONSUMER_KEY    = os.environ.get('YAHOO_BOSS_OAUTH_CONSUMER_KEY')
OAUTH_CONSUMER_SECRET = os.environ.get('YAHOO_BOSS_OAUTH_CONSUMER_SECRET')

def oauth_request(url, params, method="GET"):
    params['oauth_version'] = "1.0" #,
    params['oauth_nonce'] = oauth.generate_nonce() #,
    params['oauth_timestamp'] = int(time.time())
    consumer = oauth.Consumer(key=OAUTH_CONSUMER_KEY, secret=OAUTH_CONSUMER_SECRET)
    params['oauth_consumer_key'] = consumer.key
    req = oauth.Request(method=method, url=YAHOO_URL, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    return req

def yahoo_boss_request(query, count):
    req = oauth_request(YAHOO_URL, params = {'q': query, 'count': count, 'abstract': 'long'})
    req['q']   = req['q'].encode('utf8')
    req_url    = req.to_url().replace('+', '%20')
    raw_result = urllib2.urlopen(req_url).read()
    return json.loads(raw_result)['bossresponse']['web']['results']


def extract_info_from_yahoo_response(payload):
    return [ {'title': result['title'], 'url': result['url'], 'abstract': result['abstract']} for result in payload ]


q = yahoo_boss_request("python", 20)
urls = extract_info_from_yahoo_response(q)