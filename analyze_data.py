import pandas as pd
import os
import csv
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
import numpy as np

# global variables
years = [year for year in range(1987, 2009)]
# years = [year for year in range(2003, 2006)]
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


def exponent(x):
    if x == 0:
        return 0
    return math.floor(math.log10(abs(x)))


def round_to_sf(x, sig):
    return round(x, sig-int(math.floor(math.log10(abs(x))))-1)


def show(data_frame, rows):
    print(data_frame.head(rows))
    print(data_frame.tail(rows))
    print('There are {} of records in the data frame.'.format(len(data_frame)))


def get_rounded_endpoints_and_unit(min_value, max_value):
    """
    Returns:
        min, max, step for a graph
    """
    # max_exp = max(exponent(min_value), exponent(max_value))
    min_ret = max_ret = 0
    initial_range = max_value - min_value
    max_exp = exponent(initial_range)
    if min_value:
        min_ret = round(min_value / 10 ** max_exp - 0.5) * 10 ** max_exp
    if max_value:
        max_ret = round(max_value / 10 ** max_exp + 0.5) * 10 ** max_exp
    step = 10 ** max_exp
    the_range = max_ret - min_ret
    many = the_range // step
    if many > 10:
        many = math.ceil(many / 10)
        step = step * many
    return min_ret, max_ret, step


def create_scatter_graph_with_regression(data_frame,
                                         df_x_column,
                                         df_y_column,
                                         file_name,
                                         x_label,
                                         y_label,
                                         title,
                                         x_min=None,
                                         x_max=None,
                                         x_step=None,
                                         y_min=None,
                                         y_max=None,
                                         y_step=None):
    # points
    # x_coordinates = [map(float, x_coordinates)]
    x_coordinates = data_frame[df_x_column].astype(str).astype(float)  # .to_numpy()
    y_coordinates = data_frame[df_y_column].astype(str).astype(float)  # .to_numpy()

    # boundaries
    if x_min is None or x_max is None or x_step is None:
        low, high, step = get_rounded_endpoints_and_unit(min(x_coordinates), max(x_coordinates))
        x_min = x_min or low
        x_max = x_max or high
        x_step = x_step or step
    if y_min is None or y_max is None or y_step is None:
        low, high, step = get_rounded_endpoints_and_unit(min(y_coordinates), max(y_coordinates))
        y_min = y_min or low
        y_max = y_max or high
        y_step = y_step or step

    # plots
    fig, ax = plt.subplots()
    ax.scatter(x_coordinates, y_coordinates, s=1, c='blue', vmin=0, vmax=100)
    ax.set(xlim=(x_min, x_max), xticks=np.arange(x_min, x_max + x_step / 100, x_step),
           ylim=(y_min, y_max), yticks=np.arange(y_min, y_max + y_step / 100, y_step))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    # line of regression
    print('rcoef: {}'.format(np.corrcoef(x_coordinates, y_coordinates)[1][0]))
    a, b = np.polyfit(x_coordinates, y_coordinates, 1)
    print('y = {} x + {}'.format(a, b))
    plt.plot(x_coordinates, a * x_coordinates + b, c='red')
    plt.savefig(file_name)
    plt.show()


