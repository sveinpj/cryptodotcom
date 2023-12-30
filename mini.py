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
log = logging.getLogger('test-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
API_KEY = ""
SECRET_KEY = ""
# BASE_URL = "https://api.crypto.com/v2/"

cache_ttl = os.environ.get('CACHE_TTL', 3000)
cache_ttl = 60
cache = TTLCache(maxsize=10000, ttl=cache_ttl)
tickercache = TTLCache(maxsize=10000, ttl=cache_ttl)

class instrumentscollector():
  log.info('Step into instrumentscollector')
  def __init__(self):
    # self.base_url = 'https://api.crypto.com/v2/public/get-instruments'
    self.base_url = 'https://instruments.minimedaillon.no'
    log.info('Step after class instrumentscollector, before cache')

  @cached(cache)
  def getinstruments(self):
    log.info('Session')
    session = Session()
    r = session.get(self.base_url + "/v2/public/get-instruments/",timeout=5)
    if r.status_code == 200:
      log.info("Got 200")
      return r
    else:
      log.error("Got other than 200")

    # try:
    #   response = session.get(self.base_url + "/v2/public/get-instruments/",timeout=5)
    #   if response.status_code == 200:
    #     log.info('Status 200')
    #     instruments = json.loads(response.text)
    #     # instruments = instruments['result']['instruments']
    #     return instruments
    # except ConnectionError as exception:    # This is the correct syntax
    #   log.error('Got a exception 1')
    #   return exception
    # except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as exception:
    #   log.error('Got a exception 2')
    #   return exception
    # except Exception as exception:
    #   log.error('Got a exception 3')
    #   return exception

class CryptodotcomCollector():
  def __init__(self):
    self.collector = instrumentscollector()
  def collect(self):
    with lock:
      metric = Metric('crypto_com_marked', 'crypto.com metric values', 'gauge')
      log.info('Collecting instruments...')
      # query the api
      instruments = self.collector.getinstruments()
      if instruments is None:
        log.error("Data is none")
      else:
        print(instruments)
        log.info('End of line')
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
      log.info('Start Sleep')
      time.sleep(30)
      log.info('End Sleep')
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)