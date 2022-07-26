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


my_date <- as.Date('2022/07/26')
class(my_date)
my_date + hours(6)