# methods for question 1
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

    # (i.e. for example names of days, of months or of times of day) and values are lists of frequencies
    # add a column in data frame with names of periods
    data_frame.insert(len(data_frame.columns), 'temporary',
                      [periods_dict.get(val, periods_dict.get(val % len(periods_dict), None))
                       for val in data_frame[column_name_for_periods]])
    # create a dict where keys are values from period dict
    columns_dict = {'from': thresholds[:-1],
                    'to': thresholds[1:]}
    for period_name in set(periods_dict.values()):
        data_frame_by_single_period = data_frame[data_frame['temporary'] == period_name]
        columns_dict[period_name] = get_frequencies(data_frame=data_frame_by_single_period,
                                                    column_name=column_name_for_frequencies,
                                                    thresholds=thresholds)
    # create pandas data frame from our frequencies
    frequencies_data_frame = pd.DataFrame(columns_dict)
    # order columns as in the dictionary
    ordered_columns = list()
    period_names_temp = [name for period, name in sorted(periods_dict.items(), key=lambda x: x[0])]
    for name in period_names_temp:
        if name not in ordered_columns:
            ordered_columns.append(name)
    ordered_columns = ['from', 'to'] + ordered_columns
    frequencies_data_frame = frequencies_data_frame[ordered_columns]
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
    summary_frequencies = pd.DataFrame()
    summary_statistics = pd.DataFrame()
    arr_delays_gathered = pd.DataFrame()
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

        # add frequencies to the dataframe
        summary_frequencies = summary_frequencies.add(dataframes_dict[year], fill_value=0)
        # add summary stats to dataframe
        summary_statistics[year] = data_frame[['ArrDelay']].describe()
        # collect all ArrDelay
        arr_delays_gathered = arr_delays_gathered.append(data_frame.filter(['ArrDelay']))

    # add ArrDelays collected to summary stats
    summary_statistics['total'] = arr_delays_gathered[['ArrDelay']].describe()
    # change raw values to percentages
    if in_percentages:
        for year in years:
            convert_df_to_percentages_by_columns(dataframes_dict[year])
        convert_df_to_percentages_by_columns(summary_frequencies)

    # create excel files
    print(f'Saving all data into  "{excel_name}.xlsx."')
    with pd.ExcelWriter('excel_files/{}.xlsx'.format(excel_name)) as writer:
        for year in years:
            dataframes_dict[year].to_excel(writer, sheet_name=str(year))
        print(f'Saving summary data into  "{excel_name}.xlsx."')
        summary_frequencies.to_excel(writer, sheet_name='summary')
        print(f'Saving summary stats into  "{excel_name}.xlsx."')
        summary_statistics.to_excel(writer, sheet_name='stats')


def get_histograms_for_all_years(my_filter, thresholds, histogram_name_part):
    if thresholds is None:
        thresholds = 500
    print('>>> generating histograms for ' + histogram_name_part.replace('_', ' '))
    for idx, year in enumerate(years):
        print('Analyzing data from year {}. Year {} out of {}.'.format(year, idx + 1, len(years)))

        # get data from pickle
        data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))

        # filter out cancelled flights
        data_frame = data_frame[data_frame['Cancelled'] == 0]

        # filter only the columns that we may need
        data_frame = data_frame.filter(my_filter)

        for day in range(1, 8):
            current_day_data_frame = data_frame[data_frame['DayOfWeek'] == day]

            histogram_data = list(current_day_data_frame['ArrDelay'])

            # Creating histogram
            fig, ax = plt.subplots(figsize=(10, 7))
            ax.set(xlim=(-200, 200), xticks=np.arange(-200, 200, 50))
            ax.hist(histogram_data, bins=thresholds)
            plt.xlabel("arrival delay")
            plt.ylabel("frequency")
            plt.title('Arrival delays per day of week {}, {}'.format(year, days_of_week[day]))
            plt.savefig('images/histogram_{}_{}_{}.png'.format(histogram_name_part, year, day))
            # Show plot
            # plt.show()


def question_1():
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
    get_histograms_for_all_years(my_filter=filter_1_2,
                                 thresholds=None,  # [-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1500],
                                 histogram_name_part='time_of_day')
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


# methods for question 2
def checking_issue_date_vs_year_snippet():
    planes_data_frame = get_data_frame_from_pickle('pickles/pickle_plane-data.pkl')
    # we need only tail number and issue date
    planes_data_frame = planes_data_frame.filter(['tailnum', 'issue_date', 'year'])
    planes_data_frame = planes_data_frame.dropna()
    planes_data_frame = planes_data_frame[
        (planes_data_frame['tailnum'] != 'None') &
        (planes_data_frame['issue_date'] != 'None') &
        (planes_data_frame['year'] != 'None')
        ]

    # a dictionary {tailnumber: issue_date}, where issue_date is datetime object
    issue_dates_of_planes = dict()
    # a dict with keys: 'earlier', 'same', 'later' which compares issue_date to year
    frequency_dict = dict()
    for index, row in planes_data_frame.iterrows():
        issue_date = datetime.strptime(row[1], '%m/%d/%Y')
        issue_dates_of_planes[row[0]] = issue_date
        if issue_date.year < int(row[2]):
            frequency_dict['earlier'] = frequency_dict.get('earlier', 0) + 1
        elif issue_date.year == int(row[2]):
            frequency_dict['same'] = frequency_dict.get('same', 0) + 1
        elif issue_date.year > int(row[2]):
            frequency_dict['later'] = frequency_dict.get('later', 0) + 1
    for k, v in frequency_dict.items():
        print(k.ljust(8) + ': ' + str(v))


