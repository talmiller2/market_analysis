import pandas as pd
import numpy as np
import copy
from scipy.interpolate import interp1d
from aux_functions import change_date_format_investingcom_to_yahoo, get_number_of_days_between_dates, \
    transform_to_days_array, get_inds_between_dates, get_index_of_date
import os


def define_stock_parameters():
    expense_ratios = {}  # [percents]
    leverage_factors = {}  # [percents]
    dividend_yield = {}  # [percents] calibrated as constant in time
    underlying_index = {}  # for simulation

    expense_ratios['SP500'] = 0
    leverage_factors['SP500'] = 1.0
    underlying_index['SP500'] = 'SP500'
    div_SP500 = 2.0
    dividend_yield['SP500'] = div_SP500

    expense_ratios['SP500TR'] = 0
    leverage_factors['SP500TR'] = 1.0
    underlying_index['SP500TR'] = 'SP500TR'
    dividend_yield['SP500TR'] = 0

    expense_ratios['NDX100'] = 0
    leverage_factors['NDX100'] = 1.0
    underlying_index['NDX100'] = 'NDX100'
    div_NDX100 = 0.7
    dividend_yield['NDX100'] = div_NDX100

    expense_ratios['NDX100TR'] = 0
    leverage_factors['NDX100TR'] = 1.0
    underlying_index['NDX100TR'] = 'NDX100TR'
    dividend_yield['NDX100TR'] = 0

    # S&P500 etf
    expense_ratios['SPY'] = 0.09
    leverage_factors['SPY'] = 1.0
    underlying_index['SPY'] = 'SP500'
    dividend_yield['SPY'] = div_SP500

    expense_ratios['VFINX'] = 0.14
    leverage_factors['VFINX'] = 1.0
    underlying_index['VFINX'] = 'SP500'
    dividend_yield['VFINX'] = div_SP500

    expense_ratios['VOO'] = 0.03
    leverage_factors['VOO'] = 1.0
    underlying_index['VOO'] = 'SP500'
    dividend_yield['VOO'] = div_SP500

    expense_ratios['IVV'] = 0.03
    leverage_factors['IVV'] = 1.0
    underlying_index['IVV'] = 'SP500'
    dividend_yield['IVV'] = div_SP500

    # S&P500 X2 etf
    expense_ratios['ULPIX'] = 1.5
    leverage_factors['ULPIX'] = 2.0
    underlying_index['ULPIX'] = 'SP500TR'
    dividend_yield['ULPIX'] = 0

    expense_ratios['SPUU'] = 0.65
    leverage_factors['SPUU'] = 2.0
    underlying_index['SPUU'] = 'SP500TR'
    dividend_yield['SPUU'] = 0

    expense_ratios['SSO'] = 0.91
    leverage_factors['SSO'] = 2.0
    underlying_index['SSO'] = 'SP500TR'
    dividend_yield['SSO'] = 0

    # S&P500 X3 etf
    expense_ratios['SPXL'] = 1.01
    leverage_factors['SPXL'] = 3.0
    underlying_index['SPXL'] = 'SP500TR'
    dividend_yield['SPXL'] = 0

    expense_ratios['UPRO'] = 0.93
    leverage_factors['UPRO'] = 3.0
    underlying_index['UPRO'] = 'SP500TR'
    dividend_yield['UPRO'] = 0

    # fictitious SP500 X2.5 etf
    expense_ratios['VOO2.5'] = 1.0
    leverage_factors['VOO2.5'] = 2.5
    underlying_index['VOO2.5'] = 'SP500TR'
    dividend_yield['VOO2.5'] = 0

    # fictitious SP500 X4 etf
    expense_ratios['VOO4'] = 1.0
    leverage_factors['VOO4'] = 4.0
    underlying_index['VOO4'] = 'SP500TR'
    dividend_yield['VOO4'] = 0

    # NDX100 etf
    expense_ratios['QQQ'] = 0.2
    leverage_factors['QQQ'] = 1.0
    underlying_index['QQQ'] = 'NDX100'
    dividend_yield['QQQ'] = div_NDX100

    # NDX100 X2 etf
    expense_ratios['QLD'] = 0.95
    leverage_factors['QLD'] = 2.0
    underlying_index['QLD'] = 'NDX100TR'
    dividend_yield['QLD'] = 0

    # NDX100 X3 etf
    expense_ratios['TQQQ'] = 0.95
    leverage_factors['TQQQ'] = 3.0
    underlying_index['TQQQ'] = 'NDX100TR'
    dividend_yield['TQQQ'] = 0

    # fictitious NDX100 X2.5 etf
    expense_ratios['QQQ2.5'] = 1.0
    leverage_factors['QQQ2.5'] = 2.5
    underlying_index['QQQ2.5'] = 'NDX100TR'
    dividend_yield['QQQ2.5'] = 0

    # fictitious NDX100 X4 etf
    expense_ratios['QQQ4'] = 1.0
    leverage_factors['QQQ4'] = 4.0
    underlying_index['QQQ4'] = 'NDX100TR'
    dividend_yield['QQQ4'] = 0

    # Total bond market index etf
    expense_ratios['VBTLX'] = 0.05
    leverage_factors['VBTLX'] = 1.0
    underlying_index['VBTLX'] = 'VBTLX'
    dividend_yield['VBTLX'] = 4.0  # TODO: calibrate

    # US government treasury 10 to 30-year bond etf
    expense_ratios['VUSTX'] = 0.2
    leverage_factors['VUSTX'] = 1.0
    underlying_index['VUSTX'] = 'VUSTX'
    dividend_yield['VUSTX'] = 5

    # fictitious leveraged VUSTX variants
    expense_ratios['VUSTX2'] = 1.0
    leverage_factors['VUSTX2'] = 2.0
    underlying_index['VUSTX2'] = 'VUSTX-TR'
    dividend_yield['VUSTX2'] = 0

    expense_ratios['VUSTX2.5'] = 1.0
    leverage_factors['VUSTX2.5'] = 2.5
    underlying_index['VUSTX2.5'] = 'VUSTX-TR'
    dividend_yield['VUSTX2.5'] = 0

    expense_ratios['VUSTX3'] = 1.0
    leverage_factors['VUSTX3'] = 3.0
    underlying_index['VUSTX3'] = 'VUSTX-TR'
    dividend_yield['VUSTX3'] = 0

    expense_ratios['VUSTX4'] = 1.0
    leverage_factors['VUSTX4'] = 4.0
    underlying_index['VUSTX4'] = 'VUSTX-TR'
    dividend_yield['VUSTX4'] = 0

    # US government treasury 20-year bond etf
    expense_ratios['TLT'] = 0.15
    leverage_factors['TLT'] = 1.0
    underlying_index['TLT'] = 'TLT'
    dividend_yield['TLT'] = 4.0

    # US government treasury 20-year bond X2 etf
    expense_ratios['UBT'] = 0.95
    leverage_factors['UBT'] = 2.0
    underlying_index['UBT'] = 'TLT-TR'
    dividend_yield['UBT'] = 0

    # US government treasury 20-year bond X3 etf
    expense_ratios['TMF'] = 1.05
    leverage_factors['TMF'] = 3.0
    underlying_index['TMF'] = 'TLT-TR'
    dividend_yield['TMF'] = 0

    # actively managed etf
    expense_ratios['ARKK'] = 0.75
    leverage_factors['ARKK'] = 1.0
    underlying_index['ARKK'] = 'ARKK'
    dividend_yield['ARKK'] = 0

    return expense_ratios, leverage_factors, underlying_index, dividend_yield


