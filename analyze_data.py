import pandas as pd
import os
import math
# import numpy


# global variables
years = [year for year in range(1987, 2009)]
# years = [year for year in range(1987, 1990)]
months = {1: 'January',
          2: 'February',
          3: 'March',
          4: 'April',
          5: 'May',
          6: 'June',
          7: 'July',
          8: 'August',
          9: 'September',
          10: 'October',
          11: 'November',
          12: 'December'
          }

days_of_week = {1: 'Monday',
                2: 'Tuesday',
                3: 'Wednesday',
                4: 'Thursday',
                5: 'Friday',
                6: 'Saturday',
                7: 'Sunday'
                }

times_of_day = dict()
for time in range(0, 2400):
    if 500 <= time < 1200:
        times_of_day[time] = 'morning'
    elif 1200 <= time < 1700:
        times_of_day[time] = 'afternoon'
    elif 1700 <= time < 2100:
        times_of_day[time] = 'evening'
    else:
        times_of_day[time] = 'night'

pickles_years_directories = [os.path.join('pickles', 'pickle_' + str(year) + '.pkl') for year in years]

years_data_types = {'Year': int,
                    'Month': int,
                    'DayofMonth': int,
                    'DayOfWeek': int,
                    'DepTime': int,
                    'CRSDepTime': int,
                    'ArrTime': int,
                    'CRSArrTime': int,
                    'UniqueCarrier': str,
                    'FlightNum': int,
                    'TailNum': str,
                    'ActualElapsedTime': float,
                    'CRSElapsedTime': float,
                    'AirTime': float,
                    'ArrDelay': float,
                    'DepDelay': float,
                    'Origin': str,
                    'Dest': str,
                    'Distance': float,  # int,
                    'TaxiIn': float,  # int,
                    'TaxiOut': float,  # int,
                    'Cancelled': float,  # int,
                    'CancellationCode': str,
                    'Diverted': float,  # int,
                    'CarrierDelay': float,
                    'WeatherDelay': float,
                    'NASDelay': float,
                    'SecurityDelay': float,
                    'LateAircraftDelay': float
                    }


def sum_of_lists(list1, list2):
    return_list = list()
    for a, b in zip(list1, list2):
        return_list.append(a + b)
    return return_list


def run_only_once_convert_csv_to_pickles():
    print('starting conversion of CSV yearly files to pickles')
    csv_files_directories = [os.path.join('dataverse_files', 'data_years', str(year) + '.csv') for year in years]
    count = 0
    many = len(years)
    for csv_file, pickle in zip(csv_files_directories, pickles_years_directories):
        count += 1
        print('converting {} out of {}'.format(count, many))
        pd.read_csv(csv_file, encoding="ISO-8859-1", dtype=years_data_types).to_pickle(pickle)
    print('conversion of yearly data complete')
    print()

    print('starting conversion of other CSV files to pickles')
    folder = os.path.join('dataverse_files', 'data_other')
    for file in os.listdir(folder):
        filename, extension = os.path.splitext(file)
        if extension == '.csv':
            print('converting {} into pickle'.format(file))
            pd.read_csv(os.path.join(folder, file), encoding='ISO-8859-1').to_pickle(
                os.path.join('pickles', 'pickle_' + filename + '.pkl'))
    print('conversion complete')


def get_data_frame_from_pickle(pickle_name, print_info=False):
    if print_info:
        print('Getting data from pickle {}.'.format(pickle_name))
    return pd.read_pickle(pickle_name)


def get_frequencies(data_frame, column_name, thresholds=None):
    frequencies_list = list()
    number_of_intervals = len(thresholds) - 1
    for idx in range(number_of_intervals):
        interval_start = thresholds[idx]
        interval_end = thresholds[idx + 1]
        number_of_items = len(data_frame[(data_frame[column_name] > interval_start) &
                                         (data_frame[column_name] <= interval_end)])
        frequencies_list.append(number_of_items)
    return frequencies_list


