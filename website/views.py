import pandas as pd
from website import app
from flask import render_template, redirect, url_for, jsonify, request
from website.models import Counts
import re
import yfinance as yf
from datetime import datetime, timedelta
import json
from yahooquery import Ticker


BUY_SIGNAL_FIELDS = ['seq_buy_d', 'combo_buy_d', 'seq_buy_w', 'combo_buy_w', 'seq_b_9139', 'combo_b_9139']
SELL_SIGNAL_FIELDS = ['seq_sell_d', 'combo_sell_d', 'seq_sell_w', 'combo_sell_w', 'seq_s_9139', 'combo_s_9139']
SIGNAL_FAMILIES = {
    'all': BUY_SIGNAL_FIELDS + SELL_SIGNAL_FIELDS,
    'daily': ['seq_buy_d', 'combo_buy_d', 'seq_sell_d', 'combo_sell_d'],
    'weekly': ['seq_buy_w', 'combo_buy_w', 'seq_sell_w', 'combo_sell_w'],
    'sequential': ['seq_buy_d', 'seq_buy_w', 'seq_b_9139', 'seq_sell_d', 'seq_sell_w', 'seq_s_9139'],
    'combo': ['combo_buy_d', 'combo_buy_w', 'combo_b_9139', 'combo_sell_d', 'combo_sell_w', 'combo_s_9139'],
    'nine-thirteen-nine': ['seq_b_9139', 'combo_b_9139', 'seq_s_9139', 'combo_s_9139']
}


def serialize_count(item):
    converted_name = re.sub(r"(?<!\b)\w", lambda match: match.group().lower(), item.name_of_company)

    return {
        'name': converted_name.replace('\\', ' '),
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


def build_signal_feed(rows, direction='all', family='all', minimum=0, group=''):
    family_fields = SIGNAL_FAMILIES[family]
    buy_fields = [field for field in BUY_SIGNAL_FIELDS if field in family_fields]
    sell_fields = [field for field in SELL_SIGNAL_FIELDS if field in family_fields]
    threshold = 0 if minimum == 0 and direction == 'all' and family == 'all' else max(minimum, 1)
    normalized_group = group.strip().lower()
    matches = []

    def strongest_signal(row, fields):
        field = max(fields, key=lambda candidate: int(row.get(candidate) or 0))
        return {'field': field, 'count': int(row.get(field) or 0)}

    for row in rows:
        if normalized_group and normalized_group not in str(row.get('etf') or '').lower():
            continue

        strongest_buy = strongest_signal(row, buy_fields)
        strongest_sell = strongest_signal(row, sell_fields)
        buy_strength = strongest_buy['count']
        sell_strength = strongest_sell['count']

        if direction == 'buy':
            signal_match = buy_strength >= threshold
        elif direction == 'sell':
            signal_match = sell_strength >= threshold
        elif direction == 'both':
            signal_match = buy_strength >= threshold and sell_strength >= threshold
        else:
            signal_match = threshold == 0 or buy_strength >= threshold or sell_strength >= threshold

        if not signal_match:
            continue

        enriched_row = dict(row)
        enriched_row.update({
            'buy_strength': buy_strength,
            'sell_strength': sell_strength,
            'strongest_buy': strongest_buy,
            'strongest_sell': strongest_sell,
            'strength': max(buy_strength, sell_strength),
            'bias': 'buy' if buy_strength > sell_strength else 'sell' if sell_strength > buy_strength else 'balanced'
        })
        matches.append(enriched_row)

    return sorted(
        matches,
        key=lambda row: (-row['strength'], -(row['buy_strength'] + row['sell_strength']), row['tick'])
    )


@app.route('/')
def screener():
    counts_data = [serialize_count(item) for item in Counts.query.all()]

    return render_template('screener.html', counts=counts_data)


@app.route('/api/signals')
def signal_feed():
    direction = request.args.get('direction', 'all').lower()
    family = request.args.get('family', 'all').lower()
    group = request.args.get('group', '')

    if direction not in {'all', 'buy', 'sell', 'both'}:
        return jsonify({'error': 'direction must be all, buy, sell, or both'}), 400

    if family not in SIGNAL_FAMILIES:
        return jsonify({'error': 'unknown signal family'}), 400

    try:
        minimum = max(int(request.args.get('minimum', 0)), 0)
        limit = min(max(int(request.args.get('limit', 50)), 1), 250)
    except (TypeError, ValueError):
        return jsonify({'error': 'minimum and limit must be whole numbers'}), 400

    rows = [serialize_count(item) for item in Counts.query.all()]
    matches = build_signal_feed(rows, direction, family, minimum, group)

    return jsonify({
        'count': min(len(matches), limit),
        'total': len(matches),
        'filters': {
            'direction': direction,
            'family': family,
            'minimum': minimum,
            'group': group,
            'limit': limit
        },
        'signals': matches[:limit]
    })


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


def build_holdings_concentration(holding_info, tick):
    holdings = holding_info.get(tick, {}).get('holdings', []) if holding_info else []
    weighted_holdings = []

    for holding in holdings or []:
        try:
            weight = float(holding.get('holdingPercent') or 0)
        except (TypeError, ValueError):
            continue

        if weight <= 0:
            continue

        weighted_holdings.append({
            'symbol': holding.get('symbol') or 'N/A',
            'name': holding.get('holdingName') or holding.get('symbol') or 'Unknown holding',
            'weight': weight
        })

    weighted_holdings.sort(key=lambda holding: holding['weight'], reverse=True)

    if not weighted_holdings:
        return {
            'available': False,
            'holding_count': 0,
            'classification': 'Unavailable',
            'detail': 'No weighted holdings were reported for this fund.',
            'top_holding': None,
            'runner_up': None,
            'leader_gap': 0,
            'buckets': []
        }

    def concentration(count):
        return min(sum(holding['weight'] for holding in weighted_holdings[:count]), 1)

    top_three = concentration(3)
    top_five = concentration(5)
    top_ten = concentration(10)

    if top_ten >= 0.5:
        classification = 'Concentrated'
        detail = 'The ten largest positions account for at least half of reported exposure.'
    elif top_ten >= 0.35:
        classification = 'Focused'
        detail = 'The largest positions drive a meaningful share of reported exposure.'
    else:
        classification = 'Broadly spread'
        detail = 'Reported exposure is distributed beyond the ten largest positions.'

    top_holding = weighted_holdings[0]
    runner_up = weighted_holdings[1] if len(weighted_holdings) > 1 else None
    leader_gap = top_holding['weight'] - runner_up['weight'] if runner_up else top_holding['weight']

    return {
        'available': True,
        'holding_count': len(weighted_holdings),
        'classification': classification,
        'detail': detail,
        'top_holding': top_holding,
        'runner_up': runner_up,
        'leader_gap': leader_gap,
        'buckets': [
            {'label': 'Top 3', 'weight': top_three, 'detail': 'Largest three positions'},
            {'label': 'Top 5', 'weight': top_five, 'detail': 'Largest five positions'},
            {'label': 'Top 10', 'weight': top_ten, 'detail': 'Largest ten positions'},
            {'label': 'Beyond Top 10', 'weight': max(1 - top_ten, 0), 'detail': 'Remaining portfolio exposure'}
        ]
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

    holdings_concentration = build_holdings_concentration(holding_info, tick)

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
                           etf_snapshot=etf_snapshot,
                           holdings_concentration=holdings_concentration
                           )


