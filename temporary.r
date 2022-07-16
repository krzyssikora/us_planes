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


csv_data_years_path <- "C:/Users/krzys/Documents/teaching/LSE_Tamara/coursework/dataverse_files/data_years"
csv_data_other_path <- "C:/Users/krzys/Documents/teaching/LSE_Tamara/coursework/dataverse_files/data_other"
years = 999:999

data_years_paths <- list.files(path = csv_data_years_path, pattern = "*.csv", full.names = TRUE)  
data_years <- hash()
for (year in years) {
  # year as a string
  str_year <- as.character(year)
  # read csv file from the year
  yearly_data_frame <- paste(csv_data_years_path, '/', str_year, '.csv', sep='') %>% 
    lapply(read_csv)
  # convert to data frame
  as.data.frame(typeof(yearly_data_frame))
  print(yearly_data_frame)
  # store in a dictionary
  data_years[str_year] <- yearly_data_frame[[1]]
}

# Question 1. When is the best time to fly to minimise delays?
thresholds <- list(-1300, -90, -15, 15, 60, 120, 180, 300, 600, 1200, 1500)
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
  q1_2_data[str_year] <- yearly_data_frame %>% 
    filter(Cancelled == 0) %>%   # filter flights that were not cancelled
    select(Year, DayOfWeek, ArrDelay) %>%   # narrow data down to just 3 columns
    drop_na() %>%                           # drop N/A values
    mutate(day_of_week = names_of_days_of_week[DayOfWeek]) %>%   # add new column with name of day of week
    mutate(arr_delay_interval = cut(ArrDelay, thresholds)) %>%   # new column - delays in intervals
    group_by(day_of_week) %>%
    count(arr_delay_interval) %>%    # count number of different intervals
    mutate(proc = n/sum(n)*100)      # find percentages
}
