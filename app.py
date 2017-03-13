#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "chatbotFoodService":
		  return {}
    print(req.get("result").get("action"))
    baseurl = "http://alexav2.cloudhub.io/alexa/products?"
    print(req.get("result").get("action"))
    bww_query = makebwwQuery(req)
    print("bww_query :- "+ bww_query)
    if bww_query is None:
        return {}
    bww_url = baseurl + bww_query
    print(bww_url)
    result = urlopen(bww_url).read()
    print("Result :- "+result)
    try:
      data = json.loads(result)
    except ValueError as e:
      print(e)
    
    print(" data :-"+data)
    res = makeWebhookResult(data)
    return res


def makebwwQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    product = parameters.get("product") 
    quantity= parameters.get("quantity")
    productType= parameters.get("type")
    return "productName="+product+"&quantityName="+quantity+"&productType="+productType 
    


def makeWebhookResult(data):
    listPrice = data.get('listPrice')
    print("listPrice:- "+ listPrice)
    if listPrice is None:
        return {}

    speech = "your amount for current order is " + listPrice
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-chatFoodOrder-webhook-master"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
