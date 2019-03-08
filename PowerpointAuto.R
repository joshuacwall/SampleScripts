#load libraries
library(ggplot2)
library(scales)
library(knitr)
library(reshape2)
library(ggthemes)
library(readxl)
library(sqldf)
library(officer)
library(magrittr)
library(plotly)
library(shiny)


# code block to import needed data
AllTwoYears <- read_excel("data/AllTwoYears.xlsx", 
                          col_types = c("numeric", "date", "text", 
                                        "numeric", "numeric", "numeric"))

Orders <- read_excel("data/Orders.xlsx", 
                          col_types = c("numeric", "date", "numeric", 
                                   "numeric", "numeric", "numeric", 
                                   "numeric", "text", "numeric", "numeric"))

ordersbysystem <- read_excel("data/ordersbysystem.xlsx", 
                          col_types = c("numeric", "date", "numeric", 
                                           "numeric", "numeric","numeric", "numeric", "numeric", "numeric","numeric"))

uniqueparents <- read_excel("data/uniqueparents.xlsx", 
                          col_types = c("numeric", "date", "numeric", 
                                          "numeric", "numeric","numeric", "numeric", "numeric", "numeric","numeric","numeric", "numeric", "numeric", "numeric","numeric"))

childorders.csv <- read_excel("data/childorders.csv.xlsx", 
                          col_types = c("numeric", "date", "numeric", 
                                            "numeric", "numeric","numeric", "numeric", "numeric", "numeric","numeric"))

BigBurst <- read_excel("data/BigBurst.xlsx", 
                          col_types = c("date", "numeric", "numeric"))

IRburst <- read_excel("data/IRburst.xlsx", 
                          col_types = c("date", "numeric", "numeric", "numeric"))

ATSburst <- read_excel("data/ATSburst.xlsx", 
                          col_types = c("date", "numeric", "numeric", "numeric"))



# Order Message Histogram
hist=ggplot(data=AllTwoYears, aes(x = orders, fill = dateyear)) + 
  geom_histogram(aes(y=..density..), position = "stack",
                 col = "blue",
                 breaks=seq(0,1500000,by = 20000))+
  geom_density(aes(x= orders, fill = NULL),col="red", lwd = 1) + 
  labs(x="Volume", y="Density", fill = "Year")+
  scale_y_continuous(label = percent)+
  scale_x_continuous(label = comma)+
  theme_minimal()+
  scale_fill_manual(values = c("deepskyblue", "blue4","green"))+
  theme(legend.position="bottom")

# Order Messages
total=ggplot(data=Orders, aes(x = Date, y = Notional/2000, color = "Principle Traded (USD)")) + 
  geom_line(size = 1) +
  geom_line(aes(y=TotalCount,color = "Order Messages"),size = 1)+
  labs(title = "",x="Date", y="Total Order Messages", color = "")+
  scale_y_continuous(sec.axis = sec_axis(~.*.000002, name = "Principle Traded (Billion)", labels = comma),labels = comma)+
  scale_x_datetime("",labels =  date_format("%b"))+
  scale_color_manual(values = c("blue4", "deepskyblue")) +
  theme(axis.text.x = element_text(hjust = 1),
        axis.title.y.left = element_text(margin = margin(t=0,r=5,b=0)),
        axis.title.y.right = element_text(angle = 90, margin = margin(t=0,r=-5,b=0)),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"),
        legend.position = "bottom")

