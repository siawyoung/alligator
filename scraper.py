from __future__ import division
import os
from os.path import join, dirname
from dotenv import load_dotenv
import urllib2
import requests
import oauth2 as oauth
import time
import json
import re
import pdb
import grequests
import itertools
import isodate
from bs4 import BeautifulSoup
from collections import Counter

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

YAHOO_URL             = "http://yboss.yahooapis.com/ysearch/web"
OAUTH_CONSUMER_KEY    = "dj0yJmk9dUpYVGZCd1hnQWVVJmQ9WVdrOVJrMUdkV2R1TlRBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD00MQ--"
OAUTH_CONSUMER_SECRET = "dd7ad54a4cbfec931eb36bc6ee342170dac5e156"

def oauth_request(url, params, method="GET"):
    params['oauth_version'] = "1.0"
    params['oauth_nonce'] = oauth.generate_nonce()
    params['oauth_timestamp'] = int(time.time())
    consumer = oauth.Consumer(key=OAUTH_CONSUMER_KEY, secret=OAUTH_CONSUMER_SECRET)
    params['oauth_consumer_key'] = consumer.key
    req = oauth.Request(method=method, url=YAHOO_URL, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    return req

# def get_html_body(url):
#     try:
#         r = requests.get(url, verify = False).text
#     except:
#         r = None
#     return r

def yahoo_boss_request(query, count):
    req = oauth_request(YAHOO_URL, params = {'q': query, 'count': count, 'abstract': 'long'})
    req['q']   = req['q'].encode('utf8')
    req_url    = req.to_url().replace('+', '%20')
    return req_url
    # raw_result = urllib2.urlopen(req_url).read()
    # return json.loads(raw_result)['bossresponse']['web']['results']

def parallel_boss_requests(query, count, subqueries):
    urls = [ yahoo_boss_request(query + ' ' + subquery, count) for subquery in subqueries ]
    rs = (grequests.get(u) for u in urls)
    return grequests.map(rs)
    


def extract_info_from_yahoo_response(payload):
    parsed_payload = [x.json()['bossresponse']['web']['results'] for x in payload]
    return [ {'title': result['title'], 'url': result['url'], 'abstract': result['abstract']} for result in list(itertools.chain(*parsed_payload)) ]

def extract_span_elements_from_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return ' '.join([x.text.strip() for x in soup.find_all('p')])

def time_taken(res):

    if 'youtube.com' in res.url:
        return getDuration(res.url)
    else:
        return int(len(extract_span_elements_from_html(res.text).split()) / 200)

def compare_ignore_protocol(x, y):
    asd = x.replace('http://', '').replace('https://', '')
    asd2 = y.replace('http://', '').replace('https://', '')
    return asd == asd2

def getDuration(url):
    videoId = url.split('v=')[1][:11]
    apiUrl = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id='+videoId+'+&key=AIzaSyA8tK5-oxQRlmJBD8I_PLRGoR9IAg29EJU'
    response = requests.get(apiUrl).json()

    encodedDuration = response['items'][0]['contentDetails']['duration']
    duration = isodate.parse_duration(encodedDuration)
    minutes = int(duration.total_seconds()/60)
    return minutes

def run_subqueries(query, time):
    list_of_urls      = []
    list_of_infos     = []
    SUBQUERIES = ['tutorial', 'how to', 'beginner', 'dummies', 'intro', 'best', 'tutorials', 'learn', 'guide']
    
    page_infos = extract_info_from_yahoo_response(parallel_boss_requests(query, 50, SUBQUERIES))
    list_of_urls += [ x['url'] for x in page_infos ]
    top_urls = Counter(list_of_urls).most_common(12)
    rs = (grequests.get(u) for u, _ in top_urls)
    response_objects = grequests.map(rs)
    not_exceeded_top_infos = []
    exceeded_top_infos = []
    for response in response_objects:
        if response == None:
            continue
        filtered = filter(lambda x: compare_ignore_protocol(x['url'], response.url), page_infos)

        if len(filtered) == 0:
            continue

        top_info = filtered[0]
        if response.status_code == 200:

            time_needed = time_taken(response)

            top_info['time_taken'] = time_needed
            if time_needed > time:
                top_info['exceeded'] = (time_needed > time)
                exceeded_top_infos.append(top_info)
            elif time_needed != 0:
                top_info['exceeded'] = (time_needed > time)
                not_exceeded_top_infos.append(top_info)


    return not_exceeded_top_infos + exceeded_top_infos