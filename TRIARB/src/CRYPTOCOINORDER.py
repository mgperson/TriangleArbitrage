import sys
import subprocess
from subprocess import call,PIPE
import hashlib
import base64
import hmac
import time,datetime

sys.path.insert(0,'C:\\Users\\Matthew\\AppData\\Local\\GitHub\\PortableGit_f02737a78695063deace08e96d5042710d3e32db\\usr\\bin\\')


class CRYPTOCOINORDER:
    def __init__(self,exchange):
        self.exchange = exchange
        self.openssl_command = 'C:\\Users\\Matthew\\AppData\\Local\\GitHub\\PortableGit_f02737a78695063deace08e96d5042710d3e32db\\usr\\bin\\openssl'
        self.secret_key = 'NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'

    def do_market_order(self,currency,other_currency,side,quantity):
        query_string = self.generate_query_string(currency+other_currency,side,'MARKET',quantity)

    def generate_query_string(self,symbol,side,type,quantity):
        return 'symbol=' + symbol + '&side=' + side + '&type=' + type + '&quantity=' + quantity + '&timestamp=' + round(time.time())

    def generate_SHA256_signature(self,hashvalue):
        key_bytes = bytes(self.secret_key, 'utf-8')
        data_bytes = bytes(hashvalue, 'utf-8')
        x = hmac.new(key_bytes, data_bytes, hashlib.sha256)
        return x.hexdigest()


def Main():
    cryptocoinorder = CRYPTOCOINORDER('binance')
    query_string = 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559'
    signature = cryptocoinorder.generate_SHA256_signature(query_string)
    print(signature)

if __name__ == '__main__':
    Main()
