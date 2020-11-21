"""Functions for fetching/manipulating finance data."""

import numpy as np
from datetime import date, timedelta
import pandas_datareader as pdr
from pandas_datareader._utils import RemoteDataError

from . import currency


def fetch_close(position):
    """Return series of historical daily closing share price."""
    if position.series_x:
        date_from = position.series_x[-1] + timedelta(days=1)
    else:
        date_from = position.buy_date

    if date_from >= date.today():
        return

    dfs = pdr.get_data_yahoo(
        position.stock_code,
        start=date_from,
        end=date.today()
    )

    # Remove duplicate dates from api data
    dfs.index = [ix.to_pydatetime().date() for ix in dfs.index]
    dfs = dfs.loc[~dfs.index.duplicated(keep='first')]

    # Remove dates that already exist in DB
    if position.series_x:
        unique_dates = np.intersect1d(dfs.index, position.series_x)
        dfs.drop(
            dfs.loc[unique_dates].index,
            inplace=True
        )
    if len(dfs):
        return dfs['Close']


def format_for_render(positions):
    """Render positions' data into open/closed/totals for display."""
    def get_unique_stock_code(base, stock_data):
        """Make stock code unique by appending with number."""
        i = 2
        stock_code = base
        while stock_code in stock_data:
            stock_code = base + f"_{i}"
            i += 1
        return stock_code

    def usd_fmt(value):
        """Comma-separate values over $10 and return string formatted."""
        if value < 10000:
            return '$%.2f' % value
        x = '%.2f' % value
        x, y = x.split('.')
        return '$%s,%s.%s' % (x[:-3], x[-3:], y)

    open_pl_usd = 0
    closed_pl_usd = 0
    open_init_usd = 0
    closed_init_usd = 0
    data = {'open': {}, 'closed': {}}

    for p in positions.filter(close_price__isnull=True).order_by('buy_date'):
        pl = (p.current - p.buy_price) / p.buy_price
        pl_pc = 100 * pl
        opening_usd = currency.exchange[p.currency](p.buy_qty * p.buy_price)
        open_init_usd += opening_usd
        pl_usd = opening_usd * pl
        open_pl_usd += pl_usd
        stock_code = get_unique_stock_code(p.stock_code, data['open'])
        data['open'][stock_code] = [
            '%.2f' % p.buy_price,
            '%s' % p.buy_qty,
            '%.2f' % p.current,
            usd_fmt(p.holding),
            usd_fmt(pl_usd),
            '%.2f %%' % pl_pc,
            'plus' if pl_pc > 0 else 'minus',
            p.id,
        ]

    for p in positions.exclude(
            close_price__isnull=True).order_by('date_closed'):
        pl = (p.close_price - p.buy_price) / p.buy_price
        pl_pc = 100 * pl
        opening_usd = currency.exchange[p.currency](p.buy_qty * p.buy_price)
        closed_init_usd += opening_usd
        pl_usd = opening_usd * pl
        closed_pl_usd += pl_usd
        stock_code = get_unique_stock_code(p.stock_code, data['closed'])
        data['closed'][stock_code] = [
            p.date_closed.strftime('%d-%m-%Y'),
            '%.2f' % p.buy_price,
            '%.2f' % p.close_price,
            '%s' % p.buy_qty,
            usd_fmt(opening_usd),
            usd_fmt(pl_usd),
            '%.2f %%' % pl_pc,
            'plus' if pl_pc > 0 else 'minus',
            p.id,
        ]

    total_open_usd = sum(
        positions.filter(close_price=None)
        .values_list("holding", flat=True)
    )
    total_closed_usd = sum(
        positions.exclude(close_price=None)
        .values_list("holding", flat=True)
    )
    if open_init_usd:
        data['open_total'] = [
            usd_fmt(open_init_usd),
            usd_fmt(total_open_usd),
            usd_fmt(open_pl_usd),
            '%.2f %%' % (100 * open_pl_usd / open_init_usd),
        ]
    if closed_init_usd:
        data['closed_total'] = [
            usd_fmt(closed_init_usd),
            usd_fmt(closed_pl_usd),
            '%.2f %%' % (100 * closed_pl_usd / closed_init_usd),
        ]
    if (open_init_usd + closed_init_usd):
        data['grand_total'] = [
            usd_fmt(open_init_usd + closed_init_usd),
            usd_fmt(total_open_usd + total_closed_usd),
            usd_fmt(open_pl_usd + closed_pl_usd),
            '%.2f %%' % (
                100 *
                (open_pl_usd + closed_pl_usd)
                / (open_init_usd + closed_init_usd)
            ),
            'plus' if (open_pl_usd + closed_pl_usd) > 0 else 'minus',
        ]

    return data


def confirm_stock_code(stock_code):
    """Assert that API knows this ticker."""
    try:
        pdr.get_data_yahoo(
            stock_code,
            start=(date.today() - timedelta(days=7)),
            end=date.today(),
        )
    except RemoteDataError:
        return False
    return True