import ccxt

# 换成 OKX
okx = ccxt.okx()

# 拿 BTC/USDT 的实时行情
ticker = okx.fetch_ticker('BTC/USDT')

print(f"BTC 当前价: {ticker['last']}")
print(f"24h 高: {ticker['high']}")
print(f"24h 低: {ticker['low']}")
print(f"24h 成交量: {ticker['baseVolume']:.2f} BTC")
