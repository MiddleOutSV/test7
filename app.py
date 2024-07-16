import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from ta.momentum import RSIIndicator
from pytrends.request import TrendReq

# 구글 트렌드 데이터 가져오기
def get_google_trends(tickers):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(tickers, timeframe='today 3-m')
    trends_data = pytrends.interest_over_time()
    return trends_data.mean()

# 금융 데이터 가져오기
def get_financial_data(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data[ticker] = {
            'EBITDA': stock.financials.loc['EBITDA'].iloc[0] if 'EBITDA' in stock.financials else 0,
            'Total Assets': stock.balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in stock.balance_sheet else 0,
            'Total Capitalization': stock.balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in stock.balance_sheet else 0,
            'Free Cash Flow': stock.cashflow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in stock.cashflow else 0,
            'Beta': stock.info.get('beta', 0)
        }
    return pd.DataFrame(data).T

# RSI 데이터 가져오기
def get_rsi(tickers):
    rsi_data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='6mo')
        rsi = RSIIndicator(hist['Close']).rsi()
        rsi_data[ticker] = rsi.iloc[-1]
    return pd.Series(rsi_data)

# Streamlit 앱
st.title('Trump Beneficiary Stocks Comparison')

tickers = ['DJT', 'GEO', 'AXON', 'CDMO', 'BRCC', 'INTC']

# Google Trends Data
st.header('Google Trends Data')
google_trends = get_google_trends(tickers)
trends_df = pd.DataFrame(google_trends, columns=['Interest'])
fig = px.scatter(trends_df, x=trends_df.index, y='Interest', size='Interest', color='Interest', 
                 color_continuous_scale='Viridis', title='Google Trends Interest')
st.plotly_chart(fig)

# RSI Data
st.header('RSI Data')
rsi_data = get_rsi(tickers)
rsi_df = pd.DataFrame(rsi_data, columns=['RSI'])
rsi_df['Color'] = rsi_df['RSI'].apply(lambda x: 'red' if x > 50 else 'blue')
fig = px.scatter(rsi_df, x=rsi_df.index, y='RSI', size='RSI', color='Color', 
                 color_discrete_map={'red':'red', 'blue':'blue'}, title='RSI')
st.plotly_chart(fig)

# Financial Data
financial_data = get_financial_data(tickers)

st.header('Financial Data')
st.subheader('EBITDA & Free Cash Flow')
ebitda_fcf_df = financial_data[['EBITDA', 'Free Cash Flow']]
fig = px.bar(ebitda_fcf_df, x=ebitda_fcf_df.index, y=['EBITDA', 'Free Cash Flow'], 
             title='EBITDA and Free Cash Flow')
st.plotly_chart(fig)

st.subheader('Total Assets, Total Capitalization & Beta')
other_financials_df = financial_data[['Total Assets', 'Total Capitalization', 'Beta']]
fig = px.scatter(other_financials_df, x=other_financials_df.index, 
                 size='Total Assets', color='Beta', title='Total Assets and Beta')
st.plotly_chart(fig)

fig = px.scatter(other_financials_df, x=other_financials_df.index, 
                 size='Total Capitalization', color='Beta', title='Total Capitalization and Beta')
st.plotly_chart(fig)
