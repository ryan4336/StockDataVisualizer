#import necessary modules
import requests
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
        # If the API returned an error message (symbol doesn't exist or request limit reached)
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
    #Chart types and respective numbers for user selection
    chart_types = {
        "1": "Bar",
        "2": "Line"
    }

    #user input for chart type and validation
    while True:
        print("\nChart Types:\n----------------\n1. Bar\n2. Line\n")
        chart_type = input("Enter chart type you want (1, 2): ")
        if not chart_type in ["1", "2"]:
            print("Invalid chart type. Please enter 1 or 2.\n")
            continue

        break

    #return the selected chart type
    return chart_types[chart_type]




# -------------------------------------
# GET TIME SERIES FUNCTION AND VERIFY
# -------------------------------------
def get_time_series():
    # Time series options and their Alpha Vantage APU function names
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
# FILTER DATA BY DATE RANGE
# -------------------------------------






# -------------------------------------
# GENERATE CHART AND OPEN IN BROWSER
# -------------------------------------





# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    symbol = get_symbol()
    print(symbol)
    chart_type = get_chart_type()
    print(chart_type)
    time_series = get_time_series()
    print(time_series)
    start_date, end_date = get_date_range()
    print(start_date, end_date)
    




if __name__ == "__main__":
    main()
