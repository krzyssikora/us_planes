# install packages
install.packages('dplyr')
install.packages('tidyverse')
install.packages('tidyr')
install.packages("ggplot2") # for graphs
install.packages('hash')   # for dictionary-like objects

# load packages
library(dplyr)
library(tidyverse)
library(tidyr)
library(ggplot2)
library(hash)

substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}

csv_data_path <- "C:/Users/krzys/Documents/teaching/LSE_Tamara/coursework/dataverse_files"
csv_data_years_path <- paste(csv_data_path, "/data_years", sep = '')
csv_data_other_path <- paste(csv_data_path, "/data_other", sep = '')
years = 1987:2008

# for all questions
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
