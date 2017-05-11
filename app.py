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
    elif req.get("result").get("action") =="myloyalityService":
      print("Inside myloyalityService")
      res = processLoyaltyRequest(req)
    elif req.get("result").get("action") =="mydrinksService":
      print("Inside myloyalityService")
      res = processDrinksRequest(req)
    else:
      print("Inside promo")
      res= processPromotionRequest(req)
    
    res = json.dumps(res, indent=4)
    print("After json dumps" + res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/getRegisteredUsers', methods=['GET'])
def getRegisteredUsers():
    
	baseurl = "http://ec2-54-219-170-150.us-west-1.compute.amazonaws.com:8084/virginvoyage/getRegisteredUsers"
	result = urlopen(baseurl).read()
	print("Executed Rest Call"+result);
	r = make_response(result)
	r.headers['Content-Type'] = 'application/json'
	return r

	
	
def processDrinksRequest(req):
  print(req.get("result").get("action"))
  if req.get("result").get("action") != "mydrinksService":
		      return {}
  baseurl = "http://ec2-54-219-170-150.us-west-1.compute.amazonaws.com:8080/alexa/products/beverages/tap?beverageType=Tap"
  print(baseurl)
  result = urlopen(baseurl).read()
  print("drinks recieved")
  res = makeDrinkWebhookResult(result)
  return res

def processPromotionRequest(req):
  print(req.get("result").get("action"))
  if req.get("result").get("action") != "promotionService":
		      return {}
  baseurl = "http://ec2-54-219-170-150.us-west-1.compute.amazonaws.com:8080/alexa/getStorePromotions?storeId=4829CA"
  print(baseurl)
  result = urlopen(baseurl).read()
  print("promotion recieved")
  res = makePromoWebhookResult(result)
  return res
    
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
	
def processLoyaltyRequest(req):
    print(req.get("result").get("action"))
    if req.get("result").get("action") != "myloyalityService":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
	
    baseurl = "http://ec2-54-219-170-150.us-west-1.compute.amazonaws.com:8080/alexa/mcdonalds/memberPoints?memberID="+parameters.get("memberid")
    print("baseURL :- " + baseurl)
    result = urlopen(baseurl).read()
    res = makeLoyalWebhookResult(result)
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
      speech = "Here are our current promotions. Our first promotion is "+ resp[0]['promoName'] +". " +resp[0]['promoDescr'] +"\n Our second promotion is " + resp[1]['promoName'] + ". "+resp[1]['promoDescr'] +". \n Please visit your nearest restaurant for more information."
    
    except Exception as e: print(e)
    
    
    print("Speech is "+speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-chatFoodOrder-webhook-master"
    }
	
def makeLoyalWebhookResult(result):
    print("Inside makeLoyalWebhookResult")
    try:
      resp = json.loads(result)
      speech = "You currently have"+ resp[0]['loyaltyPoints'] +" loyalty points. \n Thanks for being a loyal member of our family. To redeem points, please visit any participating restaurant."
    
    except Exception as e: print(e)
    
    
    print("Speech is "+speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-chatFoodOrder-webhook-master"
    }

def makeDrinkWebhookResult(result):
    print("Inside makeDrinkWebhookResult")
    try:
      resp = json.loads(result)
      speech = ""
    
    except Exception as e: print(e)
    for item in resp:
      if item['beverageDesc'] is None:
        print("")
      else:
        speech=speech +item['beverageName']+ "       " + item['beverageDesc'] +" \n"

    
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
