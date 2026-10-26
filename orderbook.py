import ccxt
import time

okx = ccxt.okx()

# 加 retry：失败自动重试 3 次
orderbook = None
for attempt in range(3):
    try:
        print(f"尝试第 {attempt + 1} 次...")
        orderbook = okx.fetch_order_book('BTC/USDT', limit=10)
        print("✅ 成功！\n")
        break
    except Exception as e:
        print(f"❌ 失败：{type(e).__name__}")
        if attempt < 2:
            print("等 2 秒重试...\n")
            time.sleep(2)

if orderbook is None:
    print("\n3 次都失败了。网络不稳定，明天换网络再试。")
    exit()

print("="*60)
print(f"{'类型':<10} {'价格':<15} {'数量 (BTC)':<15}")
print("="*60)

print("\n卖单 (ASK) - 从高到低显示：")
for level in reversed(orderbook['asks']):
    price = level[0]
    amount = level[1]
    print(f"{'ASK':<10} {price:<15} {amount:<15}")

best_bid = orderbook['bids'][0][0]
best_ask = orderbook['asks'][0][0]
mid_price = (best_bid + best_ask) / 2
spread_abs = best_ask - best_bid
spread_bps = (spread_abs / mid_price) * 10000

print(f"\n{'-'*60}")
print(f"📊 MID PRICE: {mid_price}")
print(f"📊 Spread: {spread_abs:.2f} USDT = {spread_bps:.2f} bp")
print(f"{'-'*60}\n")

print("买单 (BID) - 从高到低显示：")
for level in orderbook['bids']:
    price = level[0]
    amount = level[1]
    print(f"{'BID':<10} {price:<15} {amount:<15}")

print("="*60)
