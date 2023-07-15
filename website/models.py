from website import db


class Counts(db.Model):
    name_of_company = db.Column(db.String(100), index=True, unique=False)
    ticker = db.Column(db.String(10), index=True, unique=True, primary_key=True)
    etf = db.Column(db.String(20), index=True, unique=False)
    seq_buy_count_daily = db.Column(db.Integer, index=True, unique=False)
    seq_sell_count_daily = db.Column(db.Integer, index=True, unique=False)
    seq_buy_count_weekly = db.Column(db.Integer, index=True, unique=False)
    seq_sell_count_weekly = db.Column(db.Integer, index=True, unique=False)
    seq_buy_9_13_9 = db.Column(db.Boolean, default=False)
    seq_sell_9_13_9 = db.Column(db.Boolean, default=False)
    combo_buy_count_daily = db.Column(db.Integer, index=True, unique=False)
    combo_sell_count_daily = db.Column(db.Integer, index=True, unique=False)
    combo_buy_count_weekly = db.Column(db.Integer, index=True, unique=False)
    combo_sell_count_weekly = db.Column(db.Integer, index=True, unique=False)
    combo_buy_9_13_9 = db.Column(db.Boolean, default=False)
    combo_sell_9_13_9 = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'Counts for {Counts.ticker}'