def load_stock_data(stock_name, date_start=None, date_end=None, normalize=True, close_type='Close',
                    data_format='Yahoo', dividend_yield=None, settings=None):
    """
    Load stock time evolution data.
    If date for start/end is given, restrict the output by those dates.
    Most data is from Yahoo finance.
    """

    data_file_name = stock_name
    if stock_name == 'SP500':
        data_file_name = '^GSPC'
    elif stock_name == 'SP500TR':
        data_file_name = '^SP500TR'
    elif stock_name == 'NDX100':
        data_file_name = '^NDX'
    elif stock_name == 'TLT-TR':
        data_file_name = 'TLT'
        close_type = 'Adj Close'
    elif stock_name == 'VUSTX-TR':
        data_file_name = 'VUSTX'
        close_type = 'Adj Close'
    elif stock_name == 'NDX100TR':
        # date from https://www.investing.com/indices/nasdaq-100-tr-historical-data
        data_file_name = 'Nasdaq 100 TR Historical Data'
        data_format = 'Investing.com'

    main_dir = os.path.dirname(os.path.abspath(__file__))
    data = pd.read_csv(main_dir + '/data/' + data_file_name + '.csv')

    if data_format == 'Yahoo':
        dates = [x for x in data['Date']]
        values = np.array([x for x in data[close_type]])
    elif data_format == 'Investing.com':
        # special treatment for NDX100TR
        dates = [change_date_format_investingcom_to_yahoo(x) for x in data['Date']]
        values = np.array([float(x.replace(',', '')) for x in data['Price']])
        # date is "future to past" so reverse it
        dates = dates[::-1]
        values = values[::-1]
    else:
        raise ValueError('invalid data_format = ' + str(data_format))

    # artificially extend NDX100TR data prior to 1999 by stitching it with NDX100 data + estimated dividends
    if stock_name == 'NDX100TR':
        dates_NDX100, values_NDX100 = load_stock_data('NDX100', date_start=None, date_end=None,
                                                      normalize=normalize, close_type=close_type, data_format='Yahoo',
                                                      dividend_yield=dividend_yield, settings=settings)

        data_start_NDX100TR = dates[0]
        data_end_NDX100TR = dates[-1]
        ind_cnt_NDX100TR = 1
        values_merged = [1.0]
        for i in range(1, len(dates_NDX100) - 1):
            curr_date = dates_NDX100[i]
            if get_number_of_days_between_dates(curr_date, data_start_NDX100TR) <= 0:
                # use the NDX100 + dividends prior to 1999
                values_merged += [values_merged[-1] * values_NDX100[i] / values_NDX100[i - 1]]
                values_merged[-1] *= 1 + dividend_yield['NDX100'] / 100.0 / settings['num_trading_days_in_year']
            elif get_number_of_days_between_dates(curr_date, data_end_NDX100TR) <= 0:
                # use the NDX100TR data after 1999
                values_merged += [values_merged[-1] * values[ind_cnt_NDX100TR] / values[ind_cnt_NDX100TR - 1]]
                ind_cnt_NDX100TR += 1
            else:
                break

        values = values_merged
        dates = dates_NDX100

    # check if requested time interval is contained within the data
    if date_start is not None:
        if get_number_of_days_between_dates(dates[0], date_start) > 0:
            raise ValueError('data for stock ' + str(stock_name) + ' begins at ' + dates[0]
                             + ', but requested date_start is ' + str(date_start))
    if date_end is not None:
        if get_number_of_days_between_dates(dates[-1], date_end) < 0:
            raise ValueError('data for stock ' + str(stock_name) + ' ends at ' + dates[-1]
                             + ', but requested date_end is ' + str(date_end))

    # pick only a specific time interval
    inds_restricted = get_inds_between_dates(dates, date_start, date_end)
    dates = [dates[i] for i in inds_restricted]
    values = [values[i] for i in inds_restricted]

    # normalize to initial date
    if normalize:
        values /= values[0]

    return dates, values


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


