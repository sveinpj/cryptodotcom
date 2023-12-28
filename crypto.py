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
tickercache = TTLCache(maxsize=10000, ttl=cache_ttl)

class instrumentscollector():
  def __init__(self):
    self.base_url = 'https://api.crypto.com'
    self.headers = {'Accepts': 'application/json'}
  @cached(cache)
  def getinstruments(self):
    session = Session()
    session.headers.update(self.headers)
    try:
      response = session.get(self.base_url + "/v2/public/get-instruments/") 
      if response.status_code == 200:
        instruments = json.loads(response.text)
        if 'result' not in instruments:
          log.error('No data in response. Is your API key set?')
          log.info(instruments)
        # data = response.json()
        instruments = instruments['result']['instruments']
        #instruments = instruments.get('result', {}).get('instruments')#[:3]
        self.laststatus = "ok"
        return instruments
      elif response.status_code == 502:
        log.error('Instruments failure - 502 - Bad Gateway...')
      elif response.status_code == 504:
        log.error('Instruments failure - 504 - Gateway timeout...')
      else:
        log.error('Instruments failure - Error getting API of instrumentscollector.')
        log.info(response.status_code)
    except ConnectionError as exception:    # This is the correct syntax
      return exception
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as exception:
      # log.error(f"Instruments exception failure - Unable to establish connection: {exception}.")
      return exception
    except Exception as exception:
      # log.error(f"Instruments exception failure - Unknown error occurred: {exception}.")
      return exception

class tickerinfo():
  @cached(tickercache)
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
      elif informations.status_code == 502:
        log.error('Tickerinfo failure - 502 - Bad Gateway...')
        self.laststatus = "502"
      elif informations.status_code == 504:
        log.error('Tickerinfo failure - 504 - Gateway timeout...')
        self.laststatus = "504"
      elif informations.status_code == 522:
        log.error('Tickerinfo failure - 522 - Connection timeout...')
        self.laststatus = "522"
      elif informations.status_code == 524:
        log.error('Tickerinfo failure - 524 - A Timout Occured...')
        self.laststatus = "524"
      else:
        log.error('Tickerinf failure - Error getting API of tickerinfo.')
        log.info(informations.status_code)
        self.laststatus = "error"
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
      # log.error(f"Tickerinfo exception failure - Unable to establish connection: {e}.")
      self.laststatus = "error"
    except Exception as e:
      # log.error(f"Tickerinfo exception failure - Unknown error occurred: {e}.")
      self.laststatus = "error"

class CryptodotcomCollector():
  def __init__(self):
    self.client = instrumentscollector()
  def collect(self):
    with lock:
      log.info('Collecting instruments...')
      # query the api
      instruments = self.client.getinstruments()
      if 'instrument_name' not in instruments[0]:
        print("Not Hi")
      else:
        log.info('Done collecting instruments...')
        metric = Metric('crypto_com_marked', 'crypto.com metric values', 'gauge')
        log.info('Collecting tickerinfo...')
        for instrument in instruments:
          ticker = tickerinfo((instrument['instrument_name']))
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
      log.info('Done collecting tickerinfo...')

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