#import necessary modules
import requests
import webbrowser
import os
from datetime import datetime


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
    
    while True:
        symbol = input("Enter stock symbol (e.g., AAPL): ").upper()

        if not symbol.isalpha():
            print("Invalid symbol. Please enter letters only.\n")
            continue

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": API_KEY
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
        except Exception:
            print("Error: Could not reach Alpha Vantage API. Try again.\n")
            continue

        if "Error Message" in data:
            print(f"Error: '{symbol}' is not a valid stock symbol or has no data.\n")
            continue
        if "Information" in data:
            print("Error: API request limit reached for today.")
            exit(0)
            return

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
# FETCH DATA FROM API
# -------------------------------------
def fetch_data(symbol, time_series):
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
        print("Error: Could not reach the API.")
        exit(1)

    if "Error Message" in data:
        print("Error: Invalid request to API.")
        exit(1)
    if "Information" in data:
        print("Error: API request limit reached for today.")
        exit(0)

    # Find the time series key in the response
    ts_key = None
    for key in data:
        if "Time Series" in key:
            ts_key = key
            break

    if ts_key is None:
        print("Error: Could not find time series data in API response.")
        exit(1)

    return data[ts_key]


# -------------------------------------
# FILTER DATA BY DATE RANGE
# -------------------------------------
def filter_data(time_series_data, start_date, end_date):
    filtered = {}
    for date_str, values in time_series_data.items():
        date_only = date_str.split(" ")[0]
        if start_date <= date_only <= end_date:
            filtered[date_str] = values

    if not filtered:
        print("No data found for the selected date range. Try a wider range.")
        exit(0)

    return filtered


# -------------------------------------
# GENERATE CHART AND OPEN IN BROWSER
# -------------------------------------
def generate_chart(filtered_data, symbol, chart_type, start_date, end_date):
    # Sort dates oldest to newest
    sorted_dates = sorted(filtered_data.keys())

    # Pull the closing price for each date
    closes = []
    for date_str in sorted_dates:
        values = filtered_data[date_str]
        close_key = [k for k in values if "close" in k.lower()]
        if close_key:
            closes.append(float(values[close_key[0]]))
        else:
            closes.append(0.0)

    labels_js = str(sorted_dates)
    values_js = str(closes)
    chart_js_type = "bar" if chart_type == "Bar" else "line"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{symbol} Stock Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px;
        }}
        h1 {{ color: #333; }}
        p {{ color: #666; }}
        .chart-container {{
            width: 90vw;
            max-width: 1100px;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
    </style>
</head>
<body>
    <h1>{symbol} Closing Price</h1>
    <p>{start_date} to {end_date}</p>
    <div class="chart-container">
        <canvas id="stockChart"></canvas>
    </div>
    <script>
        const labels = {labels_js};
        const values = {values_js};
        const ctx = document.getElementById('stockChart').getContext('2d');
        new Chart(ctx, {{
            type: '{chart_js_type}',
            data: {{
                labels: labels,
                datasets: [{{
                    label: '{symbol} Closing Price',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    pointRadius: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'top' }},
                    title: {{
                        display: true,
                        text: '{symbol} Stock Price ({start_date} to {end_date})'
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'Closing Price (USD)' }}
                    }},
                    x: {{
                        title: {{ display: true, text: 'Date' }},
                        ticks: {{ maxTicksLimit: 20 }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    # Save the HTML file and open in browser
    filepath = os.path.abspath("stock_chart.html")
    with open(filepath, "w") as f:
        f.write(html)

    webbrowser.open(f"file://{filepath}")
    print(f"Chart opened in your browser.")


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    symbol = get_symbol()
    chart_type = get_chart_type()
    time_series = get_time_series()
    start_date, end_date = get_date_range()

    print("\nFetching data from Alpha Vantage...")
    raw_data = fetch_data(symbol, time_series)

    print("Filtering data by date range...")
    filtered = filter_data(raw_data, start_date, end_date)

    print("Generating chart...")
    generate_chart(filtered, symbol, chart_type, start_date, end_date)


if __name__ == "__main__":
    main()

