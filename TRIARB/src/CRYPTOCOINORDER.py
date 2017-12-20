import sys
import subprocess
from subprocess import call,PIPE
import hashlib
import base64
import hmac
import time,datetime
import requests

#sys.path.insert(0,'C:\\Users\\Matthew\\AppData\\Local\\GitHub\\PortableGit_f02737a78695063deace08e96d5042710d3e32db\\usr\\bin\\')


class CRYPTOCOINORDER:
    def __init__(self,exchange,secret_key,API_key):
        self.exchange = exchange
        #self.secret_key = 'NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'
        self.secret_key = secret_key
        self.API_key = API_key

    def do_binance_conversion(self, currency, other_currency, quantity, exchange_rate_currency_to_other_currency):
        # ETHBTC SELL = CONVERT ETH TO BTC, quantity is in ETH (asset) BTC is money
        order = 'SELL'
        inverted, currency, other_currency = self.set_currencies_in_order_for_binance(currency,other_currency)
        if inverted == 'inverted':
            order = 'BUY'
            quantity = quantity * exchange_rate_currency_to_other_currency
        #quantity = round(quantity,2)
        quantity = self.round_currency_to_binance_amount(currency,other_currency,quantity)
        print(currency,other_currency,order,str(quantity))
        self.do_market_order(currency, other_currency, order, str(quantity))

    def round_currency_to_binance_amount(self,currency,other_currency,quantity):
        round_factor = 2
        if currency+other_currency == 'LTCBTC':
            round_factor = 2
        elif currency+other_currency == 'ETHBTC' or currency+other_currency == 'LTCETH':
            round_factor = 3
        else:
            raise Exception('I did not recognize the binance symbol')
        return round(quantity,round_factor)

    def set_currencies_in_order_for_binance(self, currency, other_currency):
        if currency == 'BTC' or (currency == 'ETH' and other_currency != 'BTC'):
            return ('inverted', other_currency, currency)
        else:
            return ('non-inverted', currency, other_currency)

    def do_market_order(self,currency,other_currency,side,quantity):
        query_string = self.generate_query_string(currency+other_currency,side,'MARKET',quantity)
        signature = self.generate_SHA256_signature(query_string)
        self.execute_order('https://api.binance.com/api/v3/order',query_string,signature)

    def execute_order(self,API_endpoint,query_string,signature):
        headers = {'X-MBX-APIKEY':self.API_key}
        r = requests.post(API_endpoint + '?' + query_string + '&signature=' + signature,headers=headers)
        print(r.url,r,r.text,r.content)

    def generate_query_string(self,symbol,side,type,quantity):
        return 'symbol=' + symbol + '&side=' + side + '&type=' + type + '&quantity=' + quantity + '&timestamp=' + str(round(time.time()*1000))

    def generate_SHA256_signature(self, message):
        key_bytes = bytes(self.secret_key, 'utf-8')
        data_bytes = bytes(message, 'utf-8')
        x = hmac.new(key_bytes, data_bytes, hashlib.sha256)
        return x.hexdigest()


def Main():
    if len(sys.argv) != 4:
        print ('Usage: python CRYPTOCOINORDER.py exchange private-key api-key')
        return
    cryptocoinorder = CRYPTOCOINORDER(sys.argv[1],sys.argv[2],sys.argv[3])
    #ETHBTC SELL = CONVERT ETH TO BTC, quantity is in ETH (asset) BTC is money
    #cryptocoinorder.do_market_order('LTC','ETH','BUY',str(0.008))
    cryptocoinorder.do_market_order('LTC', 'BTC', 'BUY', str(0.02))

if __name__ == '__main__':
    Main()