def get_pickle_for_question_2(year):
    planes_data_frame = get_data_frame_from_pickle('pickles/pickle_plane-data.pkl')
    # we need only tail number and issue date
    planes_data_frame = planes_data_frame.filter(['tailnum', 'issue_date', 'year'])
    planes_data_frame = planes_data_frame.dropna()
    planes_data_frame = planes_data_frame[
        (planes_data_frame['tailnum'] != 'None') &
        (planes_data_frame['issue_date'] != 'None')
        ]

    # a dictionary {tailnumber: issue_date}, where issue_date is datetime object
    issue_dates_of_planes = dict()
    for index, row in planes_data_frame.iterrows():
        issue_date = datetime.strptime(row[1], '%m/%d/%Y')
        # filter out planes issued before they were produced ;)
        if row[2].isdigit() and issue_date.year < int(row[2]):
            continue
        issue_dates_of_planes[row[0]] = issue_date

    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    my_filter = [
        "Year",
        "Month",
        "DayofMonth",  # to establish the age of a plane
        "TailNum",  # to find 'issue date' of a plane, and hence the age
        "DepDelay"
    ]
    data_frame = data_frame.filter(my_filter)
    data_frame = data_frame.dropna()

    # now we want to make up a list of tuples (age_of_plane [in days], delay [in minutes])
    output_data = list()
    # this was used only to check if there are planes with issue date after travel date
    # planes_travelling_before_their_issue = dict()
    for index, row in data_frame.iterrows():
        # establish date of flight as datetime object
        # firstly as a string:
        date_str = f'{row[0]}/{row[1]}/{row[2]}'  # YYYY/MM/DD
        date_of_flight = datetime.strptime(date_str, '%Y/%m/%d')
        if row[3] not in issue_dates_of_planes:
            continue
        issue_date = issue_dates_of_planes[row[3]]
        age_of_plane = date_of_flight - issue_date
        if age_of_plane.total_seconds() < 0:
            continue
            # planes_travelling_before_their_issue[row[3]] = age_of_plane.total_seconds()
        output_data.append((age_of_plane.days, row[4]))

    x_coordinates = np.array([p[0] for p in output_data])
    y_coordinates = np.array([p[1] for p in output_data])
    delay_vs_age_df = pd.DataFrame({'age': x_coordinates, 'delay': y_coordinates})
    delay_vs_age_df.to_pickle('pickles/delay_vs_age_{}.pkl'.format(year))


def create_scatter_graph_for_question_2(data_frame, year):
    x_coordinates = data_frame['age'].to_numpy()
    y_coordinates = data_frame['delay'].to_numpy()

    # plots
    fig, ax = plt.subplots()
    ax.scatter(x_coordinates, y_coordinates, s=1, c='blue', vmin=0, vmax=100)
    # x_min, x_max = min(x_coordinates), max(x_coordinates)
    # y_min, y_max = min(y_coordinates), max(y_coordinates)
    # print(x_min, x_max)
    # print(y_min, y_max)
    ax.set(xlim=(0, 12000), xticks=np.arange(0, 12000, 2000),
           ylim=(-200, 2650), yticks=np.arange(-200, 2650, 200))
    plt.xlabel("age of plane in days")
    plt.ylabel("arrival delay in minutes")
    plt.title('age of plane and arrival delays in  {}'.format(year))
    plt.savefig('images/age_vs_delay.png')
    plt.show()

    r_coefficient = np.corrcoef(x_coordinates, y_coordinates)
    print('r-coefficient:', r_coefficient[0][1])


def question_2():
    year = 2007
    get_pickle_for_question_2(year)
    delay_vs_age_df = get_data_frame_from_pickle('pickles/delay_vs_age_{}.pkl'.format(year))
    print(delay_vs_age_df.head(7))
    create_scatter_graph_for_question_2(delay_vs_age_df, year)


# methods for question 3
def get_flights_data_for_question_3(year, origin_airports, dest_airports):
    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    my_filter = [
        "TailNum",
        "Cancelled",
        "Origin",
        "Dest"
    ]
    data_frame = data_frame.filter(my_filter)
    data_frame = data_frame[data_frame['Cancelled'] == 0]
    data_frame = data_frame.drop('Cancelled', axis=1)
    data_frame = data_frame.dropna(subset=['Origin', 'Dest'])
    data_frame = data_frame[
        # (data_frame['TailNum'] != 'None') &
        (data_frame['Origin'] != 'None') &
        (data_frame['Dest'] != 'None') &
        (data_frame['Origin'].isin(origin_airports)) &
        (data_frame['Dest'].isin(dest_airports))
        ]
    # we do not filter out TailNum == None as it turns out that before 1995 tail numbers were not collected

    # todo return number of flights and (for year >= 1995) list of tail numbers
    return len(data_frame), list(data_frame.dropna(subset=['TailNum'])['TailNum']) if year >= 1995 else []


