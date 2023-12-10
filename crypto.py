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
API_KEY = ""
SECRET_KEY = ""

# lock of the collect method
lock = Lock()
BASE_URL = "https://api.crypto.com/v2/"
class CoinClient():
  def __init__(self):
    with open('keys.json') as keys:
        information = json.load(keys)
        API_KEY = information ['api_key']
        SECRET_KEY = information ['secret_key']
  # @cached(cache)
  # def tickers(self):
  #   session = Session()
  #   session.headers.update(self.headers)
  #   r = session.get(self.url, params=self.parameters)
  #   data = json.loads(r.text)
  #   if 'data' not in data:
  #     log.error('No data in response. Is your API key set?')
  #     log.info(data)
  #     return data
      

# logging setup
log = logging.getLogger('crypto.com-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

cache_ttl = os.environ.get('CACHE_TTL', 3000)
cache_ttl = 600
cache = TTLCache(maxsize=10000, ttl=cache_ttl)

def get_ticker(instrument_name):
    informations = requests.get(BASE_URL + "public/get-ticker?instrument_name=" + instrument_name)
    informations = json.loads(informations.text)
    return informations['result']['data'][-1]

class CryptodotcomCollector():
  @cached(cache)
  def collect(self):
    with lock:
      log.info('collecting...')
      base_url = 'https://api.crypto.com/v2/public/get-instruments'
      response = requests.get(base_url)
      if response.status_code == 200:
        metric = Metric('crypto_com_marked', 'crypto.com metric values', 'gauge')
        data = response.json()
        instruments = data.get('result', {}).get('instruments', []) #[:3] # Get first 3
        for instrument in instruments:
          instrument_name = (instrument['instrument_name'])
          # quote_currency = (instrument['quote_currency'])
          # base_currency = (instrument['base_currency'])
          # max_quantity = (instrument['max_quantity'])
          ticker = get_ticker(instrument_name)
          coinmarketmetric = '_'.join(['crypto_com_marked', 'price_higest_trade_24h']).lower()
          metric.add_sample(coinmarketmetric, value=float(ticker['h']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
          coinmarketmetric = '_'.join(['crypto_com_marked', 'price_lowest_trade_24h']).lower()
          if ticker['l'] is not None:
            metric.add_sample(coinmarketmetric, value=float(ticker['l']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
            coinmarketmetric = '_'.join(['crypto_com_marked', 'price']).lower()
          if ticker['a'] is not None:
            metric.add_sample(coinmarketmetric, value=float(ticker['a']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
            coinmarketmetric = '_'.join(['crypto_com_marked', 'traded_volume_24h']).lower()
          metric.add_sample(coinmarketmetric, value=float(ticker['v']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
          coinmarketmetric = '_'.join(['crypto_com_marked', 'traded_volume_24h_usd']).lower()
          metric.add_sample(coinmarketmetric, value=float(ticker['vv']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
          coinmarketmetric = '_'.join(['crypto_com_marked', 'price_change_24h']).lower()
          if ticker['c'] is not None:
            metric.add_sample(coinmarketmetric, value=float(ticker['c']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
            coinmarketmetric = '_'.join(['crypto_com_marked', 'best_bid_price']).lower()
          if ticker['b'] is not None:
            metric.add_sample(coinmarketmetric, value=float(ticker['b']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
            coinmarketmetric = '_'.join(['crypto_com_marked', 'best_ask_price ']).lower()
          if ticker['k'] is not None:
            metric.add_sample(coinmarketmetric, value=float(ticker['k']), labels={'id': ticker['i'],'quote_currency': instrument['quote_currency'],'base_currency': instrument['base_currency']})
            # instrument_name         = ticker['i']   # Instrument name
          # price_higest_trade_24h  = ticker['h']   # Price of the 24h highest trade
          # price_lowest_trade_24h  = ticker['l']   # Price of the 24h lowest trade, null if there weren't any trades
          # price                   = ticker['a']   # The price of the latest trade, null if there weren't any trades
          # traded_volume_24h       = ticker['v']   # The total 24h traded volume
          # traded_volume_24h_usd   = ticker['vv'] # The total 24h traded volume value (in USD)
          # price_change_24h        = ticker['c']   # 24-hour price change, null if there weren't any trades
          # best_bid_price          = ticker['b']   # The current best bid price, null if there aren't any bids
          # best_ask_price          = ticker['k']   # The current best ask price, null if there aren't any asks
          log.info(instrument_name)
          # coinmarketmetric = '_'.join(['cryptodotcom_market', 'price_higest_trade_24h']).lower()
          # metric.add_sample(coinmarketmetric, value=float(ticker['h']), labels={'id': ticker['i']})  
        # for that in ['price_higest_trade_24h','price_lowest_trade_24h','price']:
        #   coinmarketmetric = '_'.join(['coin_market', that, 55]).lower()
        #   metric.add_sample(coinmarketmetric, value=float(ticker[that]), labels={'id': data['i']})
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
      log.info('sleep 5 min...')
      time.sleep(300)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)
