# Issues
## git merge are entirely different commit histories
git checkout [BRANCH]   
git branch main [BRANCH] -f   
git checkout main
git push origin main -f


https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/
https://www.youtube.com/watch?v=yG9kmBQAtW4
https://levelup.gitconnected.com/transforming-remote-json-into-prometheus-metrics-334d772df38a
old:
coin_market_cmc_rank{id="bnb",name="BNB",symbol="BNB"} 4.0
coin_market_total_supply{id="bnb",name="BNB",symbol="BNB"} 1.5169870457493302e+08
coin_market_circulating_supply{id="bnb",name="BNB",symbol="BNB"} 1.5169870457493302e+08
coin_market_price_usd{id="bnb",name="BNB",symbol="BNB"} 228.90160470050466
coin_market_volume_24h_usd{id="bnb",name="BNB",symbol="BNB"} 5.926118524419742e+08
coin_market_market_cap_usd{id="bnb",name="BNB",symbol="BNB"} 3.472407690818996e+010
coin_market_percent_change_1h_usd{id="bnb",name="BNB",symbol="BNB"} 0.02918713
coin_market_percent_change_24h_usd{id="bnb",name="BNB",symbol="BNB"} 0.71950936
coin_market_percent_change_7d_usd{id="bnb",name="BNB",symbol="BNB"} -2.24513012

new:  
crypto_com_pricehigh_24h{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 51790.00
crypto_com_pricelow_24h{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 47895.50
crypto_com_pricelatest{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 51174.500000
crypto_com_volume_24h{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 879.5024
crypto_com_volume_24h_usd{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 26370000.12
crypto_com_open_interest{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 12345.12
crypto_com_change_24h{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 0.03955106
crypto_com_current_best_bid{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 51170.000000
crypto_com_current_best_ask{id="btcusd-perp",name="BTCUSD-PERP",instrument="BTCUSD-PERP"} 51180.000000



{
    "id": "1839",
    "name": "BNB",
    "symbol": "BNB",
    "slug": "bnb",
    "num_market_pairs": "1801",
    "date_added": "2017-07-25T00:00:00.000Z",
    "tags": [
        "marketplace",
        "centralized-exchange",
        "payments",
        "smart-contracts",
        "alameda-research-portfolio",
        "multicoin-capital-portfolio",
        "bnb-chain",
        "layer-1",
        "sec-security-token",
        "alleged-sec-securities",
        "celsius-bankruptcy-estate"
    ],
    "max_supply": "None",
    "circulating_supply": "151698717.19122392",
    "total_supply": "151698717.19122392",
    "infinite_supply": "False",
    "platform": "None",
    "cmc_rank": "4",
    "self_reported_circulating_supply": "None",
    "self_reported_market_cap": "None",
    "tvl_ratio": "None",
    "last_updated": "2023-12-01T07:09:00.000Z",
    "quote": {
        "USD": {
            "price": 228.766184614026,
            "volume_24h": 590104461.9704267,
            "volume_change_24h": -3.8897,
            "percent_change_1h": -0.10029472,
            "percent_change_24h": 0.20398068,
            "percent_change_7d": -2.59260223,
            "percent_change_30d": 1.81480495,
            "percent_change_60d": 4.37031939,
            "percent_change_90d": 6.72511453,
            "market_cap": 34703536742.67845,
            "market_cap_dominance": 2.4076,
            "fully_diluted_market_cap": 34703536742.68,
            "tvl": "None",
            "last_updated": "2023-12-01T07:09:00.000Z"
        }
    }
}





{
  "id": -1,
  "method": "public/get-tickers",
  "code": 0,
  "result": {
    "data": [{
      "h": "51790.00",        // Price of the 24h highest trade*
      "l": "47895.50",        // Price of the 24h lowest trade, null if there weren't any trades*
      "a": "51174.500000",    // The price of the latest trade, null if there weren't any trades*
      "i": "BTCUSD-PERP",     // Instrument name                                                      <-----------Name----------------->
      "v": "879.5024",        // The total 24h traded volume*
      "vv": "26370000.12",    // The total 24h traded volume value (in USD)*
      "oi": "12345.12",       // Open interest*
      "c": "0.03955106",      // 24-hour price change, null if there weren't any trades*
      "b": "51170.000000",    // The current best bid price, null if there aren't any bids*
      "k": "51180.000000",    // The current best ask price, null if there aren't any asks*
      "t": 1613580710768
    }]
  }
}