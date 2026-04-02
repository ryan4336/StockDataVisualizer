import pandas as pd
import plotly.graph_objects as go
import webbrowser
import os
import tempfile


def generate_chart(stock_data, symbol, chart_type, start_date, end_date, time_series_key):
    """
    Generates a stock chart and opens it in the user's default browser.

    Parameters:
        stock_data (dict)    : Raw JSON data from Alpha Vantage API
        symbol (str)         : Stock ticker e.g. "AAPL"
        chart_type (str)     : "bar" or "line"
        start_date (str)     : "YYYY-MM-DD"
        end_date (str)       : "YYYY-MM-DD"
        time_series_key (str): The key inside stock_data e.g. "Time Series (Daily)"
    """

    # --- Pull out the time series data from the API response ---
    try:
        time_series = stock_data[time_series_key]
    except KeyError:
        print(f"Error: Could not find '{time_series_key}' in the API data.")
        print("Available keys:", list(stock_data.keys()))
        return

    # --- Convert the data into a table (DataFrame) ---
    df = pd.DataFrame.from_dict(time_series, orient="index")

    # Clean up column names: "1. open" becomes "open", etc.
    df.columns = [col.split(". ")[1] for col in df.columns]

    # Convert dates and numbers to proper types
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df = df.sort_index()  # oldest date first

    # --- Filter to only show the date range the user chose ---
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    df_filtered = df[(df.index >= start) & (df.index <= end)]

    if df_filtered.empty:
        print("No data found for that date range. Try different dates.")
        return

    # --- Build the chart based on what type the user chose ---
    fig = go.Figure()

    if chart_type.lower() == "line":
        fig.add_trace(go.Scatter(
            x=df_filtered.index, y=df_filtered["open"],
            mode="lines", name="Open",
            line=dict(color="blue", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_filtered.index, y=df_filtered["high"],
            mode="lines", name="High",
            line=dict(color="green", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_filtered.index, y=df_filtered["low"],
            mode="lines", name="Low",
            line=dict(color="red", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_filtered.index, y=df_filtered["close"],
            mode="lines", name="Close",
            line=dict(color="orange", width=2)
        ))

    elif chart_type.lower() == "bar":
        fig.add_trace(go.Bar(
            x=df_filtered.index, y=df_filtered["open"],
            name="Open", marker_color="blue"
        ))
        fig.add_trace(go.Bar(
            x=df_filtered.index, y=df_filtered["high"],
            name="High", marker_color="green"
        ))
        fig.add_trace(go.Bar(
            x=df_filtered.index, y=df_filtered["low"],
            name="Low", marker_color="red"
        ))
        fig.add_trace(go.Bar(
            x=df_filtered.index, y=df_filtered["close"],
            name="Close", marker_color="orange"
        ))

    else:
        print(f"Unknown chart type '{chart_type}'. Please enter 'bar' or 'line'.")
        return

    # --- Style the chart ---
    fig.update_layout(
        title=f"{symbol} Stock Price ({start_date} to {end_date})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        template="plotly_white",
        hovermode="x unified",
        barmode="group"
    )

    # --- Save as HTML and open in browser ---
    tmp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=".html", prefix=f"{symbol}_chart_"
    )
    fig.write_html(tmp_file.name)
    tmp_file.close()

    webbrowser.open(f"file://{os.path.abspath(tmp_file.name)}")
    print(f"Chart opened in your browser!")