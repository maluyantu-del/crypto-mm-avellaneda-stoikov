import ccxt
import math

# ============================================
# 1. 拿真实订单簿数据
# ============================================
okx = ccxt.okx()
print("正在拿 OKX 的真实订单簿...")
orderbook = okx.fetch_order_book('BTC/USDT', limit=5)
print("✅ 拿到了\n")

market_best_bid = orderbook['bids'][0][0]
market_best_ask = orderbook['asks'][0][0]
market_mid = (market_best_bid + market_best_ask) / 2
market_spread_abs = market_best_ask - market_best_bid
market_spread_bps = (market_spread_abs / market_mid) * 10000

print("="*60)
print("📊 市场真实数据（OKX）")
print("="*60)
print(f"Mid Price:    {market_mid}")
print(f"Spread:       {market_spread_abs:.2f} USDT = {market_spread_bps:.4f} bp")
print()

# ============================================
# 2. AS 模型
# ============================================
def avellaneda_stoikov(mid, inv, sigma, T, gamma, kappa):
    sigma_sq = sigma ** 2
    reservation_price = mid - inv * gamma * sigma_sq * T
    spread = gamma * sigma_sq * T + (2/gamma) * math.log(1 + gamma/kappa)
    bid = reservation_price - spread / 2
    ask = reservation_price + spread / 2
    return reservation_price, bid, ask, spread

# ============================================
# 3. 参数选择
# ============================================
# BTC 日波动率约 3%（业内典型值）
# 用 log return 的标准差表示，年化 ~50%
# T = 1 表示 1 个会话（无量纲）
# 我们希望 spread 落在 10-30 bp 量级（业内非红海币的合理范围）

sigma = 0.03        # 日波动率 3% = log return std
T = 1.0
gamma = 0.5         # 调高让效果显著
kappa = 100         # 高频订单流强度

print("="*60)
print("🤖 AS 模型算的报价")
print(f"参数：sigma={sigma}（日波动率3%）, T={T}, gamma={gamma}, kappa={kappa}")
print("="*60)

# 测试 3 种库存
results = []
for inv in [0, 1, -1]:
    r, my_bid, my_ask, my_spread = avellaneda_stoikov(
        market_mid, inv, sigma, T, gamma, kappa
    )
    my_spread_bps = (my_spread / market_mid) * 10000
    r_offset = r - market_mid
    r_offset_bps = (r_offset / market_mid) * 10000
    results.append((inv, r, my_bid, my_ask, my_spread, my_spread_bps, r_offset_bps))
    
    inv_label = f"+{inv}" if inv > 0 else str(inv)
    print(f"\n库存 = {inv_label} BTC:")
    print(f"  储备价: {r:.2f}   (偏离 mid: {r - market_mid:+.2f} = {r_offset_bps:+.4f} bp)")
    print(f"  Bid:    {my_bid:.2f}")
    print(f"  Ask:    {my_ask:.2f}")
    print(f"  Spread: {my_spread:.2f} USDT = {my_spread_bps:.2f} bp")

# ============================================
# 4. 关键对比
# ============================================
print()
print("="*60)
print("🔥 关键洞察")
print("="*60)

inv0_data = results[0]
inv_plus_data = results[1]
inv_minus_data = results[2]

print(f"\n洞察 1：库存惩罚机制确实在工作")
print(f"  库存 0 时储备价:    {inv0_data[1]:.2f}")
print(f"  库存 +1 BTC 时:    {inv_plus_data[1]:.2f}   (低了 {inv0_data[1] - inv_plus_data[1]:.2f} USDT)")
print(f"  库存 -1 BTC 时:    {inv_minus_data[1]:.2f}   (高了 {inv_minus_data[1] - inv0_data[1]:.2f} USDT)")
print(f"  → 库存多 = 储备价低 = 卖单更便宜 = 逼自己出货 ✓")

print(f"\n洞察 2：AS 算的 spread vs 市场真实 spread")
print(f"  AS spread:      {inv0_data[5]:.2f} bp")
print(f"  市场真实 spread: {market_spread_bps:.4f} bp")
print(f"  差距:           {inv0_data[5] / market_spread_bps:.0f} 倍")
print(f"  → AS 还是太宽，挂在市场上根本不会成交")
print(f"  → 业内做法：拿到 AS 输出后再用'信号'微调，挂在 best bid/ask ± 1 tick")

print(f"\n洞察 3：参数地狱")
print(f"  今晚我调了 3 次参数 3 次错：")
print(f"  - sigma=0.01: 库存惩罚 0.00005 USDT，看不出效果")
print(f"  - sigma=2000: 储备价变成 -119237 美元，爆炸")
print(f"  - sigma=0.03, gamma=0.5: 现在的版本，库存惩罚 {abs(inv0_data[1] - inv_plus_data[1]):.2f} USDT")
print(f"  → AS 的真正工作量是参数标定，公式只是骨架")
