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


def build_signal_snapshot(counts):
    buy_signals = [
        ('Sequential Buy Daily', counts.seq_buy_count_daily),
        ('Combo Buy Daily', counts.combo_buy_count_daily),
        ('Sequential Buy Weekly', counts.seq_buy_count_weekly),
        ('Combo Buy Weekly', counts.combo_buy_count_weekly),
        ('Sequential 9-13-9 Buy', counts.seq_buy_9_13_9),
        ('Combo 9-13-9 Buy', counts.combo_buy_9_13_9)
    ]
    sell_signals = [
        ('Sequential Sell Daily', counts.seq_sell_count_daily),
        ('Combo Sell Daily', counts.combo_sell_count_daily),
        ('Sequential Sell Weekly', counts.seq_sell_count_weekly),
        ('Combo Sell Weekly', counts.combo_sell_count_weekly),
        ('Sequential 9-13-9 Sell', counts.seq_sell_9_13_9),
        ('Combo 9-13-9 Sell', counts.combo_sell_9_13_9)
    ]

    def strongest_signal(signals):
        label, value = max(signals, key=lambda signal: int(signal[1] or 0))
        return {'label': label, 'count': int(value or 0)}

    strongest_buy = strongest_signal(buy_signals)
    strongest_sell = strongest_signal(sell_signals)
    leading_signal = strongest_buy if strongest_buy['count'] >= strongest_sell['count'] else strongest_sell
    leading_count = leading_signal['count']

    if strongest_buy['count'] > strongest_sell['count']:
        bias = {'label': 'Buy leaning', 'detail': 'Buy counts lead the active setup', 'tone': 'buy'}
    elif strongest_sell['count'] > strongest_buy['count']:
        bias = {'label': 'Sell leaning', 'detail': 'Sell counts lead the active setup', 'tone': 'sell'}
    elif leading_count > 0:
        bias = {'label': 'Balanced pressure', 'detail': 'Buy and sell counts are tied', 'tone': 'balanced'}
    else:
        bias = {'label': 'No active setup', 'detail': 'No DeMark counts are currently active', 'tone': 'inactive'}

    if leading_count >= 13:
        stage = 'Complete'
    elif leading_count >= 10:
        stage = 'Countdown'
    elif leading_count >= 8:
        stage = 'Setup zone'
    elif leading_count > 0:
        stage = 'Building'
    else:
        stage = 'Inactive'

    return {
        'strongest_buy': strongest_buy,
        'strongest_sell': strongest_sell,
        'leading_signal': leading_signal,
        'bias': bias,
        'stage': stage,
        'progress': min(round((leading_count / 13) * 100), 100)
    }


def build_signal_completion_roadmap(counts):
    signal_groups = {
        'buy': [
            ('Sequential Daily', counts.seq_buy_count_daily),
            ('Combo Daily', counts.combo_buy_count_daily),
            ('Sequential Weekly', counts.seq_buy_count_weekly),
            ('Combo Weekly', counts.combo_buy_count_weekly)
        ],
        'sell': [
            ('Sequential Daily', counts.seq_sell_count_daily),
            ('Combo Daily', counts.combo_sell_count_daily),
            ('Sequential Weekly', counts.seq_sell_count_weekly),
            ('Combo Weekly', counts.combo_sell_count_weekly)
        ]
    }

    def build_lane(label, value):
        count = int(value or 0)
        remaining = max(13 - count, 0)

        if count >= 13:
            stage = 'Complete'
            detail = 'Countdown complete'
        elif count >= 10:
            stage = 'Countdown'
            detail = f'{remaining} count{"s" if remaining != 1 else ""} to completion'
        elif count >= 8:
            stage = 'Setup zone'
            detail = f'{remaining} counts to completion'
        elif count > 0:
            stage = 'Building'
            detail = f'{8 - count} count{"s" if 8 - count != 1 else ""} to setup zone'
        else:
            stage = 'Inactive'
            detail = 'No active countdown'

        return {
            'label': label,
            'count': count,
            'remaining': remaining,
            'stage': stage,
            'detail': detail,
            'progress': min(round((count / 13) * 100), 100)
        }

    return {
        direction: [build_lane(label, value) for label, value in signals]
        for direction, signals in signal_groups.items()
    }


