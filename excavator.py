# -*- coding:utf-8 -*-
import os
import sys
import operator
import pandas as pd
import pyupbit
from upbitpy import Upbitpy
import time
from datetime import datetime, timedelta
""" Reference
[1] https://github.com/inasie/upbitpy
[2] https://wikidocs.net/112460
[3] https://apt-info.github.io/암호화폐/업비트-코인-가격/
"""

class Upbit(object):
    def __init__(self):
        self.upbit = Upbitpy()
        
        
    def coin_symbols(self):
        markets = self.upbit.get_market_all()
        symbols = []
        pair = {}
        
        for market in markets:
            if "KRW" in market['market']:
                symbols.append(market["market"])
                pair[market['market']] = market['korean_name']
        
        print ("[*] Finished getting coin symbols")
        return symbols, pair
    
    
    def coin_current_price(self, symbols):
        tickers = self.upbit.get_ticker(symbols)
        for ticker in tickers:
            print(f"\t{ticker['market']} trade price : {ticker['trade_price']}")
        
        print ("[*] Finished getting coin prices")
    
    
def calc_percent(shork_price, current_price):
    percent = + round((1 - (shork_price / current_price)) * 100, 2)
    return percent
    
    
def get_delta_percent(symbols, shork_date, current_date):
    """
    ex) 
    symbol      : KRW-BTC
    shork_date  : 2021-09-18 09:00:00
    current_date    : 2021-10-21 09:00:00
    """
    shork_date = shork_date + " 09:00:00"
    current_date = current_date + " 09:00:00"
    # price_btc = pyupbit.get_current_price("KRW-BTC")
    # print("BTC : {} KRW\n".format(price_btc))
    
    std_percent = 0
    percents = {}
    
    for symbol in symbols:
        try:
            time.sleep(0.5) # for preventing erorr about JSON
            df = pyupbit.get_ohlcv(symbol)
            df = df.reset_index()
            shork_price = float(df[df['index']==shork_date]['close'])
            current_price = float(df[df['index']==current_date]['close'])
            
            percent = calc_percent(shork_price, current_price)
            percents[symbol] = percent
            
            if symbol == "KRW-BTC":
                std_percent = percent
                #print (f"[*] BTC : {std_percent}%")
                
        except Exception as ex:
            continue
    
    return percents, std_percent


def current_day():
    std_hour = int(str(datetime.now())[11:13])
    current_day = str(datetime.now() - timedelta(days=1))[:10] if std_hour < 9 else str(datetime.now())[:10]
    return current_day
    
            
def show_symbol_n_percent(percents, std_percent, pair):
    std_percent = -13 # 하락장 전 가격 대비 하락장 후 가격 차 퍼센트
    for key, value in sorted(percents.items(), key=operator.itemgetter(1)):
        if value < std_percent:
            print (f'[*] {value}% : {pair[key]}')
    

def main():
    U = Upbit()
    symbols, pair = U.coin_symbols()
    #U.coin_current_price(symbols)
    percents, std_percent = get_delta_percent(symbols, "2021-09-18", current_day())
    show_symbol_n_percent(percents, std_percent, pair)
    

if __name__ == "__main__":
    sys.exit(main())
