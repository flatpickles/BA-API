###### BEER?!?!?! ######

### IMPORT ###

# let's get some server stuff
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import Flask, request, redirect, g, jsonify

# and some more stuff
from functools import wraps
from time import gmtime, strftime


### INITIALIZE ###

app = Flask(__name__)


### HELPFUL SHIT ###

# allow jsonP
# mostly via https://gist.github.com/1094140
def jsonp(f):
  global app
  @wraps(f)
  def decorated_function(*args, **kwargs):
    callback = request.args.get('callback', False)
    if callback:
      content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
      return app.response_class(content, mimetype='application/javascript')
    else:
      return f(*args, **kwargs)
  return decorated_function

def get_time_s():
  return strftime("[%m/%d %H:%M]", gmtime())


### SERVE STUFF ###

@app.route("/search", methods=['GET', 'POST'])
@jsonp
def search():
  return jsonify({'test' : 6})


### MAIN ###

if __name__ == "__main__":
  try:
    print "%s ------------ BEGIN ------------" % get_time_s()
    # run as Tornado server
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(2337)
    IOLoop.instance().start()
  except KeyboardInterrupt:
    print "\n%s ------- KILLED BY USER --------" % get_time_s()
