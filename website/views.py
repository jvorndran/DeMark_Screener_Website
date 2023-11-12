import pandas as pd
from website import app
from flask import render_template, redirect, url_for
from website.models import Counts
import re
import yfinance as yf
from datetime import datetime, timedelta
import json
from yahooquery import Ticker


@app.route('/')
def screener():

    data = Counts.query.all()

    counts_data = []

    for item in data:

        #Makes sure only first letter of word is uppercase in company name
        converted_name = re.sub(r"(?<!\b)\w", lambda x: x.group().lower(), item.name_of_company)

        #Replaces escape characters
        converted_name = converted_name.replace('\\', ' ')

        #Makes count dict for each count
        count = {
            'name': converted_name,
            'tick': item.ticker,
            'etf': item.etf,
            'seq_buy_d': item.seq_buy_count_daily,
            'seq_sell_d': item.seq_sell_count_daily,
            'seq_buy_w': item.seq_buy_count_weekly,
            'seq_sell_w': item.seq_sell_count_weekly,
            'seq_b_9139': item.seq_buy_9_13_9,
            'seq_s_9139': item.seq_sell_9_13_9,
            'combo_buy_d': item.combo_buy_count_daily,
            'combo_sell_d': item.combo_sell_count_daily,
            'combo_buy_w': item.combo_buy_count_weekly,
            'combo_sell_w': item.combo_sell_count_weekly,
            'combo_b_9139': item.combo_buy_9_13_9,
            'combo_s_9139': item.combo_sell_9_13_9
        }
        counts_data.append(count)

    return render_template('screener.html', counts=counts_data)


def get_stock_details(tick):

    ticker = yf.Ticker(tick)

    start_date = datetime.now() - timedelta(days=365)

    price_data = yf.download(tick, start=start_date.strftime('%Y-%m-%d'))

    info = ticker.info

    news = ticker.news

    return price_data, info, news


def check_if_etf(tick):

    row = Counts.query.filter_by(ticker=tick).first()

    sector = row.etf

    if sector == 'ETF':
        return True
    else:
        return False


@app.route('/screener/<tick>')
def stock_details(tick):

    is_etf = check_if_etf(tick)

    if is_etf:
        return redirect(url_for('etf_details', tick=tick))
    else:

        stock = Ticker(tick)

        major_holders = stock.major_holders

        price, company_info, news = get_stock_details(tick)

        row = Counts.query.filter_by(ticker=tick).first()

        price = price.reset_index()

        price['Date'] = price['Date'].dt.date.astype(str)

        price_data = price.to_json(orient='records', date_format='iso')

        json_news = json.dumps(news).replace("\\", "")

        company_site = company_info.get('website')
        if company_site:
            company_site = company_site.replace("https://www.", "")

        return render_template('stock_info.html', price_data=price_data, company_info=company_info, ticker=tick,
                               demark_counts=row, news=json_news, major_holders=major_holders,
                               company_site=company_site)


@app.route('/etf/<tick>')
def etf_details(tick):

    counts = Counts.query.filter_by(ticker=tick).first()

    t = Ticker(tick)
    profile = t.fund_profile
    holding_info = t.fund_holding_info

    try:
        sector_weights = t.fund_sector_weightings

    except KeyError:
        sector_weights = None

    quote = t.quote_type
    summary = t.summary_profile
    performance = t.fund_performance

    if sector_weights is not None:
        sector_weights = sector_weights.reset_index().values.tolist()

    start_date = datetime.now() - timedelta(days=365)
    price_data = yf.download(tick, start=start_date.strftime('%Y-%m-%d'))
    price_data = price_data.reset_index()
    price_data['Date'] = price_data['Date'].dt.date.astype(str)
    price_data = price_data.to_json(orient='records', date_format='iso')

    print(profile)

    return render_template('etf_details.html', ticker=tick, demark_counts=counts,
                           price_data=price_data,
                           profile=profile, holding_info=holding_info,
                           sector_weights=sector_weights,
                           quote=quote, summary=summary,
                           performance=performance
                           )


