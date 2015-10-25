from flask import Flask, jsonify
from scraper import *
import pdb
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/query/<querystring>")
def query(querystring):
    page_infos = {'results': run_subqueries(querystring)}
    # pdb.set_trace()
    return jsonify(**page_infos)

if __name__ == "__main__":
    app.run(debug = True)