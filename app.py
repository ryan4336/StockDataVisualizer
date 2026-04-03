#import necessary modules
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import webbrowser
import os
import tempfile

API_KEY = "XAUMT7K9CR2S8LVB"
"""
API KEY LIMITS:
Daily Limit: You can make a maximum of 25 API requests in a 24-hour period.
Per-Minute Limit: You are limited to 5 API requests per minute.
"""

# ------------------------------
# GET STOCK SYMBOL AND VERIFY
# ------------------------------
def get_symbol():
    
    # Prompt the user for a stock symbol and verify it exists in Alpha Vantage.
    # Returns a valid symbol (uppercase).
    
    while True:
        symbol = input("Enter stock symbol (e.g., AAPL): ").upper()

        # Basic validation: only letters/numbers
        if not symbol.isalpha():
            print("Invalid symbol. Please enter letters only.\n")
            continue

        # Call Alpha Vantage to verify symbol
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": API_KEY
        }

        # Make the API request and handle potential errors
        try:
            response = requests.get(url, params=params)
            data = response.json()
        except Exception:
            print("Error: Could not reach Alpha Vantage API. Try again.\n")
            continue

        # Check for invalid symbol
        if "Error Message" in data:
            print(f"Error: '{symbol}' is not a valid stock symbol or has no data.\n")
            continue
        if "Information" in data:
            print("Error: API request limit reached for today.")
            exit(0)
            return

        # Symbol is valid
        print(f"Symbol '{symbol}' is valid.")
        return symbol

# ------------------------------
# GET CHART TYPE AND VERIFY
# ------------------------------
def get_chart_type():
    chart_types = {
        "1": "Bar",
        "2": "Line"
    }

    while True:
        print("\nChart Types:\n----------------\n1. Bar\n2. Line\n")
        chart_type = input("Enter chart type you want (1, 2): ")
        if not chart_type in ["1", "2"]:
            print("Invalid chart type. Please enter 1 or 2.\n")
            continue
        break

    return chart_types[chart_type]


# -------------------------------------
# GET TIME SERIES FUNCTION AND VERIFY
# -------------------------------------
def get_time_series():
    time_series_options = {
        "1": ("Intraday", "TIME_SERIES_INTRADAY"),
        "2": ("Daily", "TIME_SERIES_DAILY"),
        "3": ("Weekly", "TIME_SERIES_WEEKLY"),
        "4": ("Monthly", "TIME_SERIES_MONTHLY")
    }
    while True:
        print("\nTime Series Functions:\n----------------")
        for key, (label, _) in time_series_options.items():
            print(f"{key}. {label}")
        print()

        choice = input("Enter the time series function you want (1-4): ")
        if choice not in time_series_options:
            print("Invalid choice. Choose a number between 1 and 4.\n")
            continue
        label, api_function = time_series_options[choice]
        print(f"Time series '{label}' selected.")
        return api_function


# -------------------------------------
# GET START AND END DATE AND VERIFY
# -------------------------------------
def get_date_range():
    date_format = "%Y-%m-%d"

    def parse_date(date):
        while True:
            date_str = input(date).strip()
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.\n")
    while True:
        start_date = parse_date("Enter the start date (YYYY-MM-DD): ")
        end_date = parse_date("Enter the end date (YYYY-MM-DD): ")

        if end_date < start_date:
            print("ERROR: End date can not be before start date. Try again.\n")
            continue

        print(f"Date range set: {start_date.strftime(date_format)} to {end_date.strftime(date_format)}")
        return start_date.strftime(date_format), end_date.strftime(date_format)


# -------------------------------------
# FETCH STOCK DATA FROM API
# -------------------------------------
def fetch_stock_data(symbol, time_series):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": time_series,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": API_KEY
    }
    if time_series == "TIME_SERIES_INTRADAY":
        params["interval"] = "60min"

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception:
        print("Error: Could not reach Alpha Vantage API.")
        return None, None

    if "Error Message" in data:
        print("Error: Could not retrieve data for that symbol.")
        return None, None
    if "Information" in data:
        print("Error: API request limit reached.")
        return None, None

    # Find the time series key in the response
    time_series_key = next((k for k in data if "Time Series" in k), None)
    if not time_series_key:
        print("Error: Unexpected API response format.")
        return None, None

    return data, time_series_key


# -------------------------------------
# GENERATE CHART AND OPEN IN BROWSER
# -------------------------------------
def generate_chart(stock_data, symbol, chart_type, start_date, end_date, time_series_key):
    """
    Generates a stock chart and opens it in the user's default browser.
    Parameters:
        stock_data (dict)    : Raw JSON data from Alpha Vantage API
        symbol (str)         : Stock ticker e.g. "AAPL"
        chart_type (str)     : "Bar" or "Line"
        start_date (str)     : "YYYY-MM-DD"
        end_date (str)       : "YYYY-MM-DD"
        time_series_key (str): The key inside stock_data e.g. "Time Series (Daily)"
    """
    # Pull out the time series data from the API response
    try:
        time_series = stock_data[time_series_key]
    except KeyError:
        print(f"Error: Could not find '{time_series_key}' in the API data.")
        print("Available keys:", list(stock_data.keys()))
        return

    # Convert the data into a DataFrame
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.columns = [col.split(". ")[1] for col in df.columns]
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df = df.sort_index()

    # Filter to the user's chosen date range
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    df_filtered = df[(df.index >= start) & (df.index <= end)]

    if df_filtered.empty:
        print("No data found for that date range. Try different dates.")
        return

    # Build the chart
    fig = go.Figure()

    if chart_type.lower() == "line":
        fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["open"],
            mode="lines", name="Open", line=dict(color="blue", width=2)))
        fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["high"],
            mode="lines", name="High", line=dict(color="green", width=2)))
        fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["low"],
            mode="lines", name="Low", line=dict(color="red", width=2)))
        fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["close"],
            mode="lines", name="Close", line=dict(color="orange", width=2)))

    elif chart_type.lower() == "bar":
        fig.add_trace(go.Bar(x=df_filtered.index, y=df_filtered["open"],
            name="Open", marker_color="blue"))
        fig.add_trace(go.Bar(x=df_filtered.index, y=df_filtered["high"],
            name="High", marker_color="green"))
        fig.add_trace(go.Bar(x=df_filtered.index, y=df_filtered["low"],
            name="Low", marker_color="red"))
        fig.add_trace(go.Bar(x=df_filtered.index, y=df_filtered["close"],
            name="Close", marker_color="orange"))

    else:
        print(f"Unknown chart type '{chart_type}'. Please enter 'Bar' or 'Line'.")
        return

    # Style the chart
    fig.update_layout(
        title=f"{symbol} Stock Price ({start_date} to {end_date})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        template="plotly_white",
        hovermode="x unified",
        barmode="group"
    )

    # Save as HTML and open in browser
    tmp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=".html", prefix=f"{symbol}_chart_"
    )
    fig.write_html(tmp_file.name)
    tmp_file.close()
    webbrowser.open(f"file://{os.path.abspath(tmp_file.name)}")
    print(f"Chart opened in your browser!")


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    symbol = get_symbol()
    chart_type = get_chart_type()
    time_series = get_time_series()
    start_date, end_date = get_date_range()

    print("\nFetching stock data...")
    stock_data, time_series_key = fetch_stock_data(symbol, time_series)

    if stock_data is None:
        print("Could not retrieve stock data. Exiting.")
        return

    generate_chart(stock_data, symbol, chart_type, start_date, end_date, time_series_key)


if __name__ == "__main__":
    main()



