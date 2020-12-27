import pandas as pd
import numpy as np
import copy
from scipy.interpolate import interp1d


def load_stock_data(stock_name, date_start=None, date_end=None):
    """
    Load stock time evolution data.
    If date for start/end is given, restrict the output by those dates.
    """
    data_file_name = stock_name
    if stock_name == 'NDX100':
        data_file_name = '^NDX'
    elif stock_name == 'SP500':
        data_file_name = '^GSPC'
    data = pd.read_csv('data/' + data_file_name + '.csv')
    dates = [x for x in data['Date']]
    values = [x for x in data['Close']]

    inds_restricted = get_inds_between_dates(dates, date_start, date_end)
    dates = [dates[i] for i in inds_restricted]
    values = [values[i] for i in inds_restricted]

    return dates, values


def get_date(date_string):
    """
    parse date from string in the "Yahoo finance" format YYYY-MM-DD
    """
    date_list = date_string.split('-')
    year = int(date_list[0])
    month = int(date_list[1])
    day = int(date_list[2])
    return day, month, year


def is_date_between_dates(date, date_start=None, date_end=None):
    day, month, year = get_date(date)

    after_start_date = True
    if date_start is not None:
        day_start, month_start, year_start = get_date(date_start)
        if (year > year_start) or (year == year_start and month > month_start) \
                or (year == year_start and month == month_start and day >= day_start):
            after_start_date = True
        else:
            after_start_date = False

    before_end_date = True
    if date_end is not None:
        day_end, month_end, year_end = get_date(date_end)
        if (year < year_end) or (year == year_end and month < month_end) \
                or (year == year_end and month == month_end and day <= day_end):
            before_end_date = True
        else:
            before_end_date = False

    date_is_between_dates = after_start_date and before_end_date
    return date_is_between_dates


def get_inds_between_dates(dates, date_start=None, date_end=None):
    inds_restricted = []
    for i, date in enumerate(dates):
        if is_date_between_dates(date, date_start, date_end):
            inds_restricted += [i]
    return inds_restricted


def get_number_of_days_between_dates(date1, date2, keep_sign=False):
    """
    Count the number of days between two dates, assuming 365 days in a year with equally sized months
    """
    day1, month1, year1 = get_date(date1)
    day2, month2, year2 = get_date(date2)
    num_days1 = year1 * 365.0 + month1 * 365.0 / 12 + day1
    num_days2 = year2 * 365.0 + month2 * 365.0 / 12 + day2
    dist = num_days1 - num_days2
    if keep_sign == False:
        dist = abs(dist)
    return dist


def transform_to_days_array(dates, date_reference=None):
    """
    Instead of dealing with strings of dates, count the days passed relative to a reference date
    """
    if date_reference is None:
        date_reference = dates[0]
    days_array = []
    for date in dates:
        days_array += [get_number_of_days_between_dates(date_reference, date, keep_sign=True)]
    return days_array


def interpolate_between_dates(dates, values, date_to_interpolate):
    """
    Based on samples of dates and values, interpolate to a specific date
    """
    date_before = None
    for i, date in enumerate(dates):
        if is_date_between_dates(date, date_start=date_to_interpolate, date_end=None):
            date_before = date
            value_before = values[i]
            if i == len(dates):
                raise ValueError('requested date ' + date_to_interpolate + ' is not in the date range')
            date_after = dates[i - 1]
            value_after = values[i - 1]
            break

    days_to_interp = get_number_of_days_between_dates(date_to_interpolate, date_before)
    days_range = get_number_of_days_between_dates(date_after, date_before)
    value_interp = value_before + days_to_interp / days_range * (value_after - value_before)
    return value_interp


def get_year_labels(dates):
    """
    find indices where years start, for plot's x-asis
    """
    day_start, month_start, year_start = get_date(dates[0])
    day_end, month_end, year_end = get_date(dates[-1])
    label_years = [i for i in range(year_start + 1, year_end + 1)]
    inds_years = []
    year_cnt = year_start
    for i, date in enumerate(dates):
        curr_year = int(date.split('-')[0])
        if curr_year > year_cnt:
            inds_years += [i]
            year_cnt += 1
    return inds_years, label_years


def load_dividend_data(index_name='SP500'):
    if index_name == 'NDX100':
        # data from https://cdn.betashares.com.au/wp-content/uploads/2016/12/05160625/BetaShares-NASDAQ-100-ETF-NDQ-Whitepaper.pdf
        data_file_name = 'historic_div_yield_NDX100'
    elif index_name == 'SP500':
        # data from https://www.quandl.com/data/MULTPL/SP500_DIV_YIELD_MONTH-S-P-500-Dividend-Yield-by-Month
        data_file_name = 'historic_div_yield_SP500'
    else:
        raise ValueError('invalid index_name.')
    data = pd.read_csv('data/' + data_file_name + '.csv')
    dates = [x for x in data['Date']]
    dividends = [x for x in data['Value']]
    if index_name == 'SP500':
        # reverse the direction because div yields of SP500 are given from future to past
        dates.reverse()
        dividends.reverse()
    return dates, dividends


def get_dividend_yield(dates_to_interpolate, index_name='SP500'):
    dates_data, dividends_data = load_dividend_data(index_name=index_name)
    days_to_interpolate = transform_to_days_array(dates_to_interpolate)
    days_data_array = transform_to_days_array(dates_data, date_reference=dates_to_interpolate[0])
    interp_fun = interp1d(days_data_array, dividends_data)
    dividends_interpolated = interp_fun(days_to_interpolate)
    return dividends_interpolated

# def load_loan_rates(data):
#     # data from https://www.macrotrends.net/1433/historical-libor-rates-chart
#     loan_rates_data = pd.read_csv('data/historical-libor-rates-chart.csv')
#     dates = loan_rates_data['date']
#     loan_rate = loan_rates_data['libor-1-month']
#     data['loan_rates_dates'] = dates
#     data['loan_rates_values'] = loan_rate
#     return data

# def get_loan_rate(date):
#     dates = data['loan_rates_dates']
#     loan_rate = data['loan_rates_values']
#
#     # find where the requested day lies in the load rate data
#     ind_below =
#
#     # interpolate the loan rate for the current date
#     interp_fun = interp1d()
#
#     return loan_rate
