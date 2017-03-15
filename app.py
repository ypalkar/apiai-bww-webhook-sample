#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import traceback

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(req.get("result").get("action"))
    print(json.dumps(req, indent=4))

    if req.get("result").get("action") =="chatbotFoodService":
      print("Inside chatbotFoodService")
      res = processRequest(req)
    else:
      print("Inside promo")
      res= processPromotionRequest(req)
    print("before json dumps " + res)
    res = json.dumps(res, indent=4)
    print("After json dumps" + res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processPromotionRequest(req):
  print(req.get("result").get("action"))
  if req.get("result").get("action") != "promotionService":
		      return {}
  baseurl = "http://ec2-54-219-170-150.us-west-1.compute.amazonaws.com:8080/alexa/getStorePromotions?storeId=4829CA"
  print(baseurl)
  result = urlopen(baseurl).read()
  print("promotion recieved")
  res = makePromoWebhookResult(result)
    
def processRequest(req):
    print(req.get("result").get("action"))
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
    res = makeWebhookResult(result)
    return res

    return res

def makebwwQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    product = parameters.get("product") 
    quantity= parameters.get("quantity")
    productType= parameters.get("type")
    return "productName="+product+"&quantityName="+quantity+"&productType="+productType 
    


def makeWebhookResult(result):
    print("Inside makeWebhookResult")
    try:
      resp = json.loads(result)
      #print("resp is  " + resp)
      listPrice=resp[0]['listPrice']
      print("listPrice is  " + listPrice)
      speech = "your amount for current order is " + listPrice
    except Exception as e: print(e)
	 
    if resp is None:
        return {}

    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-chatFoodOrder-webhook-master"
    }


	
def makePromoWebhookResult(result):
    print("Inside makePromoWebhookResult")
    try:
      resp = json.loads(result)
      speech = "Here are our current promotions. Our first promotion is"+ resp[0]['promoName'] + resp[0]['promoDescr'] +"Our second promotion is" + resp[0]['promoName'] + resp[0]['promoDescr'] +". Please visit your nearest restaurant for more information."
    
    except Exception as e: print(e)
    
    
    print("Speech is "+speech)
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
