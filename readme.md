# DeMark Indicator Screener

This Flask app screens roughly 7,000 stocks for a few DeMark indicator setups and renders the results in a
single server-rendered interface.

## Highlights

- Daily and weekly TD Sequential, TD Combo, and 9-13-9 signals
- ETF drill-down pages and individual stock detail views
- SQLite-backed data populated from downloaded market data

## Local setup

1. Create and activate a Python virtual environment.
2. Install the Python dependencies with `pip install -r requirements.txt`.
3. If you need the legacy Node dependency captured in `package.json`, run `npm install`.
4. Run `python populate_db.py` to rebuild the SQLite database. This downloads about a year of price history for
   thousands of tickers, so it can take a few hours to finish.
5. Start the development server with `python main.py`.

The Flask app stores its SQLite database at `instance/database.db`.

## Stack

- Flask with Jinja templates
- SQLAlchemy with SQLite
- pandas, `yfinance`, and `yahooquery` for market data processing

