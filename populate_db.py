from website.models import Counts
from website import db, app
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import sys
import Indicators

with app.app_context():
    db.drop_all()
    db.create_all()


# end date/current date
end_day = datetime.now().strftime('%Y-%m-%d')
start_date_daily = (datetime.now() - timedelta(days=4*30)).strftime('%Y-%m-%d')
start_date_weekly = (datetime.now() - timedelta(days=12*30)).strftime('%Y-%m-%d')


# pass a list of tickers
def pop_db(tickers, fund):

    print(f"Started adding {fund} Counts to Database")

    with app.app_context():
        for index, row in tickers.iterrows():

            name = row['Name']
            t = row['Ticker']

            price_data_daily = yf.download(t, start=start_date_daily, end=end_day)
            price_data_weekly = yf.download(t, start=start_date_weekly, end=end_day, interval='1wk')

            try:

                buy_count_d, sell_count_d, has_9_13_b, has_9_13_s = Indicators.sequential(price_data_daily)
                buy_count_w, sell_count_w, has_9_13_b_w, has_9_13_s_w = Indicators.sequential(price_data_weekly)

                combo_buy_count_d, combo_sell_count_d, combo_has_9_13_b, combo_has_9_13_s = Indicators.combo_strict(price_data_daily)
                combo_buy_count_d_w, combo_sell_count_d_w, combo_has_9_13_b_w, combo_has_9_13_s_w = Indicators.combo_strict(price_data_weekly)

            except ValueError:
                print("Encountered an Error")
                continue

            count = Counts(
                ticker=t,
                etf=fund,
                name_of_company=name,
                seq_buy_count_daily=buy_count_d,
                seq_buy_count_weekly=buy_count_w,
                seq_sell_count_daily=sell_count_d,
                seq_sell_count_weekly=sell_count_w,
                seq_buy_9_13_9=has_9_13_b,
                seq_sell_9_13_9=has_9_13_s,
                combo_buy_count_daily=combo_buy_count_d,
                combo_sell_count_daily=combo_sell_count_d,
                combo_buy_count_weekly=combo_buy_count_d_w,
                combo_sell_count_weekly=combo_sell_count_d_w,
                combo_buy_9_13_9=combo_has_9_13_b,
                combo_sell_9_13_9=combo_has_9_13_s

            )
            db.session.merge(count)

        print(f'{fund} holdings counts added to database')
        db.session.commit()


hong_kong = pd.read_csv('tickers/hong_kong.csv')
ashr = pd.read_csv('tickers/ashr.csv')
austria = pd.read_csv('tickers/austria.csv')
belgium = pd.read_csv('tickers/belgium.csv')
boat = pd.read_csv('tickers/BOAT.csv')
chile = pd.read_csv('tickers/chile.csv')
denmark = pd.read_csv('tickers/denmark.csv')

pop_db(ashr, 'Mainland China')
pop_db(austria, 'Austria')
pop_db(belgium, 'Belgium')
pop_db(boat, 'Marine Shipping')
pop_db(chile, 'Chile')
pop_db(denmark, 'Denmark')
pop_db(hong_kong, 'China')

epol = pd.read_csv('tickers/epol.csv')
etfs = pd.read_csv('tickers/etfs_details_type_fund_flow.csv')
ewa = pd.read_csv('tickers/ewa.csv')
ewg = pd.read_csv('tickers/ewg.csv')
ewj = pd.read_csv('tickers/ewj.csv')
ews = pd.read_csv('tickers/ews.csv')
ewu = pd.read_csv('tickers/EWU_holdings.csv')
ewz = pd.read_csv('tickers/EWZ_holdings.csv')
fan = pd.read_csv('tickers/FAN.csv')
fdig = pd.read_csv('tickers/FDIG.csv')
finland = pd.read_csv('tickers/finland.csv')
france = pd.read_csv('tickers/france.csv')
gdx = pd.read_csv('tickers/GDX.csv')
gdxj = pd.read_csv('tickers/GDXJ.csv')
greece = pd.read_csv('tickers/greece.csv')

pop_db(epol, 'Poland')
pop_db(etfs, 'ETF')
pop_db(ewa, 'Australia')
pop_db(ewg, 'Germany')
pop_db(ewj, 'Japan')
pop_db(ews, 'Singapore')
pop_db(ewu, 'UK')
pop_db(ewz, 'Brazil')
pop_db(fan, 'Wind Power')
pop_db(fdig, 'Crypto')
pop_db(finland, 'Finland')
pop_db(france, 'France')
pop_db(gdx, 'Gold Miners')
pop_db(gdxj, 'Gold Miners')
pop_db(greece, 'Greece')

