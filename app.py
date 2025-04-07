import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta  # technical analysis library

st.set_page_config(page_title="Saham Signal Pro", layout="wide")
st.title("Saham Signal Pro - IDX Edition")

# Fungsi untuk ambil data IDX harian
@st.cache_data
def get_idx_data():
    url = "https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/StockSummary/stock_summary.csv"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        df = df[['Kode Emiten', 'Penutupan', 'Volume']]  # Simplifikasi
        df.columns = ['Kode', 'Close', 'Volume']
        df = df.dropna()
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

# Fungsi ambil data historis dari yfinance
def get_historical_data_yf(kode):
    try:
        ticker = f"{kode}.JK"
        df = yf.download(ticker, period="6mo")
        df = df[['Close']].reset_index()
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data historis untuk {kode}: {e}")
        return pd.DataFrame()

# Analisis teknikal
def analyze_stock(df_hist):
    df_hist = df_hist.copy()
    df_hist['MA50'] = df_hist['Close'].rolling(50).mean()
    df_hist['MA70'] = df_hist['Close'].rolling(70).mean()
    df_hist['MA120'] = df_hist['Close'].rolling(120).mean()
    df_hist['RSI'] = ta.momentum.RSIIndicator(df_hist['Close']).rsi()
    df_hist['MACD'] = ta.trend.MACD(df_hist['Close']).macd()
    return df_hist

# Deteksi sinyal trading
def generate_signal(df_hist):
    latest = df_hist.dropna().iloc[-1]
    signals = {}
    if latest['Close'] > latest['MA50'] > latest['MA120'] and latest['RSI'] < 70:
        signals['Signal'] = 'BUY'
        signals['Target'] = round(latest['Close'] * 1.05, 2)
        signals['StopLoss'] = round(latest['Close'] * 0.95, 2)
        signals['ExitPlan'] = 'Cut loss jika turun ke SL atau RSI turun < 50'
    else:
        signals['Signal'] = 'WAIT'
        signals['ExitPlan'] = '-'
    return signals

st.sidebar.header("Pengaturan")
selected_stock = st.sidebar.text_input("Kode Saham (Contoh: BBRI)", value="BBRI")

if st.sidebar.button("Analisis Saham"):
    with st.spinner("Mengambil dan menganalisis data..."):
        df_summary = get_idx_data()
        df_hist = get_historical_data_yf(selected_stock)
        if df_hist.empty:
            st.warning("Data historis kosong atau gagal diambil.")
        else:
            df_analyzed = analyze_stock(df_hist)
            signal = generate_signal(df_analyzed)

            st.subheader(f"Analisis Saham: {selected_stock.upper()}")
            st.line_chart(df_analyzed.set_index('Date')[['Close', 'MA50', 'MA120']])

            st.write("**Sinyal Trading:**")
            st.write(f"Sinyal: {signal['Signal']}")
            if signal['Signal'] == 'BUY':
                st.write(f"Target Price: {signal['Target']}")
                st.write(f"Stop Loss: {signal['StopLoss']}")
            st.write(f"Exit Plan: {signal['ExitPlan']}")
