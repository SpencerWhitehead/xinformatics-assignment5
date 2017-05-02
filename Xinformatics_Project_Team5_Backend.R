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
input_data <- read.table("C:\\Users\\delosh\\Documents\\Grad Year 1 Spring Semester 2017\\X-Informatics\\annotated.txt", sep = "~")


# goals: sales graph generation
# densities and dot plots based on statistics
# number of customers, sales based on the week

# get the variables based on input
analysis_type <- as.character(input_data[1,1])
var_of_interest <- as.character(input_data[2,1])
store_vars <- as.character(input_data[3,1])
store_lab <- as.character(input_data[4,1])
time_lab <- as.character(input_data[5,1])
plot_title <- as.character(input_data[6,1])
y_axis_title <- as.character(input_data[7,1])
time_unit <- as.character(input_data[8,1])

# parse the stores
if(store_vars != "all"){
  store_vars <- as.numeric(unlist(strsplit(store_vars,",")))
} else{
  store_vars <- unique(sales_data[,store_lab])
}

#subset the data for what stores we want to look at
sub.df <- subset(sales_data,(sales_data[,store_lab] %in% store_vars))
sub.df[,store_lab] <- as.factor(sub.df[,store_lab])

# exploratory analysis ----


if (analysis_type=="density"){

# density plot
# colors after decisions
p <- ggplot(sub.df,aes_string(var_of_interest)) + 
  geom_density(alpha = .1, aes_string(fill=store_lab, color = store_lab))+
  ggtitle(plot_title)+
  labs(x=y_axis_title,y="Density")+
  theme(plot.title = element_text(hjust = 0.5))

t <- tidy(summary(fivenum(sub.df[,var_of_interest])))
} else if(analysis_type=="dot"){
# dot plot
var_of_interest_x <- as.character("Date")
p <- ggplot(sub.df,aes_string(time_lab,var_of_interest)) + 
  geom_point(aes_string(fill=store_lab, color = store_lab)) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, size = .3))+
  ggtitle(plot_title)+
  labs(x=time_unit,y=y_axis_title)+
  theme(plot.title = element_text(hjust = 0.5))

# text

t <- tidy(summary(fivenum(sub.df[,var_of_interest])))
} else {
# sales regression ----

times <- c(1:length(unique(sales_data[,time_lab])))

#do linear regression
lin_reg <- lm(subset(sales_data,(sales_data[,store_lab] %in% store_vars))[,var_of_interest] ~ times)
coeff <- lin_reg$coefficients # resulting coefficients

# resulting y values
res <- coeff[1] + (coeff[2]*times)

# put results and original into easy to access dataframe
lr.df <- data.frame(times =times,date=unique(sales_data[,time_lab]),original=sales_data[sales_data[,store_lab] %in% store_vars,var_of_interest], result=res)

# linear regression plot
p <- ggplot(lr.df) +
  geom_point(aes(times,original))+
  geom_line(aes(times,result), size = 2, color="blue", alpha = .5)+
  ggtitle(plot_title)+
  labs(x=time_unit,y=var_of_interest)+
  theme(plot.title = element_text(hjust = 0.5))

# add text output
t <- tidy(lin_reg)
}

# save output ----

# save image
png(filename = "Density.png", pointsize = 26,width = 620, height = 420)
plot(p)
dev.off()

# save text
write.table(t, file = "5numbersummary.txt")
