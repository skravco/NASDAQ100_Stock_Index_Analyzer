import streamlit as st
import pandas as pd
import yfinance as yf

st.title('NASDAQ 100 Analysis App')

st.sidebar.header('User Input Features')
@st.cache_resource
def get_data():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    html = pd.read_html(url, header=0)
    df = html[4]
    return df

def compute_cumulative_return(df):
    percentage_change = df.pct_change()
    cumulative_return = (1 + percentage_change).cumprod() - 1
    cumulative_return = cumulative_return.fillna(0)
    return cumulative_return

df = get_data()
sector = df.groupby('GICS Sector')

# Sidebar sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique)

# Filter data based on selected sector
df_selected_sector = df[df['GICS Sector'].isin(selected_sector)]

symbols = list(df_selected_sector['Ticker'])
dropdown = st.sidebar.multiselect('Select a stock from the list', symbols)

start = st.sidebar.date_input('Start', value=pd.to_datetime('2020-01-01'))
end = st.sidebar.date_input('End', value=pd.to_datetime('today'))

# Display companies in selected sector
st.header('Companies in Selected Sector(s)')
st.write('Total # of Companies: ' + str(df_selected_sector.shape[0]) + '\n')
st.dataframe(df_selected_sector)

if len(dropdown) > 0:
    # Filter data based on selected stock(s)
    selected_tickers = df_selected_sector[df_selected_sector['Ticker'].isin(dropdown)]
    # Calculate cumulative return using filtered data
    df = compute_cumulative_return(yf.download(selected_tickers['Ticker'].tolist(), start, end)['Adj Close'])
    st.write('Plot Cumulative Return of Chosen Stocks')
    st.line_chart(df)
