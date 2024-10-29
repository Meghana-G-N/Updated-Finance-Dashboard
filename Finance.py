import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt

# Title of the dashboard
st.title('Lit Finance Dashboard')

# Define tickers
tickers = ('TSLA', 'AAPL', 'MSFT', 'BTC-USD', 'ETH-USD')
dropdown = st.multiselect('Pick your assets', tickers)

# Define date input
start = st.date_input('Start', value=pd.to_datetime('2021-01-01'))
end = st.date_input('End', value=pd.to_datetime('today'))

# Function to calculate relative returns
def relativeret(df):
    rel = df.pct_change()
    cumret = (1 + rel).cumprod() - 1
    cumret = cumret.fillna(0)
    return cumret

# Function to calculate risk metrics
def calculate_risk_metrics(df):
    daily_returns = df.pct_change().dropna()
    metrics = {
        'Annualized Volatility': daily_returns.std() * np.sqrt(252),
        'Annualized Return': daily_returns.mean() * 252,
        'Sharpe Ratio': (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
    }
    return pd.DataFrame(metrics, index=['Value'])

if len(dropdown) > 0:
    df = yf.download(dropdown, start, end)['Adj Close']
    cumret = relativeret(df)
    risk_metrics = calculate_risk_metrics(df)
    
    st.header('Returns of {}'.format(dropdown))
    st.line_chart(cumret)
    
    st.header('Risk Metrics')
    st.write(risk_metrics)
    
    st.header('Candlestick Chart')
    for asset in dropdown:
        asset_data = yf.download(asset, start, end)
        st.subheader(f'Candlestick Chart for {asset}')
        
        base = alt.Chart(asset_data.reset_index()).encode(
            x='Date:T',
            tooltip=['Date:T', 'Open:Q', 'High:Q', 'Low:Q', 'Close:Q']
        )
        
        rule = base.mark_rule().encode(
            y='Low:Q',
            y2='High:Q'
        )
        
        bars = base.mark_bar().encode(
            y='Open:Q',
            y2='Close:Q',
            color=alt.condition("datum.Open < datum.Close", alt.value("green"), alt.value("red"))
        )
        
        candlestick_chart = rule + bars
        
        st.altair_chart(candlestick_chart, use_container_width=True)
