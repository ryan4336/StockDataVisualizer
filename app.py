#import necessary modules
import requests



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





# -------------------------------------
# GET START AND END DATE AND VERIFY
# -------------------------------------





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
    




if __name__ == "__main__":
    main()