# Order Messages (By System)
totalsys=ggplot(data=ordersbysystem, aes(x = Date, y = Notional/2000, color = "Principle Traded (USD)")) + 
  geom_line(size = 1) +
  geom_line(aes(y=ATSCount,color = "ATS Messages"),size = 1)+
  geom_line(aes(y=IRCount,color = "IR Messages"),size = 1)+
  labs(title = "",x="Date", y="Total Order Messages", color = "")+
  scale_y_continuous(sec.axis = sec_axis(~.*.000002, name = "Principle Traded (Billion)", labels = comma), labels = comma)+
  scale_x_datetime("",labels =  date_format("%b"))+
  scale_color_manual(values = c("blue4", "green", "deepskyblue")) +
  theme(axis.text.x = element_text(hjust = 1),
        axis.title.y.left = element_text(margin = margin(t=0,r=5,b=0)),
        axis.title.y.right = element_text(angle = 90, margin = margin(t=0,r=-5,b=0)),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"),
        legend.position = "bottom")

# Unique Parents
iraverage = mean(uniqueparents$UniqueParentsIR,na.rm=TRUE)

uparent=ggplot(data=uniqueparents, aes(x = Date, y = Notional/30000, color = "Principle Traded (USD)")) + 
  geom_line(size = 1) +
  geom_line(aes(y=UniqueParentsATS,color = "ATS Messages"),size = 1)+
  geom_line(aes(y=UniqueParentsIR,color = "IR Messages"),size = 1)+
  geom_hline(aes(yintercept= 12000), colour = "red", linetype = "dashed", size = 1)+
  geom_hline(aes(yintercept= iraverage), colour = "black", linetype = "dashed", size = 1)+
  labs(title = "",x="Date", y="Parent Messages", color = "")+
  scale_y_continuous(sec.axis = sec_axis(~.*.0000333, name = "Principle Traded (Billion)", labels = comma), labels = comma)+
  scale_x_datetime("",labels =  date_format("%b"))+
  scale_color_manual(values = c("blue4", "green","deepskyblue")) +
  theme(axis.text.x = element_text(hjust = 1),
        axis.title.y.left = element_text(margin = margin(t=0,r=5,b=0)),
        axis.title.y.right = element_text(angle = 90, margin = margin(t=0,r=-5,b=0)),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"),
        legend.position = "bottom")

# Unique Children
uchild=ggplot(data=childorders.csv, aes(x = Date, y = Notional/300000, color = "Principle Traded (USD)")) + 
  geom_line(size = 1) +
  geom_line(aes(y=ATSCount,color = "ATS Messages"),size = 1)+
  geom_line(aes(y=IRCount,color = "IR Messages"),size = 1)+
  labs(title = "",x="Date", y="Child Messages", color = "")+
  scale_y_continuous(sec.axis = sec_axis(~.*.00025, name = "Principle Traded (Billion)", labels = comma), labels = comma)+
  scale_x_datetime("",labels =  date_format("%b"))+
  scale_color_manual(values = c("blue4", "green","deepskyblue")) +
  theme(axis.text.x = element_text(hjust = 1),
        axis.title.y.left = element_text(margin = margin(t=0,r=5,b=0)),
        axis.title.y.right = element_text(angle = 90, margin = margin(t=0,r=-5,b=0)),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"),
        legend.position = "bottom")

# March 26, 2018 Microburst ATS
ATSAVG = mean(BigBurst$ATS,na.rm=TRUE)

