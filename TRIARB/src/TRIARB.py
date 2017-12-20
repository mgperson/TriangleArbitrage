'''
TRIARB takes a currency list and a per transaction fee and searches for profitable triangle arbitrage trades from all permutations of the currency list
'''

import requests
import json
import itertools
import time,datetime
import sys
from CRYPTOCOINORDER import CRYPTOCOINORDER

class TRIARB:
    def __init__(self, currency_list, per_transaction_fee, exchange,mode='analyze',secret_key=None,API_key=None):
        self.currency_list = currency_list
        self.per_transacation_fee = per_transaction_fee
        self.fee_rate = self.get_fee_rate()
        self.exchange = exchange
        self.mode = mode

        self.exchange_rate_cache = {}
        #print(self.get_profitability_of_trades_at_intervals('gdax', 120, 5, 10000))
        #self.trade_quantity_in_bitcoin = .0001608
        #self.trade_quantity_in_bitcoin = .0002670
        #self.trade_quantity_in_bitcoin = .0002
        self.trade_quantity_in_LTC = .01


        if mode == 'run':
            self.cryptocoinorder = CRYPTOCOINORDER(exchange,secret_key,API_key)
        print(self.get_profitability_of_trades_at_intervals(exchange, 240, 5, 10000))

    def get_profitability_of_trades_at_intervals(self, site, duration_seconds, interval_seconds, starting_value):
        value = starting_value
        for i in range(int(duration_seconds/interval_seconds)):
            trade_result = self.get_maximum_advisable_trade_permutation(site)
            if trade_result[1] != None:
                value *= (trade_result[0] - self.fee_rate)
                if self.mode == 'run':
                    self.perform_triple_trade(self.exchange,trade_result[1])
            print(datetime.datetime.now())
            time.sleep(interval_seconds)
            #flush cash after every check
            self.exchange_rate_cache = {}
        return value

    def get_maximum_advisable_trade_permutation(self, site):
        max_rate,max_permutation = 0,None
        for permutation in itertools.permutations(self.currency_list):
            try:
                profit_rate = self.get_trade_profit(site,permutation)
                #print('Analyzed profit rate for permutation:' + ','.join([str(currency) for currency in permutation]) + ' is: ' + str(profit_rate))
                if self.is_trade_advisable(self.fee_rate,profit_rate) and profit_rate > max_rate:
                    max_rate,max_permutation = profit_rate,permutation
                    print ('Most profitable transaction is: ' + str(profit_rate) + ' for: ' + ','.join([currency for currency in max_permutation]))
            except:
                print('I could not process the arbitrage calculation for: ' + permutation)
        return (max_rate,max_permutation)

    def perform_trade(self,currency,other_currency):
        #quantity = self.trade_quantity_in_bitcoin if currency == 'BTC' else self.trade_quantity_in_bitcoin * self.get_exchange_rate_from_binance('BTC', currency)
        quantity = self.trade_quantity_in_LTC if currency == 'LTC' else self.trade_quantity_in_LTC * self.get_exchange_rate_from_binance(
            'LTC', currency)
        #print('currency:' + currency)
        #print('exchange rate: ' + str(self.get_exchange_rate_from_binance('BTC', currency)))
        #print('quantity:' + str(quantity))
        self.cryptocoinorder.do_binance_conversion(currency, other_currency, quantity, self.get_exchange_rate_from_binance(currency,other_currency))


    def perform_triple_trade(self,exchange,currency_ordered_list):
        for i in range(len(currency_ordered_list)-1):
            self.perform_trade(currency_ordered_list[i],currency_ordered_list[i+1])
        self.perform_trade(currency_ordered_list[-1], currency_ordered_list[0])

    def get_fee_rate(self):
        return (len(self.currency_list) -0) * self.per_transacation_fee


    def is_trade_advisable(self,fee_rate,profit_percentage):
        return fee_rate < (profit_percentage - 1)

    def get_trade_profit(self, site, currency_ordered_list):
        profit_percentage = 1
        for i in range(len(currency_ordered_list)-1):
            currency = currency_ordered_list[i]
            other_currency = currency_ordered_list[i+1]
            profit_percentage *= self.get_exchange_rate(site,currency,other_currency)
        profit_percentage *= self.get_exchange_rate(site,currency_ordered_list[-1],currency_ordered_list[0])
        return profit_percentage

    def get_exchange_rate(self,site,currency,other_currency):
        if site == 'gdax':
            return self.get_exchange_rate_from_gdax(currency,other_currency)
        elif site == 'binance':
            return self.get_exchange_rate_from_binance(currency, other_currency)
        else:
            raise Exception('Did not recognize exchange site')

    def get_exchange_rate_from_gdax(self,currency,other_currency):
        if (currency,other_currency) in self.exchange_rate_cache:
            return self.exchange_rate_cache[(currency,other_currency)]
        url = 'https://api.coinbase.com/v2/exchange-rates?currency=' + currency
        try:
            result = requests.get(url,timeout=100)
            exchange = json.loads(result.text)
            exchange_rate = exchange['data']['rates'][other_currency]
        except:
            raise Exception('There was an error contacting site: ' + url)
        self.exchange_rate_cache[(currency,other_currency)] = float(exchange_rate)
        return float(exchange_rate)

    def get_exchange_rates_from_binance(self):
        if 'binance' in self.exchange_rate_cache:
            pass
        else:
            url = 'https://api.binance.com/api/v3/ticker/price'
            try:
                result = requests.get(url, timeout=100)
                self.exchange_rate_cache['binance'] = json.loads(result.text)
            except:
                raise Exception('There was an error contacting site: ' + url)
        return self.exchange_rate_cache['binance']

    #Binance only displays ETH and BTC conversions
    def set_currencies_in_order_for_binance(self,currency,other_currency):
        if currency == 'BTC' or (currency == 'ETH' and other_currency != 'BTC'):
            return ('inverted',other_currency,currency)
        else:
            return ('non-inverted',currency,other_currency)


    def get_exchange_rate_from_binance(self,currency,other_currency):
        inverted,currency,other_currency = self.set_currencies_in_order_for_binance(currency,other_currency)
        exchange_rates = self.get_exchange_rates_from_binance()
        for exchange_rate in exchange_rates:
            if exchange_rate['symbol'] == currency + other_currency:
                if inverted == 'inverted':
                    return 1 / float(exchange_rate['price'])
                else:
                    return float(exchange_rate['price'])



def Main():
    if len(sys.argv) != 4 and len(sys.argv) != 6:
        print ('Usage for showing analysis: python TRIARB.py coin-abbreviations fee exchange')
        print('or to run triangle arbitrage: python TRIARB.py coin-abbreviations fee exchange private-key api-key')
        return
    coins = sys.argv[1].split(',')
    fee_rate = float(sys.argv[2])
    exchange = sys.argv[3]
    #triarb = TRIARB(['BTC','LTC','ETH'],.0025,'binance')
    if len(sys.argv) == 4:
        triarb = TRIARB(coins, fee_rate,exchange)
    else:
        secret_key = sys.argv[4]
        API_key = sys.argv[5]
        triarb = TRIARB(coins, fee_rate, exchange,'run',secret_key,API_key)

if __name__ == '__main__':
    Main()