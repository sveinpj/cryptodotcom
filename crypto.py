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
      
"""
crypto.com
{
  "id": -1,
  "method": "public/get-tickers",
  "code": 0,
  "result": {
    "data": [{
      "h": "51790.00",        // Price of the 24h highest trade
      "l": "47895.50",        // Price of the 24h lowest trade, null if there weren't any trades
      "a": "51174.500000",    // The price of the latest trade, null if there weren't any trades
      "i": "BTCUSD-PERP",     // Instrument name
      "v": "879.5024",        // The total 24h traded volume
      "vv": "26370000.12",    // The total 24h traded volume value (in USD)
      "oi": "12345.12",       // Open interest
      "c": "0.03955106",      // 24-hour price change, null if there weren't any trades
      "b": "51170.000000",    // The current best bid price, null if there aren't any bids
      "k": "51180.000000",    // The current best ask price, null if there aren't any asks
      "t": 1613580710768
    }]
  }
}

coinmarked
{
"data": [
{
"id": 1,
"name": "Bitcoin",
"symbol": "BTC",
"slug": "bitcoin",
"cmc_rank": 5,
"num_market_pairs": 500,
"circulating_supply": 16950100,
"total_supply": 16950100,
"max_supply": 21000000,
"infinite_supply": false,
"last_updated": "2018-06-02T22:51:28.209Z",
"date_added": "2013-04-28T00:00:00.000Z",
"tags": [
"mineable"
],
"platform": null,
"self_reported_circulating_supply": null,
"self_reported_market_cap": null,
"quote": {
"USD": {
"price": 9283.92,
"volume_24h": 7155680000,
"volume_change_24h": -0.152774,
"percent_change_1h": -0.152774,
"percent_change_24h": 0.518894,
"percent_change_7d": 0.986573,
"market_cap": 852164659250.2758,
"market_cap_dominance": 51,
"fully_diluted_market_cap": 952835089431.14,
"last_updated": "2018-08-09T22:53:32.000Z"
},
"BTC": {
"price": 1,
"volume_24h": 772012,
"volume_change_24h": 0,
"percent_change_1h": 0,
"percent_change_24h": 0,
"percent_change_7d": 0,
"market_cap": 17024600,
"market_cap_dominance": 12,
"fully_diluted_market_cap": 952835089431.14,
"last_updated": "2018-08-09T22:53:32.000Z"
}
}
},
{
"id": 1027,
"name": "Ethereum",
"symbol": "ETH",
"slug": "ethereum",
"num_market_pairs": 6360,
"circulating_supply": 16950100,
"total_supply": 16950100,
"max_supply": 21000000,
"infinite_supply": false,
"last_updated": "2018-06-02T22:51:28.209Z",
"date_added": "2013-04-28T00:00:00.000Z",
"tags": [
"mineable"
],
"platform": null,
"quote": {
"USD": {
"price": 1283.92,
"volume_24h": 7155680000,
"volume_change_24h": -0.152774,
"percent_change_1h": -0.152774,
"percent_change_24h": 0.518894,
"percent_change_7d": 0.986573,
"market_cap": 158055024432,
"market_cap_dominance": 51,
"fully_diluted_market_cap": 952835089431.14,
"last_updated": "2018-08-09T22:53:32.000Z"
},
"ETH": {
"price": 1,
"volume_24h": 772012,
"volume_change_24h": -0.152774,
"percent_change_1h": 0,
"percent_change_24h": 0,
"percent_change_7d": 0,
"market_cap": 17024600,
"market_cap_dominance": 12,
"fully_diluted_market_cap": 952835089431.14,
"last_updated": "2018-08-09T22:53:32.000Z"
}
}
}
],
"status": {
"timestamp": "2018-06-02T22:51:28.209Z",
"error_code": 0,
"error_message": "",
"elapsed": 10,
"credit_count": 1
}
}
"""


