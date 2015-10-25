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

def get_html_body(url):
    try:
        r = requests.get(url, verify = False).text
    except:
        r = None
    return r

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
    return [ {'title': result[0]['title'], 'url': result[0]['url'], 'abstract': result[0]['abstract']} for result in parsed_payload ]

def extract_html_from_url(url):
    pass
    # x = []
    # for url in urls:
    #     y = get_html_body(url)
    #     if y:
    #         x.append(extract_span_elements_from_html(y))
    # return x
    # return [ extract_span_elements_from_html(get_html_body(url)) for url in urls ]

def extract_span_elements_from_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return ' '.join([x.text.strip() for x in soup.find_all('p')])
    # pdb.set_trace()
    # [s.extract() for s in soup('script')] # remove script tags
    # word_list = [re.sub(r'\W+', ' ', text) for text in soup.stripped_strings] # remove non alphanuerical
    # return ' '.join(filter(lambda x : len(x) > 2, [ word.strip() for word in word_list ] )) # remove whitespace and too short words, then concatenate

def time_taken(words_string):
    time = int(len(words_string.split()) / 200)
    return time if time != 0 else 1

def run_subqueries(query):
    list_of_urls      = []
    list_of_infos     = []
    SUBQUERIES = ['tutorial', 'how to', 'beginner', 'dummies', 'intro']
    # for subquery in SUBQUERIES:
        # page_infos = extract_info_from_yahoo_response(yahoo_boss_request(query + ' ' + subquery, 50))
        # page_infos = extract_info_from_yahoo_response(parallel_boss_requests(query, 50, subquery))
        # list_of_urls += [ x['url'] for x in page_infos ]
        # list_of_infos += page_infos

    page_infos = extract_info_from_yahoo_response(parallel_boss_requests(query, 50, SUBQUERIES))
    list_of_urls += [ x['url'] for x in page_infos ]
    # list_of_infos += page_infos
    top_urls = Counter(list_of_urls).most_common(50)

    top_infos = []
    for top_url, _ in top_urls:
        top_info = filter(lambda x: x['url'] == top_url, page_infos)[0]
        html = get_html_body(top_info['url'])
        if html:
            top_info['time_taken'] = time_taken(extract_span_elements_from_html(html)) 
        else:
            top_info['time_taken'] = 'unknown'

        top_infos.append(top_info)
        if len(top_infos) > 10:
            break

    return top_infos

# def check_video_presence_on_page(url):
#     soup = BeautifulSoup(get_html_body(url), 'html.parser')
#     return soup

# r = check_video_presence_on_page('https://sitedart.net/make-my-website/web-presence-builder')
# q = yahoo_boss_request("explain rails", 2)
# page_infos = extract_info_from_yahoo_response(q)
# htmls = extract_html_from_urls([x['url'] for x in page_infos])
