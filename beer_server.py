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
import urllib2
import urllib
from bs4 import BeautifulSoup
import json

### INITIALIZE ###

app = Flask(__name__)
search_base = "https://www.googleapis.com/customsearch/v1element?"
params = {
  'key':'AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY',
  'hl':'en',
  'prettyPrint':'true',
  'cx':'005327738776847734170:u5pemqi5fnk'
} # add 'num' and 'q'

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

def get_soup(url):
  html = urllib2.urlopen(url).read()
  return BeautifulSoup(html)

def get_search_json(query, num):
  params_new = params
  params_new['num'] = num
  params_new['q'] = query
  return json.loads(urllib2.urlopen(search_base + urllib.urlencode(params_new)).read())['results']

### SERVE SEARCH ###

@app.route("/search", methods=['GET', 'POST'])
@jsonp
def search():
  # results dict
  res = {}
  # get search query & max results
  query = request.values.get('q', '')
  num = request.values.get('num', '5')
  # get results for query
  r = get_search_json(query, num)
  # iterate through items, add as appropriate
  i = 0
  for item in r:
    if not ('url' in item and 'richSnippet' in item and 'thumbnail' in item['richSnippet']): continue
    # build a new beer item with relevant infos
    beer = {}
    beer['name'] = item['richSnippet']['product']['name']
    beer['thumbnail'] = item['richSnippet']['thumbnail']['src']
    beer['url'] = item['url']
    # get some more info by scraping the beer page
    soup = get_soup(item['url'])
    scores = soup.find_all('span', attrs={'class':'BAscore_big'})
    info_box = soup.find_all('td')
    data = info_box[6].renderContents().split("ABV")[1]
    # add new data to beer structure
    beer['ba_score'] = scores[0].renderContents()
    beer['bros_score'] = scores[1].renderContents()
    beer['style'] = BeautifulSoup(data).find_all("b")[0].renderContents()
    beer['abv'] = data.decode("utf8").split("|")[1].split("%")[0].strip() + "%"
    # add it, keep this orderly
    res[i] = beer
    i += 1
  # present our findings
  return jsonify(res)

### MAIN ###

if __name__ == "__main__":
  try:
    print "%s ------------ BEGIN ------------" % get_time_s()
    # run as Tornado server
    app.debug = True
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(2337)
    IOLoop.instance().start()
  except KeyboardInterrupt:
    print "\n%s ------- KILLED BY USER --------" % get_time_s()
