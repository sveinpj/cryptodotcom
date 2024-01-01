from prometheus_client import start_http_server, Metric, REGISTRY
from threading import Lock
from cachetools import cached, TTLCache
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from platform import system
import argparse
import json
import requests
import logging
import os
import sys
import time
lock = Lock()

osversion = system()
# logging setup
log = logging.getLogger('crypto.com-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
BASE_URL = "https://api.crypto.com"

cache_ttl = os.environ.get('CACHE_TTL', 1800)
cache = TTLCache(maxsize=10000, ttl=int(cache_ttl))
testing = os.environ.get('TESTING', "true")

class instrumentscollector():
  def __init__(self):
    self.base_url = BASE_URL
    self.headers = {'Accepts': 'application/json'}
  @cached(cache)
  def getinstruments(self):
    session = Session()
    session.headers.update(self.headers)
    try:
      log.info('Collecting instruments...')
      response = session.get(self.base_url + "/v2/public/get-instruments/",timeout=10) 
      if response.status_code == 200:
        instruments = json.loads(response.text)
        if 'result' not in instruments:
          log.error('Instruments failure. No json data in response')
        else:
          if testing == "false":
            instruments = instruments['result']['instruments']
          else:
             instruments = instruments['result']['instruments'][:3] # Test to have 3 records
          self.laststatus = "ok"
          if osversion == "Windows":
            filename = "instruments.txt"
          else:
            filename = "/tmp/instruments.txt"
          #Write instruments to file if needed to check if processes halted.
          if os.path.exists(filename):
            os.remove(filename)
            f = open(filename, "a")
            f.write(str(instruments))
            f.close()
          else:
            f = open(filename, "a")
            f.write(str(instruments))
            f.close()
          return instruments
      else:
        log.error(f"Instruments failure - Error getting API. Error {response.status_code}")
    except ConnectionError as exception:
      log.error(f"Instruments exception - ConnectionError")
    except Timeout as exception:
      log.error(f"Instruments exception - Timeout")

class tickerinfo():
  def __init__(self,instrument):
    baseurl = BASE_URL
    try:
      informations = requests.get(baseurl + "/v2/public/get-ticker?instrument_name=" + instrument,timeout=10)
      if informations.status_code == 200:
        informations_json = json.loads(informations.text)
        result = informations_json['result']['data'][-1]
        self.instrument_name = result['i']
        self.price_higest_trade_24h = result['h']
        self.price_lowest_trade_24h = result['l']
        self.price = result['a']
        self.traded_volume_24h = result['v']
        self.traded_volume_24h_usd = result['vv']
        self.price_change_24h = result['c']
        self.best_bid_price = result['b']
        self.best_ask_price = result['k']
        self.laststatus = "ok"
      else:
        log.error(f"Tickerinfo failure - Error getting API of {instrument}. Error {informations.status_code}")
        self.laststatus = "error"
    except ConnectionError as exception:
      self.laststatus = "error"
    except Timeout as exception:
      self.laststatus = "error"

class CryptodotcomCollector():
  def __init__(self):
    self.client = instrumentscollector()
  def collect(self):
    with lock:
      instruments = self.client.getinstruments()
      if instruments == None:
        log.error('Could not collect instruments')
      else:
        if 'instrument_name' not in instruments[0]:
          log.error("No instrument_name in collection of instruments")
        else:
          metric = Metric('crypto_com_marked', 'crypto.com metric values', 'gauge')
          log.info('Collecting tickerinfo...')
          for instrument in instruments:
            ticker = tickerinfo((instrument['instrument_name']))
            if ticker.laststatus == "ok":
              if ticker.price_higest_trade_24h is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'price_higest_trade_24h']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.price_higest_trade_24h), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.price_lowest_trade_24h is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'price_lowest_trade_24h']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.price_lowest_trade_24h), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.price is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'price']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.price), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.traded_volume_24h is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'traded_volume_24h']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.traded_volume_24h), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.traded_volume_24h_usd is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'traded_volume_24h_usd']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.traded_volume_24h_usd), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.price_change_24h is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'price_change_24h']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.price_change_24h), labels={'id': (ticker.instrument_name).lower(),'name': instrument['base_currency']})
              if ticker.best_bid_price is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'best_bid_price']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.best_bid_price), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              if ticker.best_ask_price is not None:
                coinmarketmetric = '_'.join(['crypto_com_marked', 'best_ask_price']).lower()
                metric.add_sample(coinmarketmetric, value=float(ticker.best_ask_price), labels={'id': (ticker.instrument_name).lower(),'quote_currency': instrument['quote_currency'],'name': instrument['base_currency']})
              yield metric
          log.info("Done collecting tickerinfo...")

if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on', default=9101)
    parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='The interface to bind to', default='0.0.0.0')
    args = parser.parse_args()
    log.info('listening on http://%s:%d/metrics' % (args.addr, args.port))

    REGISTRY.register(CryptodotcomCollector())
    start_http_server(int(args.port), addr=args.addr)

    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)