# import os
# from flask import Flask
# try:
#   from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
#   from SocketServer import TCPServer as Server
# except ImportError:
#   from http.server import SimpleHTTPRequestHandler as Handler
#   from http.server import HTTPServer as Server

# # Read port selected by the cloud for our application
# PORT = int(os.getenv('PORT', 8000))
# # Change current directory to avoid exposure of control files
# os.chdir('static')

# httpd = Server(("", PORT), Handler)
# try:
#   print("Start serving at port %i" % PORT)
#   httpd.serve_forever()
# except KeyboardInterrupt:
#   pass
# httpd.server_close()

import os
from flask import Flask, jsonify
from flask.ext.cors import CORS
from scraper import *
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/query/<querystring>/<time>")
def query(querystring, time):
    page_infos = {'results': run_subqueries(querystring, int(time))}
    # pdb.set_trace()
    return jsonify(**page_infos)

# port = os.getenv('VCAP_APP_PORT', '5000')
port = int(os.getenv('PORT', 8000))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))