def get_origin_and_dest_airports_from_states(origin_states, dest_states):
    # non_us_airports = ['ROP', 'ROR', 'SPN', 'YAP']
    airports_df = get_data_frame_from_pickle('pickles/pickle_airports.pkl')
    airports_df = airports_df.filter(['iata', 'state'])
    origin_airports_df = airports_df[airports_df['state'].isin(origin_states)]
    dest_airports_df = airports_df[airports_df['state'].isin(dest_states)]
    origin_airports = list(origin_airports_df['iata'])
    dest_airports = list(dest_airports_df['iata'])
    return origin_airports, dest_airports


def get_model_capacity_dict():
    # todo get the model_capacity_dict from df / csv
    model_capacity_dict = {
        "EMB-145XR": 37,
        "A320-214": 144,
        "737-3TO": 168,
        "747-422": 660,
        "EMB-145LR": 37,
        "747-451": 376,
        "737-824": 162,
        "EMB-135LR": 37,
        "737-524": 147,
        "767-332": 221,
        "757-224": 200,
        "737-76N": 130,
        "EMB-145EP": 37,
        "DC-9-31": 80,
        "737-724": 85,
        "EMB-135ER": 37,
        "767-3P6": 269,
        "737-3G7": 126,
        "CL-600-2B19": 50,
        "A321-211": 200,
        "737-33A": 144
    }
    return model_capacity_dict


def get_planes_capacity_dict():
    model_capacity_dict = get_model_capacity_dict()
    plane_capacity_dict = dict()
    # get planes data
    planes_data_frame = get_data_frame_from_pickle('pickles/pickle_plane-data.pkl')
    # only tail number and model are in our concern
    planes_data_frame = planes_data_frame.filter(['tailnum', 'model'])
    # filter out when model is not given
    planes_data_frame = planes_data_frame.dropna()
    planes_data_frame = planes_data_frame.set_index('tailnum')
    tailnum_model_dict = planes_data_frame.T.to_dict('index')['model']

    models_with_missing_capacities = set()
    for tail_number, model in tailnum_model_dict.items():
        capacity = model_capacity_dict.get(model, 0)
        if capacity == 0:
            models_with_missing_capacities.add(model)
        plane_capacity_dict[tail_number] = capacity
    print('Capacities for the following models were not found in the dict: {}'
          .format(', '.join(models_with_missing_capacities)))

    return plane_capacity_dict