bigATS=ggplot(data=BigBurst, aes(x=Time))+
  geom_line(aes(y=ATS), color = "blue4")+
  scale_y_continuous(labels = comma)+
  scale_x_datetime("",breaks = date_breaks("1 hours"), labels =  date_format("%H:%M:%S"))+
  labs(y = "Order Messages",
       x = "Date",
       title = "ATS",
       colour = "Legend")+
  theme(axis.text.x = element_text(angle = 90,hjust = 1),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"))+
  geom_hline(yintercept=160, color = "red")+
  geom_hline(yintercept=ATSAVG, color = "green")


# March 26, 2018 Microburst IR
IRAVG = mean(BigBurst$IR,na.rm=TRUE)

bigIR=ggplot(data=BigBurst, aes(x=Time))+
  geom_line(aes(y=IR), color = "deepskyblue")+
  scale_y_continuous(labels = comma)+
  scale_x_datetime("",breaks = date_breaks("1 hours"), labels =  date_format("%H:%M:%S"))+
  labs(y = "Order Messages",
       x = "Date",
       title = "IR",
       colour = "Legend")+
  theme(axis.text.x = element_text(angle = 90,hjust = 1),
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"))+
  geom_hline(yintercept=160, color = "red")+
  geom_hline(yintercept=IRAVG, color = "green")


# Last 3 Months Microburst ATS
AVG = mean(ATSburst$Total,na.rm=TRUE)

monATS=ggplot(data=ATSburst, aes(x = Time, y = EMEA, color = "EMEA")) + 
  geom_line(size = 1) +
  geom_line(aes(y=APAC,color = "APAC"),size = 1)+
  labs(title = "ATS",x="", y="Order Messages", color = "")+
  scale_y_continuous(labels = comma)+
  scale_x_datetime("",breaks = date_breaks("1 hours"),labels =  date_format("%H:%M:%S"))+
  scale_color_manual(values = c("blue4", "deepskyblue")) +
  theme(axis.text.x = element_text(angle = 90,hjust = 1),
        axis.title.y = element_text(margin = margin(t=0,r=5,b=0)),
        legend.position = "bottom",
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"))+
  geom_hline(yintercept=160, color = "red")+
  geom_hline(yintercept=AVG, color = "green")

# Last 3 Months Microburst IR
AVG = mean(ATSburst$Total,na.rm=TRUE)

monIR=ggplot(data=IRburst, aes(x = Time, y = EMEA, color = "EMEA")) + 
  geom_line(size = 1) +
  geom_line(aes(y=APAC,color = "APAC"),size = 1)+
  labs(title = "IR",x="", y="Order Messages", color = "")+
  scale_y_continuous(labels = comma)+
  scale_x_datetime("",breaks = date_breaks("1 hours"),labels =  date_format("%H:%M:%S"))+
  scale_color_manual(values = c("blue4", "deepskyblue")) +
  theme(axis.text.x = element_text(angle = 90,hjust = 1),
        axis.title.y = element_text(margin = margin(t=0,r=5,b=0)),
        legend.position = "bottom",
        panel.background = element_blank(),
        panel.grid.major = element_line(colour = "grey"))+
  geom_hline(yintercept=160, color = "red")+
  geom_hline(yintercept=AVG, color = "green")


# Creating Powerpoint
my_pres <- read_pptx("decks/lntemplate.pptx")
layout_properties(my_pres)
my_pres <- read_pptx("decks/lntemplate.pptx")%>%
# Order Message Histogram
  add_slide(layout = "Two Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Order Message Histogram")%>%
  ph_with_gg(index = 1, value = hist)%>%
  ph_with_text(index=2, type = "body", str = "test")%>%
  ph_with_text(index=1, type = "sldNum", str = "test")%>%
# Order Messages
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Order Messages")%>%
  ph_with_gg(value = total)%>%
# Order Messages (By System)
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Order Messages (By System)")%>%
  ph_with_gg(value = totalsys)%>%
# Unique Parents
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Unique Parents")%>%
  ph_with_gg(value = uparent)%>%
# Unique Children
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Unique Children")%>%
  ph_with_gg(value = uchild)%>%
# March 26, 2018 Microburst ATS
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "March 26, 2018 Microburst ATS")%>%
  ph_with_gg(value = bigATS)%>%
# March 26, 2018 Microburst IR
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "March 26, 2018 Microburst IR")%>%
  ph_with_gg(value = bigIR)%>%
# Last 3 Months Microburst ATS
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "Last 3 Months Microburst ATS")%>%
  ph_with_gg(value = monATS)%>%
# Last 3 Months Microburst IR
  add_slide(layout = "One Column", master = "New Theme")%>%
  ph_with_text(type = "title", str = "3 Months Microburst IR")%>%
  ph_with_gg(value = monIR)

print(my_pres, target = "decks/automate.pptx") 


