from prometheus_client import start_http_server, Metric, REGISTRY
from threading import Lock
from cachetools import cached, TTLCache
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import argparse
import json
import requests
import logging
import os
import sys
import time

# logging setup
log = logging.getLogger('crypto.com-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
# lock of the collect method
lock = Lock()
cache_ttl = 540
cache = TTLCache(maxsize=10000, ttl=cache_ttl)

class instrumentscollector():
  def __init__(self):
    self.base_url = 'https://api.crypto.com/v2/public/get-instruments'

  @cached(cache)
  def getinstruments(self):
    response = requests.get(self.base_url)
    if response.status_code == 200:
      data = response.json()
      instruments = data.get('result', {}).get('instruments', [])#[:3]
      return instruments
    else:
      log.error('No data in response')
      log.info(response.status_code)

class tickerinfo():
  def __init__(self,instrument):
    baseurl = 'https://api.crypto.com/v2/'
    informations = requests.get(baseurl + "public/get-ticker?instrument_name=" + instrument)
    informations_json = json.loads(informations.text)
    result = informations_json['result']['data'][-1]
    self.instrument_name = result['i']
    self.price_higest_trade_24h = float(result['h'])
    self.price_lowest_trade_24h = float(result['l'])
    self.price = float(result['a'])
    self.traded_volume_24h = float(result['v'])
    self.traded_volume_24h_usd = float(result['vv'])
    self.price_change_24h = float(result['c'])
    self.best_bid_price = float(result['b'])
    self.best_ask_price = float(result['k'])

# class mycollector():
#   def __init__(self):
#     self.client = instrumentscollector()
#   def collect(self):
#     mycollectvalues = self.client.getinstruments()
# ticker = tickerinfo("BTCUSD-PERP")
# print(ticker.traded_volume_24h)
mycollector = instrumentscollector()
mydata = mycollector.getinstruments()
for instrument in mydata:
  # print (instrument['instrument_name'])
  ticker = tickerinfo(instrument['instrument_name'])
  print(ticker.traded_volume_24h)

# my = mydata.collect()