def load_libor_rates():
    # data from https://www.macrotrends.net/1433/historical-libor-rates-chart
    main_dir = os.path.dirname(os.path.abspath(__file__))
    loan_rates_data = pd.read_csv(main_dir + '/data/historical-libor-rates-chart.csv')
    dates = [x for x in loan_rates_data['date']]
    libor_rate = [x for x in loan_rates_data['libor-1-month']]
    return dates, libor_rate


def get_libor_rate(dates_to_interpolate):
    dates_data, libor_rate_data = load_libor_rates()
    days_to_interpolate = transform_to_days_array(dates_to_interpolate)
    days_data_array = transform_to_days_array(dates_data, date_reference=dates_to_interpolate[0])

    # check if requested time interval is contained within the data
    date_start = dates_to_interpolate[0]
    if get_number_of_days_between_dates(dates_data[0], date_start) > 0:
        raise ValueError('data for libor rates begins at ' + dates_data[0]
                         + ', but requested date_start is ' + str(date_start))

    date_end = dates_to_interpolate[-1]
    if get_number_of_days_between_dates(dates_data[-1], date_end) < 0:
        raise ValueError('data for  libor rate ends at ' + dates_data[-1]
                         + ', but requested date_end is ' + str(date_end))

    # interpolate
    interp_fun = interp1d(days_data_array, libor_rate_data)
    libor_rate_interpolated = interp_fun(days_to_interpolate)
    return libor_rate_interpolated
