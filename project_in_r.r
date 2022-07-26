##### PACKAGES - FOR ALL QUESTIONS #####


# install packages
install.packages('dplyr')
install.packages('tidyverse')
install.packages('tidyr')
install.packages("ggplot2")   # for graphs
install.packages('hash')      # for dictionary-like objects
install.packages("lubridate") # for time manipulation

# load packages
library(dplyr)
library(tidyverse)
library(tidyr)
library(ggplot2)
library(hash)
library(lubridate)




##### GENERAL DATA - FOR ALL QUESTIONS #####




substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}

csv_data_path <- "C:/Users/krzys/Documents/teaching/LSE_Tamara/coursework/dataverse_files"
csv_data_years_path <- paste(csv_data_path, "/data_years", sep = '')
csv_data_other_path <- paste(csv_data_path, "/data_other", sep = '')
years = 1987:2008


data_years <- hash()
for (year in years) {
  # year as a string
  str_year <- as.character(year)
  print(paste('Collecting data for year', str_year))
  # read csv file from the year
  yearly_data_frame <- read.csv(paste(csv_data_years_path, '/', str_year, '.csv', sep=''))
  yearly_data_frame <- as.data.frame(yearly_data_frame)
  yearly_data_frame <- yearly_data_frame %>% 
    filter(Cancelled == 0)   # filter flights that were not cancelled
  # store in a dictionary
  data_years[str_year] <- yearly_data_frame
}



##### QUESTION 1 #####



