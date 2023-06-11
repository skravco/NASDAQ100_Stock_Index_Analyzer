import streamlit as st
import pandas as pd
import yfinance as yf

class Nasdaq100App:
    def __init__(self):
        self.data_cache = st.cache_resource(self.fetch_data)  # Cache the fetch_data method to improve performance

    def fetch_data(self):
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        html = pd.read_html(url, header=0)  # Read the HTML table from the Wikipedia page
        df = html[4]  # Select the desired table from the HTML
        return df

    def select_stocks(self, df_selected_sector):
        if df_selected_sector is None or df_selected_sector.empty:
            st.sidebar.warning("Select sector to begin.")  # Display a warning if no sector is selected
            return None

        symbols = list(df_selected_sector['Ticker'])  # Get the list of ticker symbols from the selected sector
        dropdown = st.sidebar.multiselect('Stock(s)', symbols)  # Allow the user to select multiple stocks
        return dropdown

    def select_weights(self, dropdown):
        if len(dropdown) == 1:
            return {}  # Return an empty dictionary if only one ticker is selected

        weights = {}
        for stock in dropdown:
            weight = st.sidebar.slider(f"Weight for {stock}", 0.0, 1.0, 0.5, 0.1)  # Allow the user to set weights for each stock
            weights[stock] = weight
        return weights

    def filter_data(self, df_selected_sector, dropdown):
        if len(dropdown) > 0:
            selected_tickers = df_selected_sector[df_selected_sector['Ticker'].isin(dropdown)]  # Filter the selected stocks
            return selected_tickers
        return None

    def single_stock_cumulative_return(self, df):
        percentage_change = df.pct_change()
        cumulative_return = (1 + percentage_change).cumprod() - 1  # Calculate the cumulative return of a single stock
        cumulative_return = cumulative_return.fillna(0)
        return cumulative_return

    def portfolio_cumulative_return(self, selected_tickers, weights, start, end):
        if selected_tickers is None:
            st.sidebar.warning("Please select ticker(s) to proceed.")  # Display a warning if no tickers are selected
            return None
    
        if len(selected_tickers) > 1:
            sum_of_weights = sum(weights.values())
            if abs(sum_of_weights - 1.0) > 0.01:  # Check if the sum of weights is not close to 1
                st.sidebar.warning("The total sum of weights is not 1.0. Rounding to 1.0.")
                if sum_of_weights != 0.0:
                    weights = {k: v / sum_of_weights for k, v in weights.items()}  # Normalize the weights
                else:
                    weights = {k: 1.0 / len(selected_tickers) for k in weights.keys()}  # Assign equal weights
    
            data = yf.download(selected_tickers['Ticker'].tolist(), start, end)['Adj Close']  # Download the stock data from Yahoo Finance
            data = data.pct_change().fillna(0)  # Calculate the percentage change of the stock prices
            weighted_returns = (data * pd.Series(weights)).sum(axis=1)  # Calculate the weighted returns of the portfolio
            cumulative_return = (1 + weighted_returns).cumprod() - 1  # Calculate the cumulative return of the portfolio
            cumulative_return = cumulative_return

            cumulative_return = cumulative_return.fillna(0)
            return cumulative_return
        else:
            data = yf.download(selected_tickers['Ticker'].tolist(), start, end)['Adj Close']  # Download the stock data from Yahoo Finance
            cumulative_return = self.single_stock_cumulative_return(data)  # Calculate the cumulative return of a single stock
            return cumulative_return

    def main(self):
        st.title('NASDAQ 100 Analysis App')

        st.sidebar.header('User Input Features')

        start = st.sidebar.date_input('Start', value=pd.to_datetime('2020-01-01'), key='begin_period_input')  # Get the start date from the user
        end = st.sidebar.date_input('End', value=pd.to_datetime('today'), key='end_period_input')  # Get the end date from the user

        df = self.data_cache()  # Retrieve the cached data
        sorted_sector_unique = sorted(df['GICS Sector'].unique())  # Get the unique sectors from the data
        selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique)  # Allow the user to select multiple sectors

        df_selected_sector = df[df['GICS Sector'].isin(selected_sector)]  # Filter the data based on selected sectors

        st.header('Companies in Selected Sector(s)')
        st.write('Total # of Companies: ' + str(df_selected_sector.shape[0]))  # Display the number of selected companies
        st.dataframe(df_selected_sector)  # Display the selected companies in a table

        dropdown = self.select_stocks(df_selected_sector)  # Allow the user to select stocks
        if dropdown is None:
            return  # Exit the main method if no sector is selected or available

        weights = self.select_weights(dropdown)  # Allow the user to set weights for selected stocks

        selected_tickers = self.filter_data(df_selected_sector, dropdown)  # Filter the data based on selected stocks

        if selected_tickers is not None:
            df = self.single_stock_cumulative_return(
                yf.download(selected_tickers['Ticker'].tolist(), start, end)['Adj Close']
            )
            st.write('Plot Cumulative Return of Stocks')
            st.line_chart(df)  # Display the cumulative return of selected stocks in a line chart

        cumulative_return = self.portfolio_cumulative_return(selected_tickers, weights, start, end)  # Calculate the cumulative return of the portfolio
        if cumulative_return is not None:
            st.write('Plot Cumulative Return of Portfolio')
            st.line_chart(cumulative_return, )  # Display the cumulative return of the portfolio in a line chart
            st.write(f"Cumulative Return of Portfolio: {cumulative_return.iloc[-1]:.2%}")  # Display the final cumulative return of the portfolio


if __name__ == '__main__':
    app = Nasdaq100App()
    app.main()