indonesia = pd.read_csv('tickers/indonesia.csv')
ireland = pd.read_csv('tickers/ireland.csv')
isreal = pd.read_csv('tickers/isreal.csv')
italy = pd.read_csv('tickers/italy.csv')
iwm = pd.read_csv('tickers/IWM_holdings.csv')
iyt = pd.read_csv('tickers/IYT-holdings.csv')
jets = pd.read_csv('tickers/JETS.csv')
ksa = pd.read_csv('tickers/ksa.csv')
lit = pd.read_csv('tickers/lit.csv')
malaysia = pd.read_csv('tickers/malaysia.csv')
mexico = pd.read_csv('tickers/mexico.csv')
mid_cap = pd.read_csv('tickers/mid_cap.csv')
netherlands = pd.read_csv('tickers/netherlands.csv')
portugal = pd.read_csv('tickers/portugal.csv')
qatar = pd.read_csv('tickers/qatar.csv')

pop_db(indonesia, 'Indonesia')
pop_db(ireland, 'Ireland')
pop_db(isreal, 'Israel')
pop_db(iwm, 'Small Caps')
pop_db(iyt, 'Transports')
pop_db(jets, 'Airlines')
pop_db(ksa, 'Saudi Arabia')
pop_db(lit, 'Lithium')
pop_db(malaysia, 'Malaysia')
pop_db(mexico, 'Mexico')
pop_db(mid_cap, 'Mid Caps')
pop_db(netherlands, 'Netherlands')
pop_db(portugal, 'Portugal')
pop_db(qatar, 'Qatar')

rus_growth = pd.read_csv('tickers/russell_growth.csv')
rus_mid = pd.read_csv('tickers/russell_mid_cap.csv')
sdy = pd.read_csv('tickers/SDY.csv')
semis = pd.read_csv('tickers/semis.csv')
sil = pd.read_csv('tickers/sil.csv')
south_africa = pd.read_csv('tickers/south_africa.csv')
south_korea = pd.read_csv('tickers/south_korea.csv')
spy = pd.read_csv('tickers/spy.csv')
sweeden = pd.read_csv('tickers/sweeden.csv')
tan = pd.read_csv('tickers/tan.csv')
tawian = pd.read_csv('tickers/tawian.csv')
thailand = pd.read_csv('tickers/thailand.csv')
tiny = pd.read_csv('tickers/TINY-holdings.csv')
turkey = pd.read_csv('tickers/turkey.csv')
uae = pd.read_csv('tickers/uae.csv')
urnm = pd.read_csv('tickers/urnm.csv')
vtv = pd.read_csv('tickers/VTV-holdings.csv')
water = pd.read_csv('tickers/water.csv')
wgmi = pd.read_csv('tickers/WGMI.csv')
wood = pd.read_csv('tickers/WOOD.csv')


pop_db(rus_growth, 'Small Cap Growth')
pop_db(rus_mid, 'Mid Caps')
pop_db(sdy, 'High Dividend')
pop_db(semis, 'Semiconductors')
pop_db(sil, 'Silver Miners')
pop_db(south_africa, 'South Africa')
pop_db(south_korea, 'South Korea')
#pop_db(spy, 'United States')
pop_db(sweeden, 'Sweeden')
pop_db(tan, 'Solar')
pop_db(tawian, 'Tawian')
pop_db(thailand, 'Thailand')
pop_db(tiny, 'Micro Chips')
pop_db(turkey, 'Turkey')
pop_db(uae, 'UAE')
pop_db(urnm, 'Uranium')
pop_db(vtv, 'Value')
pop_db(water, 'Water')
pop_db(wgmi, 'Bitcoin Miners')
pop_db(wood, 'Lumber')


xlc = pd.read_csv('tickers/xlc.csv')
xme = pd.read_csv('tickers/xme.csv')
xlb = pd.read_csv('tickers/xlb.csv')
xop = pd.read_csv('tickers/xop_csv.csv')
xlf = pd.read_csv('tickers/xlf.csv')
xli = pd.read_csv('tickers/xli.csv')
xlk = pd.read_csv('tickers/xlk.csv')
xlp = pd.read_csv('tickers/xlp.csv')
xlre = pd.read_csv('tickers/xlre.csv')
xlu = pd.read_csv('tickers/xlu.csv')
xlv = pd.read_csv('tickers/xlv.csv')
xly = pd.read_csv('tickers/xly.csv')
remx = pd.read_csv('tickers/remx.csv')
amlp = pd.read_csv('tickers/amlp.csv')

pop_db(amlp, 'Oil Services')
pop_db(remx, 'Minerals')
pop_db(xlf, 'Financials')
pop_db(xli, 'Industrials')
pop_db(xlk, 'Tech')
pop_db(xlp, 'Staples')
pop_db(xlre, 'Real Estate')
pop_db(xlu, 'Utilities')
pop_db(xlv, 'Health Care')
pop_db(xly, 'Consumer Discretionary')
pop_db(xlc, 'Communications')
pop_db(xme, 'Metals')
pop_db(xlb, 'Materials')
pop_db(xop, 'Oil')
