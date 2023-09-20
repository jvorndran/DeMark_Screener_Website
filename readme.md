# Screener for DeMark Indicators
This app screens over 7,000 stocks for various indicators in the DeMark suite. DeMark indicators are
used widely in the institutional investment community. However, they are behind a very steep paywall. The
cheapest platform to get them on is $250 a month.

# Features
It is just a single page application (literally), with a easy to navigate table of all stocks status for various
indicators. This screener supports the three most popular indicators, the TD Sequential, the TD Combo, and the 
9-13-9. These indicators are calculated on a weekly and daily timeframe. Most likely none of this makes sense. 
If you would like to read more about how they work there is a overview with examples under the table.

# Usage
After cloning the project, use the command "npm install" to download the node dependencies, then use the command 
"pip install -r requirements.txt" to download the python dependencies. Then you should be ready to run the server. 
There is a script that populates the database with the total of 14 indicators (populate_db.py). It downloads
around 1 year of price data for 7,000 stocks so it takes a long time to execute (normally around 3 hours). 
Then you run main.py and the server will start.

# Tech Used
For the backend Flask was used. For the frontend, jinja2 templates were used and rendered on the server. For 
the database sqlite was used.

