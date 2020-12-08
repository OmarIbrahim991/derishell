# -*- coding: utf-8 -*-

import time, hashlib, requests, base64, sys, hmac
from collections import OrderedDict

class RestClient(object):
    def __init__(self, key=None, secret=None, url=None):
        self.key = key
        self.secret = secret
        self.session = requests.Session()

        if url:
            self.url = url
        else:
            self.url = "https://api.binance.com"

    def request(self, action, data, method="GET", private=False):
        response = None
        headers = {}

        if private:
            if self.key is None or self.secret is None:
                raise Exception("Key or secret empty")
            headers["X-MBX-APIKEY"] = self.key
            tstamp = int(time.time()* 1000)
            data["timestamp"] = tstamp
            signature = self.generate_signature(data)
            data["signature"] = signature

        if method == "GET":
            response = self.session.get(self.url + action, params=data, headers=headers, verify=True)
        elif method == "POST":
            response = self.session.post(self.url + action, params=data, headers=headers, verify=True)
        elif method == "DELETE":
            response = self.session.delete(self.url + action, params=data, headers=headers, verify=True)

        if response.status_code != 200:
            raise Exception("Wrong response code: " + str(response.status_code))

        return response.json()
        
        # if "result" in json:
        #     return json["result"]
        # elif "message" in json:
        #     return json["message"]
        # else:
        #     return "Ok"


    def generate_signature(self, data):
        sorted_signature_data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

        def converter(data):
            key = data[0]
            value = data[1]
            if isinstance(value, list):
                return '='.join([str(key), ''.join(value)])
            else:
                return '='.join([str(key), str(value)])

        items = map(converter, sorted_signature_data.items())
        signature_string = '&'.join(items)
        hmac_sha256 = hmac.new(self.secret.encode("utf-8"), signature_string.encode("utf-8"), hashlib.sha256)

        return hmac_sha256.hexdigest()

    def getsummary(self, instrument=None):   #GET /api/v3/ticker/24hr
        options = {}

        if instrument:
            options["symbol"] = instrument

        return self.request("/api/v3/ticker/24hr", options)

    def account(self):  #GET /api/v3/account (HMAC SHA256)
        return self.request("/api/v3/account", {}, private=True)


    def buy(self, instrument, quantity, price, postOnly=None, label=None):  #POST /api/v3/order  (HMAC SHA256)
        options = {
            "symbol": instrument,
            "side": "BUY",
            "type": "MARKET",
            "quantity": quantity,
            "price": price
        }
  
        if label:
            options["newClientOrderId"] = label

        if postOnly:
            options["type"] = "LIMIT_MAKER"

        return self.request("/api/v3/order", options, method="POST", private=True)


    def sell(self, instrument, quantity, price, postOnly=None, label=None):     #POST /api/v3/order  (HMAC SHA256)
        options = {
            "symbol": instrument,
            "side": "SELL",
            "type": "Market",
            "quantity": quantity,
            "price": price
        }

        if label:
            options["newClientOrderId"] = label
        if postOnly:
            options["type"] = "LIMIT_MAKER"

        return self.request("/api/v3/order", options, method="POST", private=True)

    def sell_stop_market_order(self, instrument, quantity, price):
        options = {
            "symbol": instrument,
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "time_in_force": "GTC",
            "quantity": quantity,
            "price": price,
            "stopPrice": price      #execIns
        }

        return self.request("/api/v3/order", options, method="POST", private=True)

    def cancel(self, orderId, symbol="LTCBTC"):      #DELETE /api/v3/order  (HMAC SHA256)
        options = {
            "symbol": symbol,
            "orderId": orderId
        }  

        return self.request("/api/v3/order", options, method="DELETE", private=True)

    def getopenorders(self, instrument=None, orderId=None):     #GET /api/v3/openOrders  (HMAC SHA256)
        options = {}

        if instrument:
            options["symbol"] = instrument 
        # if orderId:
        #     options["orderId"] = orderId

        return self.request("/api/v3/openOrders", options, private=True)

    def getorderstate(self, orderId=None, symbol="LTCBTC"):      #GET /api/v3/order (HMAC SHA256)
        options = {
            "symbol": symbol
        }

        if orderId:
            options["orderId"] = orderId

        return self.request("/api/v3/order", options, private=True)  


    def positions(self):        #GET /api/v3/openOrders  (HMAC SHA256)
        return self.request("/api/v3/openOrders", {}, private=True)


    def orderhistory(self, count=None):     #GET /api/v3/allOrders (HMAC SHA256)
        options = {}
        if count:
            options["limit"] = count

        return self.request("/api/v3/allOrders", options, private=True)
