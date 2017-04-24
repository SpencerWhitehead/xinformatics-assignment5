# Sales Data Interface Backend
# Xinformatics Final Project
# By Team 5
# Curated by Hannah De los Santos
# Last update: 4/19/17

# load packages ----

require(ggplot2)
library(reshape2)
library(dplyr)
library(broom)

# load and format data ----

# load data, assumed to have column names
sales_data <- read.csv("C:\\Users\\delosh\\Documents\\Grad Year 1 Spring Semester 2017\\X-Informatics\\train.csv", header = TRUE)

# user input data - assumed to be text 
input_data <- read.table("filename", sep = "x")

# exploratory analysis ----

# goals: sales graph generation
# bar charts and histograms based on statistics
# number of customers, sales based on the week

# multiple store graphs
# strtoi(thing)

mult_store_number <- c(1,2,3)
store_var <- as.character("Store")
var_of_interest_x <- as.character("Store")
var_of_interest_y <- as.character("Sales")

sub.df <- subset(sales_data,(sales_data[,var_of_interest_x] %in% mult_store_number))
sub.df[,var_of_interest_x] <- as.factor(sub.df[,var_of_interest_x])

# density plot
# colors after decisions

# density plot
# colors after decisions
p <- ggplot(sub.df,aes_string(var_of_interest_y)) + 
  geom_density(alpha = .1, aes_string(fill=var_of_interest_x, color = var_of_interest_x))+
  ggtitle("title here")+
  labs(x="def",y="Density")

# dot plot
var_of_interest_x <- as.character("Date")
p <- ggplot(sub.df,aes_string(var_of_interest_x,var_of_interest_y)) + 
  geom_point(aes_string(fill=store_var, color = store_var)) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, size = .3))+
  ggtitle("title here")+
  labs(x="TimeUnit",y="VarofInterest")

# text

t <- tidy(summary(fivenum(sub.df[,"Sales"])))

# sales regression ----

time_var <- as.character("Date")
times <- c(1:length(unique(sales_data[,time_var])))
var_of_interest_x <- as.character("Store")

# number of stores
#do linear regression
lin_reg <- lm(subset(sales_data,(sales_data[,var_of_interest_x] %in% 1))$Sales ~ times)
coeff <- lin_reg$coefficients # resulting coefficients

res <- coeff[1] + (coeff[2]*times)

lr.df <- data.frame(times =times,date=unique(sales_data[,time_var]),original=sales_data[sales_data[,var_of_interest_x] %in% 1,"Sales"], result=res)

p <- ggplot(lr.df) +
  geom_point(aes(times,original))+
  geom_line(aes(times,result), size = 2, color="red", alpha = .5)+
  ggtitle("x Regression")+
  labs(x="TimeUnit",y="VariableofInterest")

# add text output
t <- tidy(lin_reg)

# save output ----

# save image
png(filename = "filename_extension.png")
plot(p)
dev.off()

# save text
write.table(t, file = "somehting.txt")
