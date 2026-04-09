from chart_generator import generate_chart

# Fake data that looks exactly like what Alpha Vantage sends back
fake_data = {
    "Time Series (Daily)": {
        "2024-03-01": {"1. open": "170", "2. high": "175", "3. low": "168", "4. close": "173", "5. volume": "5000000"},
        "2024-03-04": {"1. open": "173", "2. high": "178", "3. low": "171", "4. close": "176", "5. volume": "4800000"},
        "2024-03-05": {"1. open": "176", "2. high": "180", "3. low": "174", "4. close": "178", "5. volume": "5200000"},
        "2024-03-06": {"1. open": "178", "2. high": "182", "3. low": "176", "4. close": "180", "5. volume": "4600000"},
        "2024-03-07": {"1. open": "180", "2. high": "185", "3. low": "179", "4. close": "184", "5. volume": "5100000"},
    }
}

# Test line chart
generate_chart(
    stock_data=fake_data,
    symbol="AAPL",
    chart_type="line",
    start_date="2024-03-01",
    end_date="2024-03-07",
    time_series_key="Time Series (Daily)"
)