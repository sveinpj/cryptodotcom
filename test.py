import json
def mytest():
  global coinmarketmetric
  for that in ['cmc_rank', 'total_supply', 'max_supply', 'circulating_supply']:
    coinmarketmetric = '_'.join(['coin_market', that])
  return coinmarketmetric

with open('sample.json') as keys:
  information = json.load(keys)
  for item in information['coins']:
    print (item['id'])

# mytest()
# print (coinmarketmetric)