question_1 <- function() {
  # Question 1. When is the best time to fly to minimise delays?
  thresholds <- c(-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1800)
  # 1.1 time of day - for later
  # 1.2 day of week
  names_of_days_of_week = c('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
  q1_2_data <- hash()
  # loop through all years and get summaries for each year
  for (year in years) {
    # year as a string
    str_year <- as.character(year)
    # take data for the year
    yearly_data_frame <- data_years[[str_year]]
    yearly_data_frame <- as.data.frame(yearly_data_frame)
    q1_2_data[str_year] <- yearly_data_frame %>% 
      select(Year, DayOfWeek, ArrDelay) %>%   # narrow data down to just 3 columns
      drop_na() %>%                           # drop N/A values
      mutate(day_of_week = names_of_days_of_week[DayOfWeek]) # %>%   # add new column with name of day of week
    
    # create daily normalized histograms, i.e. with total area of bars = 1 
    for (day in names_of_days_of_week) {
      daily_delays <- q1_2_data[[str_year]] %>% 
        filter(day_of_week == day)
      just_delays <- daily_delays$ArrDelay
      hist(just_delays,   # Store output of hist function
           main = paste('Arrival delays per day of week', str_year, day, sep = ', '),
           xlab = 'delays in minutes',
           xlim = c(-200,200),
           ylab = 'normalized frequency',
           col = 'blue',
           border = 'purple',
           breaks = 500,  # unlist(thresholds))
           freq = FALSE)
    }
    
    # get data in the same intervals as in Python
    q1_2_data[str_year] <- q1_2_data[[str_year]] %>% 
      mutate(arr_delay_interval = cut(ArrDelay, thresholds)) %>%   # new column - delays in intervals
      count(arr_delay_interval) %>%    # count number of different intervals
      mutate(proc = n/sum(n)*100)      # find percentages
  }
}

question_1()




##### QUESTION 2 #####




# for question 2
plane_data_data_frame <- paste(csv_data_other_path, '/', 'plane-data.csv', sep='') %>% 
  lapply(read_csv)
plane_data_data_frame <- as.data.frame(plane_data_data_frame)
plane_data_data_frame <- plane_data_data_frame %>% 
  drop_na() %>% 
  filter(substrRight(issue_date, 4) >= year ) %>% 
  mutate(plane_date = as.Date(issue_date, "%m/%d/%Y"))

question_2 <- function() {
  q2_plane_data_df <- plane_data_data_frame %>% 
    select(tailnum, plane_date) %>% 
    drop_na()
  
  q2_data <- hash()
  # loop through all years and get summaries for each year
  for (year in 2007:2007) {
    # year as a string
    str_year <- as.character(year)
    
    # take data for the year
    yearly_data_frame <- data_years[[str_year]]
    
    as.data.frame(yearly_data_frame)
    
    q2_data[str_year] <- yearly_data_frame %>% 
      filter(Cancelled == 0) %>%                               # filter flights that were not cancelled
      select(Year, Month, DayofMonth, TailNum, DepDelay) %>%   # narrow data down to 5 columns
      drop_na() %>%                                            # drop N/A values
      mutate(flight_date = as.Date(paste(as.character(Year), '/',# adds a column with date in proper format
                                         as.character(Month), '/',
                                         as.character(DayofMonth),
                                         sep = ''),
                                   "%Y/%m/%d"
      ))
    
    q2_data_frame <- merge(x = q2_data[[str_year]], 
                           y = q2_plane_data_df,
                           by.x = "TailNum",
                           by.y = 'tailnum') %>% 
      mutate(age_of_plane = as.integer(difftime(flight_date, plane_date, units = 'days'))) %>%    # add new column with age of plane
      select(age_of_plane, DepDelay)
    
    x <- q2_data_frame$age_of_plane
    y <- q2_data_frame$DepDelay
    # Plot with main and axis titles
    # Change point shape (pch = 19) and remove frame.
    plot(x, y, main = "age of plane vs delay",
         xlab = "age of plane in days", ylab = "delay in minutes",
         pch = 19, frame = FALSE)
    # Add regression line
    # abline(lm(y ~ x, data = q2_data_frame), col = "blue")
    r_coef <- cor(x, y, method = "pearson", use = "complete.obs")
    print(r_coef)
  }
}

question_2()




##### QUESTION 3 #####




# data for question 3
# firstly, mapping airport to state and region (West / East)
west_coast_states = c('WA', 'OR', 'CA')
east_coast_states = c('ME', 'NH', 'MA', 'RI', 'CT', 'NJ', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'FL')
airports_data_frame <- paste(csv_data_other_path, '/', 'airports.csv', sep='') %>% 
  lapply(read_csv)
airports_data_frame <- as.data.frame(airports_data_frame)
airports_data_frame <- airports_data_frame %>% 
  drop_na() %>% 
  select(iata, state)
airports_data_frame$west_states <- as.list(rep(list(west_coast_states), nrow(airports_data_frame)))
airports_data_frame$east_states <- as.list(rep(list(east_coast_states), nrow(airports_data_frame)))

airports_data_frame$region_w <- c("", "West")[mapply(`%in%`,
                                                     airports_data_frame$state,
                                                     airports_data_frame$west_states) + 1]
airports_data_frame$region_e <- c("", "East")[mapply(`%in%`,
                                                     airports_data_frame$state,
                                                     airports_data_frame$east_states) + 1]
airports_data_frame$region <- paste(airports_data_frame$region_e, 
                                    airports_data_frame$region_w, 
                                    sep = "")
airports_data_frame <- airports_data_frame %>% 
  select(iata, region) %>% 
  filter(!region == "")

# secondly, mapping tail number through model to capacity
csv_path <- paste(csv_data_other_path, '/', 'models_capacities.csv', sep='')
model_capacity_data_frame <- read_csv(csv_path, col_names = c('model', 'capacity'))
model_capacity_data_frame <- as.data.frame(model_capacity_data_frame)

plane_data_data_frame <- paste(csv_data_other_path, '/', 'plane-data.csv', sep='') %>% 
  lapply(read_csv)
plane_data_data_frame <- as.data.frame(plane_data_data_frame) %>% 
  select(tailnum, model) %>% 
  drop_na()

tailnum_capacity_data_frame <- merge(x = model_capacity_data_frame,
                                     y = plane_data_data_frame,
                                     by = 'model') %>% 
  select(tailnum, capacity)

# for each year, get number of flights, total number of passengers, 
# number of flights without known capacity
q3_columns <- c('year', 
                'number_of_flights', 
                'number_of_passengers', 
                'number_of_flights_without_a_record')
# three lines below should be run once only:
q3_data <- data.frame(matrix(nrow = 0, ncol = length(q3_columns))) 
colnames(q3_data) = q3_columns 
write.csv(q3_data, paste(csv_data_path, '/', 'q3_data_R.csv', sep=''), row.names = FALSE)




get_q3_yearly_data <- function(year) {
  # year as a string
  str_year <- as.character(year)
  yearly_data_frame <- data_years[[str_year]]
  as.data.frame(yearly_data_frame)
  print('   getting yearly data')
  yearly_data_frame <- yearly_data_frame %>% 
    filter(Cancelled == 0) %>%          # filter flights that were not cancelled
    select(Origin, Dest, TailNum) %>%   # narrow data down to just 3 columns
    drop_na(Origin, Dest)               # drop N/A values
  # merge with data required for this question
  print('   adding info about origin airports')
  origin_airports_data_frame <- rename(airports_data_frame, origin=iata, origin_region=region)
  yearly_data_frame <- merge(x = yearly_data_frame, 
                             y = origin_airports_data_frame,
                             by.x = "Origin",
                             by.y = "origin")
  print('   filtering dataframe')
  yearly_data_frame <- yearly_data_frame %>%
    filter(origin_region == "West") %>% 
    select(Dest, TailNum)
  print('   adding info about destination airports')
  dest_airports_data_frame <- rename(airports_data_frame, dest=iata, dest_region=region)
  yearly_data_frame <- merge(x = yearly_data_frame, 
                             y = dest_airports_data_frame,
                             by.x = "Dest",
                             by.y = "dest")
  print('   filtering dataframe')
  yearly_data_frame <- yearly_data_frame %>%
    filter(dest_region == "East") %>% 
    select(TailNum)
  print('   adding info about capacity')
  yearly_data_frame <- merge(x = yearly_data_frame, 
                             y = tailnum_capacity_data_frame,
                             by.x = "TailNum",
                             by.y = 'tailnum',
                             all.x = TRUE)
  print('   filtering dataframe')
  yearly_data_frame <- yearly_data_frame %>%
    select(capacity)
  
  # get summaries for this year
  print('   getting summaries for this year')
  number_of_flights <- nrow(yearly_data_frame)
  yearly_data_frame <- yearly_data_frame %>% 
    drop_na()
  number_of_passengers <- sum(yearly_data_frame)
  number_of_flights_without_a_record <- number_of_flights - nrow(yearly_data_frame)
  yearly_summary <- data.frame(year, number_of_flights, number_of_passengers, number_of_flights_without_a_record)
  colnames(yearly_summary) <- c('year',
                                'number_of_flights',
                                'number_of_passengers',
                                'number_of_flights_without_a_record')
  return(yearly_summary)
}


get_q3_data <- function(from, to) {
  # load from csv
  q3_data <- read.csv(paste(csv_data_path, '/', 'q3_data_R.csv', sep=''))
  # convert to data frame
  as.data.frame(q3_data)
  if (!is.null(dim(q3_data))) {
    from <- max(max(q3_data$year + 1), from)
  }
  if (from <= to) {
    for (year in from:to) {
      print(paste('collecting data for year', as.character(year)))
      yearly_summary <- get_q3_yearly_data(year)
      q3_data <- rbind(q3_data, yearly_summary)
      write.csv(q3_data, paste(csv_data_path, '/', 'q3_data_R.csv', sep=''), row.names = FALSE)
    }
  }
  return(q3_data)
}

make_q3_scatter_plot <- function(plot_data, y_column) {
  print(plot_data)
  x <- plot_data$year
  y <- plot_data[,y_column]
  # Plot with main and axis titles
  # Change point shape (pch = 19) and remove frame.
  plot(x, y, main = paste(y_column, "from West to East"),
       xlab = "year", ylab = y_column,
       pch = 19, frame = FALSE)
  # Add regression line
  model <- lm(y ~ x, data = plot_data)
  abline(model, col = "blue")
  print(paste(y_column, 'in time:'))
  r_coef <- cor(x, y, method = "pearson", use = "complete.obs")
  print(paste('correlation coefficient: ', as.character(r_coef)))
  coeffs <- coefficients(model)
  print(paste('Line of regression: y=', as.character(coeffs[2]), 'x +', as.character(coeffs[1])))
} 


question_3 <- function(q3_data) {
  
  q3_data <- get_q3_data(1988, 2007)
  
  make_q3_scatter_plot(q3_data, 'number_of_flights')
  q3_data <- q3_data %>% 
    filter(number_of_passengers > 0)
  make_q3_scatter_plot(q3_data, 'number_of_passengers')
  # year, get number of flights, total number of passengers, number of flights without known capacity
  unknown_capacities <- q3_data %>% 
    mutate(percentage_unknown = number_of_flights_without_a_record / number_of_flights * 100) %>% 
    select(year, percentage_unknown)
  View(unknown_capacities)
}

question_3(q3_data)




##### QUESTION 4 #####




# data for question 4:
# define small planes as those with capacity below 100 passengers
small_planes = c("A109E", "A-1B", "AS 355F1", "ATR 72-212", "ATR-72-212", "C90",
                "CL-600-2B19", "CL-600-2C10", "CL600-2D24", "DA 20-A1", "DC-7BF",
                "DHC-8-102", "DHC-8-202", "E-90", "EMB-120", "EMB-120ER", "EMB-135ER",
                "EMB-135KL", "EMB-135LR", "EMB-145", "EMB-145EP", "EMB-145EP",
                "EMB-145LR", "EMB-145XR", "ERJ 190-100 IGW", "EXEC 162F", "F85P-1",
                "FALCON XP", "FALCON-XP", "G-IV", "HST-550", "KITFOX IV", "M-5-235C",
                "OTTER DHC-3", "PA-28-180", "PA-31-350", "PA-32R-300", "PA-32RT-300",
                "S-50A", "S-76A", "SAAB 340B", "T210N", "T337G", "VANS AIRCRAFT RV6")

# define large planes as those with capacity of at least 200 passengers
large_planes = c("737-832", "737-924", "737-924ER", "737-990", "747-2B5F",
                "747-422", "747-451", "757-212", "757-222", "757-223",
                "757-224", "757-225", "757-231", "757-232", "757-23N",
                "757-251", "757-26D", "757-2B7", "757-2G7", "757-2Q8",
                "757-2S7", "757-324", "757-33N", "757-351", "767-201",
                "767-223", "767-224", "767-2B7", "767-322", "767-323",
                "767-324", "767-332", "767-33A", "767-3CB", "767-3G5",
                "767-3P6", "767-424ER", "767-432ER", "777-222", "777-224",
                "777-232", "777-232LR", "A321-211", "A330-223", "A330-323")
# prepare a dataframe with info whether a tailnumber is for a small or a large plane
# (other planes will not be included)
planes_data_frame <- read.csv(paste(csv_data_other_path, '/', 'plane-data.csv', sep=''))
planes_data_frame <- as.data.frame(planes_data_frame)
planes_data_frame <- planes_data_frame %>% 
  select(tailnum, model) %>% 
  drop_na()

planes_data_frame$small_planes <- as.list(rep(list(small_planes), nrow(planes_data_frame)))
planes_data_frame$large_planes <- as.list(rep(list(large_planes), nrow(planes_data_frame)))

planes_data_frame$plane_type_small <- c("", "small")[mapply(`%in%`,
                                                            planes_data_frame$model,
                                                            planes_data_frame$small_planes) + 1]
planes_data_frame$plane_type_large <- c("", "large")[mapply(`%in%`,
                                                            planes_data_frame$model,
                                                            planes_data_frame$large_planes) + 1]
planes_data_frame$plane_type <- paste(planes_data_frame$plane_type_small, 
                                      planes_data_frame$plane_type_large,
                                      sep = "")
planes_data_frame <- planes_data_frame %>% 
  select(tailnum, plane_type) %>% 
  filter(!plane_type == "")

# get small planes from JFK and large to JFK from the year
connection_time = 30
delay_value = 60
year = 2007
str_year <- as.character(year)
yearly_data_frame <- data_years[[str_year]]

as.data.frame(yearly_data_frame)

yearly_data_frame <- yearly_data_frame %>% 
  filter(Cancelled == 0) %>%                               # filter flights that were not cancelled
  select(Year, Month, DayofMonth, 
         TailNum, 
         ArrTime, CRSArrTime, ArrDelay, 
         DepTime, CRSDepTime, DepDelay,
         Origin, Dest) %>%                                 # narrow data
  filter((Origin == 'JFK') | (Dest == 'JFK')) %>% 
  drop_na() %>%                                            # drop N/A values
  mutate(flight_date = as.Date(paste(as.character(Year), '/',# adds a column with date in proper format
                                     as.character(Month), '/',
                                     as.character(DayofMonth),
                                     sep = ''),
                               "%Y/%m/%d"
  )) %>% 
  select(-c(Year, Month, DayofMonth)) %>% 
  mutate(arr_time = flight_date 
         + hours(floor(ArrTime / 100))
         + minutes(ArrTime %% 100)
         ) %>% 
  select(-ArrTime) %>% 
  mutate(arr_time_w_connection = arr_time
         + minutes(connection_time)) %>% 
  mutate(crs_arr_time = flight_date
         + hours(floor(CRSArrTime / 100))
         + minutes(CRSArrTime %% 100)
         ) %>% 
  select(-CRSArrTime) %>% 
  mutate(crs_arr_time_w_connection = crs_arr_time
         + minutes(connection_time)) %>% 
  mutate(dep_time = flight_date 
         + hours(floor(DepTime / 100))
         + minutes(DepTime %% 100)
  ) %>% 
  select(-DepTime) %>% 
  mutate(crs_dep_time = flight_date
         + hours(floor(CRSDepTime / 100))
         + minutes(CRSDepTime %% 100)
  ) %>% 
  select(TailNum, Origin, Dest, flight_date,
         arr_time, arr_time_w_connection, crs_arr_time, crs_arr_time_w_connection, ArrDelay, 
         dep_time, crs_dep_time, DepDelay)
  

q4_data_frame <- merge(x = yearly_data_frame, 
                       y = planes_data_frame,
                       by.x = "TailNum",
                       by.y = 'tailnum')

large_planes_to_JFK <- q4_data_frame %>% 
  filter((Dest == 'JFK') &
           (plane_type == 'large') &
           (ArrDelay > delay_value)) %>% 
#  select(TailNum, flight_date, arr_time, arr_time_w_connection, crs_arr_time, crs_arr_time_w_connection, ArrDelay, dep_time, crs_dep_time, DepDelay)
  select(TailNum, flight_date, arr_time, arr_time_w_connection, crs_arr_time, crs_arr_time_w_connection, ArrDelay)

small_planes_from_JFK <- q4_data_frame %>% 
  filter((Origin == 'JFK') &
           (plane_type == 'small') &
           (ArrDelay > delay_value)) %>% 
  select(TailNum, flight_date, dep_time, crs_dep_time, DepDelay, ArrDelay)

# prepare an empty csv file to store data about possible cascading delays
q4_cascades_columns <- c('tailnumber_large',
                         'planned_arrival',
                         'arr_delay',
                         'real_arrival',
                         'tailnumber_small',
                         'planned_departure',
                         'dep_delay',
                         'real_dep')
# three lines below should be run once only:
q4_cascades_data <- data.frame(matrix(nrow = 0, ncol = length(q4_cascades_columns))) 
colnames(q4_cascades_data) = q4_cascades_columns 
write.csv(q4_cascades_data, paste(csv_data_path, '/', 'q4_cascades_data_R.csv', sep=''), row.names = FALSE)

# loop through large planes to find for each large plane those small planes that could be late because of the large one
for (idx in 1:nrow(large_planes_to_JFK)) {
  # collect large plane data
  # those that we will need for csv
  tailnumber_large <-
    as.character(large_planes_to_JFK[idx,]['TailNum'])
  planned_arrival <-
    as.POSIXct(large_planes_to_JFK[idx,]['crs_arr_time'][[1]])
  arr_delay <- as.numeric(large_planes_to_JFK[idx,]['ArrDelay'])
  real_arrival <-
    as.POSIXct(large_planes_to_JFK[idx,]['arr_time'][[1]])
  # those that we will not need for csv
  flight_date_large_plane = as.Date(large_planes_to_JFK[idx,]['flight_date'][[1]])
  arrival_w_connection <-
    as.POSIXct(large_planes_to_JFK[idx,]['arr_time_w_connection'][[1]])
  planned_arrival_w_connection <-
    as.POSIXct(large_planes_to_JFK[idx,]['crs_arr_time_w_connection'][[1]])
  # find small planes
  temp_small_planes <- small_planes_from_JFK %>%
    filter((flight_date == flight_date_large_plane) &
             (dep_time > arrival_w_connection) &
             (crs_dep_time > planned_arrival_w_connection) &
             (crs_dep_time < real_arrival)
    )
  # loop through small planes to add all pairs (large, small) to csv
  if(nrow(temp_small_planes) > 0) {
    for (idx2 in 1:nrow(temp_small_planes)) {
      # collect small plane data for csv
      tailnumber_small <-
        as.character(temp_small_planes[idx2,]['TailNum'])
      planned_departure <-
        as.POSIXct(temp_small_planes[idx2,]['crs_dep_time'][[1]])
      dep_delay <- as.numeric(temp_small_planes[idx2,]['DepDelay'])
      real_dep <-
        as.POSIXct(temp_small_planes[idx2,]['dep_time'][[1]])
      cascade_summary <-
        data.frame(
          tailnumber_large,
          planned_arrival,
          arr_delay,
          real_arrival,
          tailnumber_small,
          planned_departure,
          dep_delay,
          real_dep
        )
      colnames(cascade_summary) <- q4_cascades_columns
      q4_cascades_data <- rbind(q4_cascades_data, cascade_summary)
      write.csv(
        q4_cascades_data,
        paste(csv_data_path, '/', 'q4_cascades_data_R.csv', sep = ''),
        row.names = FALSE
      )
    }
  }
}

# get the information printed into txt file
q4_data <- read.csv(paste(csv_data_path, '/', 'q4_cascades_data_R.csv', sep=''))
for (idx in 1:nrow(q4_data)) {
  tailnumber_large <- as.character(q4_data[idx, ]['tailnumber_large'])
  planned_arrival <- as.character(q4_data[idx, ]['planned_arrival'])
  arr_delay <- as.character(q4_data[idx, ]['arr_delay'])
  real_arrival <- as.character(q4_data[idx, ]['real_arrival'])
  tailnumber_small <- as.character(q4_data[idx, ]['tailnumber_small'])
  planned_departure <- as.character(q4_data[idx, ]['planned_departure'])
  dep_delay <- as.character(q4_data[idx, ]['dep_delay'])
  real_dep <- as.character(q4_data[idx, ]['real_dep'])
  message <- paste(as.character(idx),
                   '\n',
                   'Plane with tail number ', 
                   tailnumber_large, 
                   ' was supposed to arrive at ', 
                   planned_arrival,
                   ', but it was ',
                   arr_delay,
                   ' minutes late, so it arrived at ',
                   real_arrival,
                   '. Plane with tail number ',
                   tailnumber_small,
                   ' was supposed to depart at ',
                   planned_departure,
                   ' but it was ',
                   dep_delay,
                   ' minutes late, so it departed at ',
                   real_dep,
                   '. \n',
                   sep = '')
  write(message,file="q4_output_R.txt",append=TRUE)
}
