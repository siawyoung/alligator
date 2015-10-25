import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import urllib

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def make_summarizer_request(url):
    r = requests.get("https://joanfihu-article-analysis-v1.p.mashape.com/link?entity_description=False&link=" + urllib.quote(url), headers = {
            "X-Mashape-Key": os.environ.get('MASHAPE_SUMMARIZER_KEY'),
            "Accept": "application/json" })

    return r.json()

def get_summary(url):
    return make_summarizer_request(url)['summary'] # returns a list of important sentences