def get_question_3_dataframe(planes_capacity_dict, origin_airports, dest_airports):
    q3_data_frame = pd.DataFrame(columns=['year',
                                          'number_of_flights',
                                          'number_of_passengers',
                                          'number_of_flights_without_a_record'])
    for year in years[1:-1]:
        # throw out 1987 and 2007 as we don't have data from full years, so we cannot compare them with other years
        number_of_flights, tail_numbers = get_flights_data_for_question_3(year,
                                                                          origin_airports,
                                                                          dest_airports)
        number_of_passengers = sum(planes_capacity_dict.get(tail_number, 0) for tail_number in tail_numbers)
        number_of_flights_without_a_record = len([tail_number for tail_number in tail_numbers
                                                  if tail_number not in planes_capacity_dict])
        yearly_tuple = (year, number_of_flights, number_of_passengers, number_of_flights_without_a_record)
        q3_data_frame = q3_data_frame.append(pd.Series(yearly_tuple, index=q3_data_frame.columns), ignore_index=True)
        with open('excel_files/question_3_data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(yearly_tuple)
        print(yearly_tuple)
    return q3_data_frame


def question_3():
    west_coast_states = ['WA', 'OR', 'CA']
    east_coast_states = ['ME', 'NH', 'MA', 'RI', 'CT', 'NJ', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'FL']
    west_coast_airports, east_coast_airports = get_origin_and_dest_airports_from_states(west_coast_states,
                                                                                        east_coast_states)
    # todo: should this be moved inside get_question_3_dataframe?
    planes_capacity_dict = get_planes_capacity_dict()

    # q3_data_frame will have the following columns:
    # year, number_of_flights, number_of_passengers or 0 / None, number_of_flights_without_a_record
    q3_data_frame = get_question_3_dataframe(planes_capacity_dict, west_coast_airports, east_coast_airports)
    # correlation no of flights on year
    create_scatter_graph_with_regression(data_frame=q3_data_frame,
                                         df_x_column='year',
                                         df_y_column='number_of_flights',
                                         file_name='images/flights_vs_year_scatter_plot.png',
                                         x_label='years',
                                         y_label='number of flights',
                                         title=''
                                         )
    # correlation no of passengers for year >= 1995 on year
    q3_data_frame_from_1995 = q3_data_frame[q3_data_frame['year'] >= 1995]
    q3_data_frame_from_1995 = q3_data_frame_from_1995.dropna()
    create_scatter_graph_with_regression(data_frame=q3_data_frame_from_1995,
                                         df_x_column='year',
                                         df_y_column='number_of_passengers',
                                         file_name='images/passengers_vs_year_scatter_plot.png',
                                         x_label='years',
                                         y_label='number of passengers',
                                         title=''
                                         )
    # (add to graphs) info about percentage of flights where the number of passengers cannot be investigated
    mysterious_flights_df = q3_data_frame_from_1995.filter(['year',
                                                            'number_of_flights',
                                                            'number_of_flights_without_a_record'])
    years_str = [str(year) for year in mysterious_flights_df['year']]
    percentages_str = [str(no_record * 100 // flights) + '%' for no_record, flights in
                       zip(mysterious_flights_df['number_of_flights_without_a_record'],
                           mysterious_flights_df['number_of_flights'])]
    print('percentage of flights with unknown data about planes\' capacity:')
    print(' | '.join(x for x in years_str))
    print(' | '.join(x.rjust(4) for x in percentages_str))


def get_jfk_planes(data_frame,
                   my_filter,
                   from_to,
                   which_delay,
                   delay_value,
                   planes_dict,
                   type_of_planes
                   ):
    # which columns we need
    data_frame = data_frame.filter(my_filter)
    # filter out cancelled flights
    data_frame = data_frame.dropna()
    # either flights TO or FROM JFK
    data_frame = data_frame[data_frame[from_to] == 'JFK']
    # let us consider only arrival / departure delays of more than delay_value (e.g. 60) minutes
    data_frame = data_frame[data_frame[which_delay] > delay_value]
    # add a column in data frame with planes'models
    data_frame.insert(len(data_frame.columns), 'model',
                      [planes_dict.get(tailnumber) for tailnumber in data_frame['TailNum']])
    # and now type of flights, i.e. either small or large ones
    data_frame = data_frame[data_frame['model'].isin(type_of_planes)]
    data_frame = data_frame.reset_index(drop=True)
    return data_frame


def display_cascade(year, cause, effect):
    def get_string(plane, action_verb):
        arr_time_string = '{}{}{}{}'.format(year,                           # year
                                            str(plane[0]).rjust(2, '0'),    # month
                                            plane[1],
                                            plane[2])
        arr_time = datetime.strptime(arr_time_string, '%Y%m%d%H%M')
        date = arr_time.strftime('%d/%m/%Y')
        arr_time_str = arr_time.strftime('%H:%M')
        action_verb_past = action_verb.strip('e')
        ret_str = f'Plane with tail number {plane[5]} was supposed to {action_verb} ' \
                  f'on {date} at {plane[3]}, but it was {plane[4]} minutes late, ' \
                  f'so it {action_verb_past}ed at {arr_time_str}'
        return ret_str

    print(get_string(cause, 'arrive'))
    print(get_string(effect, 'depart'))
    print()


def question_4():
    # get planes data
    planes_data_frame = get_data_frame_from_pickle('pickles/pickle_plane-data.pkl')
    # only tail number and model are in our concern
    planes_data_frame = planes_data_frame.filter(['tailnum', 'model'])
    # filter out when model is not given
    planes_data_frame = planes_data_frame.dropna()
    planes_data_frame = planes_data_frame.set_index('tailnum')
    planes_dict = planes_data_frame.T.to_dict('index')['model']

    # define small planes as those with capacity below 100 passengers
    small_planes = ["A109E", "A-1B", "AS 355F1", "ATR 72-212", "ATR-72-212", "C90",
                    "CL-600-2B19", "CL-600-2C10", "CL600-2D24", "DA 20-A1", "DC-7BF",
                    "DHC-8-102", "DHC-8-202", "E-90", "EMB-120", "EMB-120ER", "EMB-135ER",
                    "EMB-135KL", "EMB-135LR", "EMB-145", "EMB-145EP", "EMB-145EP",
                    "EMB-145LR", "EMB-145XR", "ERJ 190-100 IGW", "EXEC 162F", "F85P-1",
                    "FALCON XP", "FALCON-XP", "G-IV", "HST-550", "KITFOX IV", "M-5-235C",
                    "OTTER DHC-3", "PA-28-180", "PA-31-350", "PA-32R-300", "PA-32RT-300",
                    "S-50A", "S-76A", "SAAB 340B", "T210N", "T337G", "VANS AIRCRAFT RV6"
                    ]

    # define large planes as those with capacity of at least 200 passengers
    large_planes = ["737-832", "737-924", "737-924ER", "737-990", "747-2B5F",
                    "747-422", "747-451", "757-212", "757-222", "757-223",
                    "757-224", "757-225", "757-231", "757-232", "757-23N",
                    "757-251", "757-26D", "757-2B7", "757-2G7", "757-2Q8",
                    "757-2S7", "757-324", "757-33N", "757-351", "767-201",
                    "767-223", "767-224", "767-2B7", "767-322", "767-323",
                    "767-324", "767-332", "767-33A", "767-3CB", "767-3G5",
                    "767-3P6", "767-424ER", "767-432ER", "777-222", "777-224",
                    "777-232", "777-232LR", "A321-211", "A330-223", "A330-323"
                    ]

    # consider year 2007
    year = 2007
    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    # as smaller flights (sometimes) wait for larger flights:
    # firstly, we need large flights to JFK
    filter_to = [
        "Month",
        "DayofMonth",
        "TailNum",
        "ArrTime",
        "CRSArrTime",
        "ArrDelay",
        "Dest"
    ]

    data_frame_to_jfk = get_jfk_planes(data_frame=data_frame,
                                       my_filter=filter_to,
                                       from_to='Dest',
                                       which_delay='ArrDelay',
                                       delay_value=60,
                                       planes_dict=planes_dict,
                                       type_of_planes=large_planes
                                       )
    # secondly, we need smaller flights from JFK
    filter_from = [
        "Month",
        "DayofMonth",
        "TailNum",
        "DepTime",
        "CRSDepTime",
        "ArrDelay",
        "DepDelay",
        "Origin"
    ]
    data_frame_from_jfk = get_jfk_planes(data_frame=data_frame,
                                         my_filter=filter_from,
                                         from_to='Origin',
                                         which_delay='DepDelay',
                                         delay_value=60,
                                         planes_dict=planes_dict,
                                         type_of_planes=small_planes
                                         )
    show(data_frame_to_jfk, 4)
    show(data_frame_from_jfk, 4)
    possible_cascades = dict()
    # key - large plane late to JFK
    # value - list of small planes late from JFK, whose delays could be caused by the large plane
    connection_time = timedelta(minutes=30)
    for index, row in data_frame_to_jfk.iterrows():
        # let us gather data about the large plane (key in the dict):
        plane_late_to_jfk = (row['Month'],
                             row['DayofMonth'],
                             int(row['ArrTime']),
                             row['CRSArrTime'],
                             int(row['ArrDelay']),
                             row['TailNum']
                             )
        # change arrival times (both real and CRS) into datetime objects to include connection time:
        arr_time_datetime = datetime.strptime(str(int(row['ArrTime'])), '%H%M')
        crs_arr_time_datetime = datetime.strptime(str(int(row['CRSArrTime'])), '%H%M')
        # add connection time
        arr_time_datetime_with_connection = arr_time_datetime + connection_time
        crs_arr_time_datetime_with_connection = crs_arr_time_datetime + connection_time
        # change back to integers
        arr_time_with_connection = int(arr_time_datetime_with_connection.strftime('%H%M'))
        crs_arr_time_with_connection = int(crs_arr_time_datetime_with_connection.strftime('%H%M'))
        #
        # now from dataframe of planes late from JFK we have to choose those that can be late because of the plane above
        cascade_planes_df = data_frame_from_jfk[
            # same month
            (data_frame_from_jfk['Month'] == row['Month']) &
            # same day
            (data_frame_from_jfk['DayofMonth'] == row['DayofMonth']) &
            # small plane departs after large plane's arrival
            (data_frame_from_jfk['DepTime'] > arr_time_with_connection) &
            # same for planned times
            (data_frame_from_jfk['CRSDepTime'] > crs_arr_time_with_connection) &
            # planned departure time of small plane was before real arrival time of large
            (data_frame_from_jfk['CRSDepTime'] < row['ArrTime'])
            ]
        if len(cascade_planes_df) > 0:
            possible_cascades[plane_late_to_jfk] = list()
            for index2, row2 in cascade_planes_df.iterrows():
                # append consecutive small planes to the list
                possible_cascades[plane_late_to_jfk].append((row2['Month'],
                                                             row2['DayofMonth'],
                                                             int(row2['DepTime']),
                                                             row2['CRSDepTime'],
                                                             int(row2['DepDelay']),
                                                             row2['TailNum'],
                                                             int(row2['ArrDelay'])
                                                             ))
    # sort large planes by date of flight
    planes_to_jfk = list(possible_cascades.keys())
    planes_to_jfk.sort(key=lambda x: x[1])  # sort by day of month
    planes_to_jfk.sort(key=lambda x: x[0])  # sort by month
    # print out results
    counter = 0
    for large_plane in planes_to_jfk:
        for small_plane in possible_cascades[large_plane]:
            counter += 1
            print(counter)
            display_cascade(year, large_plane, small_plane)


def get_flights_dataframe_for_question_5(year):
    """
    Args:
        year: between 1987 and 2007 incl.
    Returns:
        data frame with all that we need and a list of total arrival delays per month
    """
    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    reasons_for_delay = ['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay']
    my_filter = [
                    "Year",
                    "Month",
                    # "DayofMonth",
                    'Cancelled',
                    "ArrDelay"
                ] + reasons_for_delay
    data_frame = data_frame.filter(my_filter)
    data_frame = data_frame.dropna(subset=reasons_for_delay, how='all')
    data_frame = data_frame[data_frame['Cancelled'] == 0]
    data_frame = data_frame[data_frame['ArrDelay'] > 0]
    data_frame = data_frame.drop('Cancelled', axis=1)
    data_frame = data_frame.reset_index(drop=True)

    return data_frame


def get_delays_reason_data_for_q5():
    # we will collect tuples:
    # (year, month, %CarrierDelay, %WeatherDelay, %NASDelay, %SecurityDelay, %LateAircraftDelay, %other)
    reasons_for_delay = ['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay']
    reasons_data = list()
    for year in years:
        data_frame = get_flights_dataframe_for_question_5(year)
        for month in range(1, 13):
            arr_delay_total = data_frame.loc[data_frame['Month'] == month, 'ArrDelay'].sum()
            row = [year, month]
            for reason_for_delay in reasons_for_delay:
                data_frame_month = data_frame[data_frame['Month'] == month]
                data_frame_month = data_frame_month[data_frame_month[reason_for_delay].notnull()]
                row.append(data_frame_month[reason_for_delay].sum() * 100 // arr_delay_total
                           if len(data_frame_month[reason_for_delay].unique()) else 0)
            row.append(100 - sum(row[-5:]))
            if row[-1] > 95:
                continue
            reasons_data.append(tuple(row))

    return reasons_data


def create_scatter_graph_for_question_5(reasons_list):
    reasons_for_delay = ['Carrier', 'Weather', 'NAS', 'Security', 'Late Aircraft', 'Unknown']
    reasons_data = [list() for _ in range(6)]
    for idx, reason in enumerate(reasons_for_delay):
        reasons_data[idx] = [reasons_list[idx + 2]]
    # https://stackoverflow.com/questions/67582913/plotting-time-series-in-matplotlib-with-month-names-ex-january-and-showing-ye
    # x: points and boundaries
    x_coordinates = pd.Series([datetime(x[0], x[1], 1, 0, 0, 0, 0) for x in reasons_list])
    x_min = datetime(min(x_coordinates).year, min(x_coordinates).month, 1, 0, 0, 0, 0)
    x_max = datetime(max(x_coordinates).year, max(x_coordinates).month, 28, 0, 0, 0, 0)

    # y: points and boundaries
    y_coordinates_list = [pd.Series([x[idx] for x in reasons_list]) for idx in range(2, 8)]
    y_min = 0
    y_max = max(max(y_coordinates) + 2 for y_coordinates in y_coordinates_list)
    y_step = 10
    # Minor ticks every year.
    fmt_year = mdates.YearLocator()

    # plots
    fig, ax = plt.subplots()
    ax.set(xlim=(x_min, x_max),
           ylim=(y_min, y_max), yticks=np.arange(y_min, y_max + y_step / 100, y_step))
    ax.xaxis.set_major_locator(fmt_year)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # font size for labels
    ax.tick_params(labelsize=10, which='both')

    line = [None for _ in range(6)]
    for idx, y_coordinates, c in zip(range(6), y_coordinates_list,
                                     ['blue', 'red', 'orange', 'green', 'black', 'purple']):
        line[idx], = ax.plot(x_coordinates, y_coordinates, c=c, linestyle='solid', label=reasons_for_delay[idx])
    ax.legend(handles=line)
    plt.xlabel('time')
    plt.ylabel('percentage reason')
    plt.title('changes in reasons for delays')

    # todo: line of regression
    # print('rcoef: {}'.format(np.corrcoef(x_coordinates, y_coordinates)[1][0]))
    # a, b = np.polyfit(x_coordinates, y_coordinates, 1)
    # print('y = {} x + {}'.format(a, b))
    # plt.plot(x_coordinates, a * x_coordinates + b, c='red')
    plt.savefig('images/reasons_for_delays.png', dpi=300)
    plt.show()


def get_data_with_distance_for_question_5(year):
    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    my_filter = [
        # "Year",
        # "Month",
        'Cancelled',
        "ArrDelay",
        "Distance"
    ]
    data_frame = data_frame.filter(my_filter)
    data_frame = data_frame.dropna()
    data_frame = data_frame[data_frame['Cancelled'] == 0]
    data_frame = data_frame[data_frame['ArrDelay'] > 0]
    data_frame = data_frame.filter(['Distance', 'ArrDelay'])
    return data_frame


def get_correlation_coefficients_between_distance_and_delay():
    correlation_coefficients = dict()
    for year in years:
        df = get_data_with_distance_for_question_5(year)
        # correlation coefficient
        x_coordinates = df['Distance'].astype(str).astype(float)
        y_coordinates = df['ArrDelay'].astype(str).astype(float)
        rcoef = np.corrcoef(x_coordinates, y_coordinates)[1][0]
        print('correlation coefficient for year {}: {}'.format(year, rcoef))
        correlation_coefficients[year] = rcoef
    return correlation_coefficients


def get_data_with_flight_size_for_question_5(year):
    # get data from pickle
    data_frame = get_data_frame_from_pickle('pickles/pickle_{}.pkl'.format(year))
    my_filter = [
        # "Year",
        # "Month",
        "TailNum",
        'Cancelled',
        "ArrDelay"
    ]
    data_frame = data_frame.filter(my_filter)
    data_frame = data_frame.dropna()
    data_frame = data_frame[data_frame['Cancelled'] == 0]
    data_frame = data_frame[data_frame['ArrDelay'] > 0]
    data_frame = data_frame.reset_index(drop=True)
    if len(data_frame) == 0:
        return None
    data_frame = data_frame.filter(['TailNum', 'ArrDelay'])
    return data_frame


def get_correlation_coefficients_between_flight_size_and_delay():
    planes_capacity_dict = get_planes_capacity_dict()
    correlation_coefficients = dict()
    for year in years:
        df = get_data_with_flight_size_for_question_5(year)
        if df is None:
            continue
        df['flight_size'] = df['TailNum'].map(planes_capacity_dict)
        df = df.dropna()
        df = df.reset_index(drop=True)
        # correlation coefficient
        x_coordinates = df['flight_size'].astype(str).astype(float)
        y_coordinates = df['ArrDelay'].astype(str).astype(float)
        rcoef = np.corrcoef(x_coordinates, y_coordinates)[1][0]
        print('correlation coefficient for year {}: {}'.format(year, rcoef))
        correlation_coefficients[year] = rcoef
    return correlation_coefficients


def question_5():
    # we will trace changes of percentage of all reasons for delays out of all delays
    reasons_list = get_delays_reason_data_for_q5()
    create_scatter_graph_for_question_5(reasons_list)  # nothing interesting here
    correlation_coefficients_1 = \
        get_correlation_coefficients_between_distance_and_delay()  # nothing interesting here
    correlation_coefficients_2 = get_correlation_coefficients_between_flight_size_and_delay() # nothing interesting here


def main():
    t0 = datetime.now()
    # run_only_once_convert_csv_to_pickles()
    # question_1()
    # question_2()
    # question_3()
    # question_4()
    question_5()
    t1 = datetime.now()
    print(t1 - t0)

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
# pd.set_option("display.max_columns", None)  # to see the whole df.head
