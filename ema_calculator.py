import requests
import pandas as pd

def get_binance_ohlcv(symbol: str, interval: str, limit: int = 1000):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        print(f"⏳ Veri çekiliyor: {symbol}, {interval}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) < 50:
            print("⛔ Yetersiz veri:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print("❌ Binance veri çekme hatası:", e)
        return pd.DataFrame()

def find_best_ema_combination(symbol, interval, short_min, short_max, long_min, long_max):
    df = get_binance_ohlcv(symbol, interval)

    if df.empty:
        return {
            "short": 0, "long": 0, "profit": -9999,
            "equity_curve": [], "note": "Veri çekilemedi"
        }

    best = {"short": 0, "long": 0, "profit": -9999, "equity_curve": []}

    for short in range(short_min, short_max + 1):
        for long in range(long_min, long_max + 1):
            if short >= long:
                continue

            df['ema_short'] = df['close'].ewm(span=short).mean()
            df['ema_long'] = df['close'].ewm(span=long).mean()
            df['signal'] = 0
            df.loc[df['ema_short'] > df['ema_long'], 'signal'] = 1
            df.loc[df['ema_short'] < df['ema_long'], 'signal'] = -1
            df['return'] = df['close'].pct_change().shift(-1)
            df['strategy'] = df['signal'].shift(1) * df['return']
            df['equity'] = (df['strategy'].fillna(0) + 1).cumprod()

            valid = df['equity'].notna().sum()
            if valid < 5:
                continue

            total_profit = df['equity'].iloc[-2] - 1
            if total_profit > best["profit"]:
                best = {
                    "short": short,
                    "long": long,
                    "profit": round(total_profit, 4),
                    "equity_curve": df['equity'].fillna(1).round(4).tolist()
                }

    return best
