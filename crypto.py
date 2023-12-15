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
# lock of the collect method
lock = Lock()

# logging setup
log = logging.getLogger('crypto.com-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
API_KEY = ""
SECRET_KEY = ""
BASE_URL = "https://api.crypto.com/v2/"

cache_ttl = os.environ.get('CACHE_TTL', 3000)
cache_ttl = 300
cache = TTLCache(maxsize=10000, ttl=cache_ttl)

class instrumentscollector():
  def __init__(self):
    self.base_url = 'https://api.crypto.com/v2/public/get-instruments'

  @cached(cache)
  def getinstruments(self):
    try:
      response = requests.get(self.base_url)
      if response.status_code == 200:
        data = response.json()
        instruments = data.get('result', {}).get('instruments', [])#[:3]
        return instruments
      else:
        log.error('Failure - Error getting API of instrumentscollector.')
        log.info(response.status_code)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
      log.error(f"Failure - Unable to establish connection: {e}.")
    except Exception as e:
      log.error(f"Failure - Unknown error occurred: {e}.")

class tickerinfo():
  def __init__(self,instrument):
    baseurl = 'https://api.crypto.com/v2/'
    try:
      informations = requests.get(baseurl + "public/get-ticker?instrument_name=" + instrument)
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
        log.error('Failure - Error getting API of tickerinfo.')
        log.info(informations.status_code)
        self.laststatus = "error"
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
      log.error(f"Failure - Unable to establish connection: {e}.")
    except Exception as e:
      log.error(f"Failure - Unknown error occurred: {e}.")

class CryptodotcomCollector():
  def __init__(self):
    self.client = instrumentscollector()
  def collect(self):
    with lock:
      log.info('collecting...')
      # query the api
      instruments = self.client.getinstruments()
      metric = Metric('crypto_com_marked', 'crypto.com metric values', 'gauge')
      if 'instrument_name' not in instruments[0]:
        log.error('Halting getting instrument in instruments.')
      else:
        for instrument in instruments:
          ticker = tickerinfo((instrument['instrument_name']))
          if ticker.laststatus == "error":
            log.error('Halting getting coinmarketmetric')
          else:
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