# logging setup
log = logging.getLogger('crypto.com-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

cache_ttl = os.environ.get('CACHE_TTL', 3000)
cache_ttl = 540
cache = TTLCache(maxsize=10000, ttl=cache_ttl)

# BASE_URL = "https://api.crypto.com/v2/"
# API_KEY = ""
# SECRET_KEY = ""

# with open('keys.json') as keys:
#     information = json.load(keys)
#     API_KEY = information ['api_key']
#     SECRET_KEY = information ['secret_key']

# def get_candlestick(instrument_name,timeframe):
#     informations = requests.get(BASE_URL + "public/get-candlestick?instrument_name="+instrument_name+"&timeframe=" + timeframe)
#     informations = json.loads(informations.text)
#     return informations['result']['data'][-1]

def get_ticker(instrument_name):
    informations = requests.get(BASE_URL + "public/get-ticker?instrument_name=" + instrument_name)
    informations = json.loads(informations.text)
    return informations['result']['data'][-1]



def get_instruments():
    # headers = {
    # 'Content-Type': 'application/json',
    # 'Authorization': f'Bearer {API_KEY}'
    # }
    base_url = 'https://api.crypto.com/v2/public/get-instruments'
    # Fetch the list of symbols
    response = requests.get(base_url)
    informations = json.loads(response.text)
    if response.status_code == 200:
       data = response.json()
       instruments = data.get('result', {}).get('instruments', [])
       symbols = [instrument['instrument_name'] for instrument in instruments]
    #    return symbols
    #    print("List of symbols:")
    #    var = "[]"
       for symbol in symbols:
           latest_ticker = get_ticker(symbol)
           print (latest_ticker)
        #    latest_candlestick = get_candlestick(symbol,"M5")
        #    print(latest_candlestick)
def simpleticker():
    btc_usd = get_ticker("BTC_USD")
    print (btc_usd)
simpleticker()

class CoinCollector():
  def __init__(self):
     a = 1
    
#     self.client = CoinClient()
  def collect(self):
     with lock:
      log.info('collecting...')
      btc_usd = get_ticker("BTC_USD")
      print (btc_usd)
#       response = self.client.tickers()
#       metric = Metric('coin_market', 'coinmarketcap metric values', 'gauge')
if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on', default=9101)
    parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='The interface to bind to', default='0.0.0.0')
    args = parser.parse_args()
    log.info('listening on http://%s:%d/metrics' % (args.addr, args.port))

    # REGISTRY.register(CoinCollector())
    start_http_server(int(args.port), addr=args.addr)

    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)


    #     if data.get('result') == 'success':
    #         instruments = data.get('data', {}).get('instruments', [])
    #         symbols = [instrument['instrument_name'] for instrument in instruments]
    #         print("List of symbols:")
    #         for symbol in symbols:
    #             print(symbol)
    #     else:
    #         print("Failed to retrieve symbols.")
    # else:
    #     print(f"Failed to fetch symbols. Status code: {response.status_code}")
# get_ticker("BTCUSD-PERP")
# exit()
# get_instruments()
# informations = requests.get(https://BASE_URL + "/public/get-tickers?instrument_name=BTCUSD-PERP")
# informations = json.loads(informations.text)
# print informations
# # import requests

# # Replace 'YOUR_API_KEY' with your actual API key from Crypto.com
# # API_KEY = 'YOUR_API_KEY'
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': f'Bearer {API_KEY}'
# }


# # Define the base URL for the Crypto.com API
# # https://{URL}/public/get-tickers?instrument_name=BTCUSD-PERP
# base_url = 'https://api.crypto.com/v2/public/get-tickers'
# # Define the list of symbols for which you want to retrieve the latest prices
# symbols = ['BTCUSD-PERP']  # Add more symbols as needed

# # Create an empty dictionary to store symbol and its latest price
# latest_prices = {}

# # Fetch latest prices for each symbol
# for symbol in symbols:
#     params = {'instrument_name': symbol}
#     response = requests.get(base_url, headers=headers, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         if data.get('result') == 'success':
#             ticker_data = data.get('data', {}).get('ticker', {})
#             latest_price = ticker_data.get('last', 'N/A')
#             latest_prices[symbol] = latest_price
#         else:
#             print(f"Failed to retrieve data for {symbol}")
#     else:
#         print(f"Failed to fetch data for {symbol}. Status code: {response.status_code}")

# # Display latest prices
# for symbol, price in latest_prices.items():
#     print(f"Latest price for {symbol}: {price}")


