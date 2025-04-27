import requests
import pandas as pd
import numpy as np
import talib
from datetime import datetime

# توکن API Twelvedata (باید از Twelvedata API خود دریافت کنید)
api_key = 'ee21ac4e811a4cdba9316622085da401'

# تابع دریافت داده از Twelvedata
def get_forex_data(symbol, interval='1h', start_date='2023-01-01', end_date=datetime.now().strftime('%Y-%m-%d')):
    url = f'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': interval,
        'apikey': api_key,
        'start_date': start_date,
        'end_date': end_date
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'values' in data:
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.astype(float)
        return df
    else:
        raise ValueError(f"Error fetching data: {data.get('message', 'Unknown error')}")

# تابع برای تحلیل امواج الیوت (به صورت ساده)
def apply_elliott_wave(df):
    # اینجا یک الگوریتم پایه برای تحلیل امواج الیوت داریم که می‌توانید گسترش دهید
    df['wave_up'] = np.where(df['close'] > df['close'].shift(1), 1, 0)
    df['wave_down'] = np.where(df['close'] < df['close'].shift(1), 1, 0)
    df['wave_strength'] = df['close'] - df['close'].shift(1)
    return df

# تابع برای تحلیل پرایس اکشن
def apply_price_action(df):
    # نمونه تحلیل پرایس اکشن: شناسایی الگوهای کندلی
    df['bullish_engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
    df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
    df['morning_star'] = talib.CDL3STARSIN3COLUMNS(df['open'], df['high'], df['low'], df['close'])
    return df

# اجرای استراتژی با اندیکاتورها و تحلیل
def apply_technical_indicators(df):
    # نمونه اندیکاتورهای مورد استفاده
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['SMA'] = talib.SMA(df['close'], timeperiod=50)
    df['EMA'] = talib.EMA(df['close'], timeperiod=50)
    
    # اضافه کردن تحلیل امواج الیوت و پرایس اکشن
    df = apply_elliott_wave(df)
    df = apply_price_action(df)
    
    # تنظیم سیگنال‌های خرید و فروش
    df['buy_signal'] = np.where((df['RSI'] < 30) & (df['close'] > df['SMA']), 1, 0)
    df['sell_signal'] = np.where((df['RSI'] > 70) & (df['close'] < df['SMA']), 1, 0)

    # اضافه کردن سایر استراتژی‌های لازم
    df['buy_signal'] = np.where((df['bullish_engulfing'] > 0) | (df['doji'] > 0) | (df['morning_star'] > 0), 1, df['buy_signal'])
    df['sell_signal'] = np.where((df['bullish_engulfing'] < 0) | (df['doji'] < 0) | (df['morning_star'] < 0), 1, df['sell_signal'])

    return df

# تابع برای تحلیل سیگنال‌ها
def analyze_signals(symbol, interval='1h', start_date='2023-01-01', end_date=datetime.now().strftime('%Y-%m-%d')):
    df = get_forex_data(symbol, interval, start_date, end_date)
    df = apply_technical_indicators(df)
    
    # خروجی سیگنال‌ها
    buy_signals = df[df['buy_signal'] == 1]
    sell_signals = df[df['sell_signal'] == 1]
    
    return buy_signals, sell_signals

# تعیین نماد فارکس و اجرای تحلیل
symbol = 'EUR/USD'  # به دلخواه تغییر دهید
buy_signals, sell_signals = analyze_signals(symbol)

# نمایش سیگنال‌ها
print("Buy Signals:")
print(buy_signals[['close', 'RSI', 'SMA', 'bullish_engulfing', 'doji', 'morning_star', 'wave_up', 'wave_strength']])
print("\nSell Signals:")
print(sell_signals[['close', 'RSI', 'SMA', 'bullish_engulfing', 'doji', 'morning_star', 'wave_down', 'wave_strength']])