def get_dataframe_with_frequencies_for_single_year(data_frame, column_name_for_frequencies,
                                                   column_name_for_periods, periods_dict,
                                                   step, thresholds=None):
    # creating thresholds if they are not passed to the function
    if thresholds is None:
        unique_column_values = list(data_frame[column_name_for_frequencies].unique())
        unique_column_values.sort()
        min_value = math.floor(min(unique_column_values) / step) * step
        max_value = math.ceil(max(unique_column_values) / step) * step
        thresholds = [threshold for threshold in range(min_value, max_value + step, step)]
        position_zero = thresholds.index(0)
        thresholds = thresholds[:position_zero] + [-15, 15] + thresholds[position_zero + 1:]

    # create lists for 'from' and 'to' columns of our spreadsheet
    list_from = thresholds[:-1]
    list_to = thresholds[1:]

    # create list of column values
    # firstly, 2 columns showing intervals
    columns = [list_from, list_to]

    # secondly, create a dict where keys are values from period dict
    # (i.e. for example names of days, of months or of times of day) and values are lists of frequencies
    columns_dict = dict()
    columns_dict_keys = set(periods_dict.values())
    # initial frequencies are 0
    for key in columns_dict_keys:
        columns_dict[key] = [0 for _ in range(len(thresholds) - 1)]
    for single_period in periods_dict:
        data_frame_by_single_period = data_frame[data_frame[column_name_for_periods] == single_period]
        new_frequencies_for_single_period = get_frequencies(data_frame=data_frame_by_single_period,
                                                            column_name=column_name_for_frequencies,
                                                            thresholds=thresholds)
        columns_dict[periods_dict[single_period]] = sum_of_lists(columns_dict[periods_dict[single_period]],
                                                                 new_frequencies_for_single_period)
    # thirdly, transform the dict into a list
    while True:
        if len(columns_dict_keys) == 0:
            break
        for single_period in periods_dict:
            period_name = periods_dict[single_period]
            if period_name in columns_dict_keys:
                columns_dict_keys.remove(period_name)
                columns.append(columns_dict[period_name])

    # convert column data to row data
    rows = [list() for _ in range(len(thresholds) - 1)]
    for column in columns:
        for elt, row in zip(column, rows):
            row.append(elt)

    # create list of column names
    column_names = ['from', 'to']
    for single_period in periods_dict.keys():
        column_name = periods_dict[single_period]
        if column_name not in column_names:
            column_names.append(periods_dict[single_period])

    # create pandas data frame from our frequencies
    frequencies_data_frame = pd.DataFrame(rows, columns=column_names)
    return frequencies_data_frame


def convert_df_to_percentages_by_columns(df):
    for column in df.columns:
        if column not in {'from', 'to'}:
            total = sum(df[column])
            df[column] = df[column] / total * 100
    return df


def get_excel_with_frequencies_for_all_years(my_filter, column_name_for_periods, thresholds, periods_dict, excel_name,
                                             in_percentages=True):
    print('>>> ' + excel_name.replace('_', ' '))
    dataframes_dict = dict()
    summary_dataframe = pd.DataFrame()
    for idx, year in enumerate(years):
        print('Analyzing data from year {}. Year {} out of {}.'.format(year, idx + 1, len(years)))

        # get data from pickle
        data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))

        # filter out cancelled flights
        data_frame = data_frame[data_frame['Cancelled'] == 0]

        # filter only the columns that we may need
        data_frame = data_frame.filter(my_filter)

        # get frequencies per day in a dataframe
        dataframes_dict[year] = get_dataframe_with_frequencies_for_single_year(
            data_frame=data_frame, column_name_for_frequencies='ArrDelay',
            column_name_for_periods=column_name_for_periods, step=100, periods_dict=periods_dict,
            thresholds=thresholds)

        # add frequencies to the summary dict
        summary_dataframe = summary_dataframe.add(dataframes_dict[year], fill_value=0)

    # change raw values to percentages
    if in_percentages:
        for year in years:
            convert_df_to_percentages_by_columns(dataframes_dict[year])
        convert_df_to_percentages_by_columns(summary_dataframe)

    # create excel files
    print(f'Saving all data into  "{excel_name}.xlsx."')
    with pd.ExcelWriter('excel_files/{}.xlsx'.format(excel_name)) as writer:
        for year in years:
            dataframes_dict[year].to_excel(writer, sheet_name=str(year))
        print(f'Saving summary data into  "{excel_name}.xlsx."')
        summary_dataframe.to_excel(writer, sheet_name='summary')


