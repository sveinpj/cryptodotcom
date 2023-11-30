import json
from prometheus_client import start_http_server, Metric, REGISTRY
# def mytest():
#   global coinmarketmetric
#   for that in ['cmc_rank', 'total_supply', 'max_supply', 'circulating_supply']:
#     coinmarketmetric = '_'.join(['coin_market', that])
#   return coinmarketmetric

with open('sample.json') as keys:
  information = json.load(keys)
  metric = Metric('coin_market', 'coinmarketcap metric values', 'gauge')
  for value in information['coins']:
    #for that in ['cmc_rank', 'total_supply', 'max_supply', 'circulating_supply']:
    for that in ['rank', 'totalSupply']:
      coinmarketmetric = '_'.join(['coin_market', that])
      # print (coinmarketmetric)
      if value[that] is not None:
          metric.add_sample(coinmarketmetric, value=float(value[that]), labels={'id': value['slug'], 'name': value['name'], 'symbol': value['symbol']})

  # for item in information['coins']:
  #   print (item['id'])

# mytest()
# print (coinmarketmetric)