def build_group_signal_watch(counts, limit=5):
    peers = Counts.query.filter(
        Counts.etf == counts.etf,
        Counts.ticker != counts.ticker
    ).all()

    def signal_strengths(item):
        buy_strength = max(
            int(item.seq_buy_count_daily or 0),
            int(item.combo_buy_count_daily or 0),
            int(item.seq_buy_count_weekly or 0),
            int(item.combo_buy_count_weekly or 0),
            int(item.seq_buy_9_13_9 or 0),
            int(item.combo_buy_9_13_9 or 0)
        )
        sell_strength = max(
            int(item.seq_sell_count_daily or 0),
            int(item.combo_sell_count_daily or 0),
            int(item.seq_sell_count_weekly or 0),
            int(item.combo_sell_count_weekly or 0),
            int(item.seq_sell_9_13_9 or 0),
            int(item.combo_sell_9_13_9 or 0)
        )
        return buy_strength, sell_strength

    current_buy, current_sell = signal_strengths(counts)
    current_direction = 'buy' if current_buy > current_sell else 'sell' if current_sell > current_buy else 'balanced'
    active_peers = []

    for peer in peers:
        buy_strength, sell_strength = signal_strengths(peer)
        strength = max(buy_strength, sell_strength)

        if strength == 0:
            continue

        direction = 'buy' if buy_strength > sell_strength else 'sell' if sell_strength > buy_strength else 'balanced'

        if strength >= 13:
            stage = 'Complete'
        elif strength >= 10:
            stage = 'Countdown'
        elif strength >= 8:
            stage = 'Setup zone'
        else:
            stage = 'Building'

        active_peers.append({
            'ticker': peer.ticker,
            'name': re.sub(r"(?<!\b)\w", lambda match: match.group().lower(), peer.name_of_company).replace('\\', ' '),
            'buy_strength': buy_strength,
            'sell_strength': sell_strength,
            'strength': strength,
            'direction': direction,
            'direction_label': direction.title(),
            'stage': stage,
            'matches_bias': direction == current_direction
        })

    active_peers.sort(
        key=lambda peer: (peer['matches_bias'], peer['strength'], peer['buy_strength'] + peer['sell_strength']),
        reverse=True
    )

    return {
        'group': counts.etf,
        'active_count': len(active_peers),
        'peers': active_peers[:limit]
    }


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

        signal_snapshot = build_signal_snapshot(row)
        signal_completion_roadmap = build_signal_completion_roadmap(row)
        group_signal_watch = build_group_signal_watch(row)

        price = price.reset_index()

        price['Date'] = price['Date'].dt.date.astype(str)

        price_data = price.to_json(orient='records', date_format='iso')

        json_news = json.dumps(news).replace("\\", "")

        company_site = company_info.get('website')
        if company_site:
            company_site = company_site.replace("https://www.", "")

        return render_template('stock_info.html', price_data=price_data, company_info=company_info, ticker=tick,
                               demark_counts=row, news=json_news, major_holders=major_holders,
                               company_site=company_site, signal_snapshot=signal_snapshot,
                               signal_completion_roadmap=signal_completion_roadmap,
                               group_signal_watch=group_signal_watch)


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

    sector_weight_labels = [
        'Real Estate',
        'Consumer Cyclical',
        'Basic Materials',
        'Consumer Defensive',
        'Technology',
        'Communication Services',
        'Financial Services',
        'Utilities',
        'Industrials',
        'Energy',
        'Healthcare'
    ]
    top_sector = None

    if sector_weights is not None:
        sector_weights = sector_weights.reset_index().values.tolist()
        weighted_sectors = []

        for idx, row in enumerate(sector_weights):
            if len(row) > 1 and row[1] is not None and pd.notna(row[1]):
                weighted_sectors.append({
                    'name': sector_weight_labels[idx] if idx < len(sector_weight_labels) else row[0],
                    'weight': row[1]
                })

        if weighted_sectors:
            top_sector = max(weighted_sectors, key=lambda sector: sector['weight'])

    top_holding = None
    holdings = holding_info.get(tick, {}).get('holdings') if holding_info else None

    if holdings:
        top_holding = holdings[0]

    etf_snapshot = {
        'expense_ratio': profile.get(tick, {}).get('feesExpensesInvestment', {}).get('annualReportExpenseRatio'),
        'net_assets': profile.get(tick, {}).get('feesExpensesInvestment', {}).get('totalNetAssets'),
        'ytd_return': performance.get(tick, {}).get('trailingReturnsNav', {}).get('ytd'),
        'top_sector': top_sector,
        'top_holding': top_holding
    }

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
                           performance=performance,
                           etf_snapshot=etf_snapshot
                           )