def main():
    # run_only_once_convert_csv_to_pickles()
    # filter_0 = [
    #     "Year",
    #     "Month",
    #     "DayofMonth",
    #     "DayOfWeek",
    #     "DepTime",
    #     "CRSDepTime",
    #     "ArrTime",
    #     "CRSArrTime",
    #     "UniqueCarrier",
    #     "FlightNum",
    #     "TailNum",
    #     "ActualElapsedTime",
    #     "CRSElapsedTime",
    #     "AirTime",
    #     "ArrDelay",
    #     "DepDelay",
    #     "Origin",
    #     "Dest",
    #     "Distance",
    #     "TaxiIn",
    #     "TaxiOut",
    #     "Cancelled",
    #     "CancellationCode",
    #     "Diverted",
    #     "CarrierDelay",
    #     "WeatherDelay",
    #     "NASDelay",
    #     "SecurityDelay",
    #     "LateAircraftDelay"
    # ]
    # Question 1. When is the best time to fly to minimise delays?
    # 1.1 time of day
    filter_1_1 = [
        "DepTime",
        "ArrDelay"
    ]
    get_excel_with_frequencies_for_all_years(my_filter=filter_1_1,
                                             column_name_for_periods='DepTime',
                                             thresholds=[-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1500],
                                             periods_dict=times_of_day,
                                             excel_name='frequencies_for_time_of_day')
    # 1.2 day of week
    filter_1_2 = [
        "DayOfWeek",
        "ArrDelay"
    ]
    get_excel_with_frequencies_for_all_years(my_filter=filter_1_2,
                                             column_name_for_periods='DayOfWeek',
                                             thresholds=[-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1500],
                                             periods_dict=days_of_week,
                                             excel_name='frequencies_for_days_of_week')
    # 1.3 time of year
    filter_1_3 = [
        "Month",
        "ArrDelay"
    ]
    get_excel_with_frequencies_for_all_years(my_filter=filter_1_3,
                                             column_name_for_periods='Month',
                                             thresholds=[-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1500],
                                             periods_dict=months,
                                             excel_name='frequencies_for_months')

# for later use:
# print(data_frame['Cancelled'].value_counts())
# print(data_frame['DayOfWeek'].unique())
# print(data_frame_grouped_by_days.describe())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#     print(data_frame_grouped_by_days.describe())
# print(data_frame_grouped_by_days.mean())
# data_frame_grouped_by_days = data_frame.groupby('DayOfWeek', as_index=False)['ArrDelay']
# print(data_frame[data_frame['ArrDelay'] < -180])
#


if __name__ == '__main__':
    main()

# def convert_csv_data_into_pickle(pickle_name='all_data.pkl'):
#     print('starting conversion')
#     csv_files_list = ['dataverse_files/data_years/' + str(year) + '.csv' for year in years]
#     # merging csv files
#     df = pd.concat(map(lambda file: pd.read_csv(file, encoding="ISO-8859-1"), csv_files_list), ignore_index=True)
#     df.to_pickle(pickle_name)
#     print('conversion complete')
    # alternative way of getting data from pickle:
    # store = pd.HDFStore('store.h5')
    # store['df'] = df  # save it
    # store['df']  # load it
