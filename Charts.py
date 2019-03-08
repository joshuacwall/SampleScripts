import cx_Oracle
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib.dates import DateFormatter
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from sqlalchemy import create_engine
import datetime
from datetime import timedelta 
import sys
import pytz


##if the script is ran independetly, the condition will be false. If ran as part the the shell script report.sh, this condition will be true
##reads the arguement condidtions handed by report.sh
if len(sys.argv) > 1:
    date = sys.argv[1]
    lastyear = sys.argv[2]
    runUK = sys.argv[3]
    runNJ = sys.argv[4]


# used if the variables script doesnt work or if this script is ran independently
else: 
    # used if the variables script doesnt work or if this script is ran independently
    ##input the date you want to run the report for
    print("What date do you want to start at?")
    day = input("What day?(d) ")
    month = input("What month?(m) ")
    year = input("What year?(YYYY) ")
    day = datetime.datetime(int(year),int(month),int(day))
    #format date in readable form for sql queries
    date = day.strftime('%Y-%m-%d')
    lastyear = (day-timedelta(days=180)).strftime('%Y-%m-%d')
    ##decide whether you want to run the report for the UK instances, NJ instances or both
    runUK = input("Run UK(yes/no): ").lower()
    runNJ = input("Run NJ(yes/no): ").lower()

#csv file where data about each instance is kept and stored. This includes; name, sqlite table, region, and various capacity figures (0 if capacity number is unknown)
instances = pd.read_csv("instances.csv")
#Open DB connections to Capacity(sqlite)
disk_engine = create_engine('sqlite:///Capacity.db')

##looks through all the instances found in the instance csv file (to add a new instance, add its properties to the file)
for index,row in instances.iterrows():

    ##based off variable created in the beginning (either manually or fed from the shell script) determines whether or not to continue with that particular instance 
    if (runUK == 'DO NOT RUN UK' or runUK == 'no' or runUK == 'n') and (row['Region'] =='UK'):
        continue
    if (runNJ == 'DO NOT RUN NJ' or runNJ == 'no' or runNJ == 'n') and (row['Region'] =='NJ'):
        continue
    #create pdf to save the charts in
    pp = PdfPages('report/CapacityCharts'+ row['Instance'] +'.pdf')

    #date and time formats
    dayFormat = DateFormatter("%d/%m/%Y") 
    timeFmt = DateFormatter("%H:%M") 
    
    if row['Region'] == 'UK':
        tz = 'Europe/London'
    else:
        tz = 'America/New_York'

    ###########################
    #Concurrent Active Orders
    with open('queries/SQLite/ActiveOrders.txt', 'r') as myfile:
        query=myfile.read()
    #grab Active Parent Order Data for date of report
    ActiveParentOrders = pd.read_sql_query(query.format(row['Table'],date,'Parent',row['Instance']),disk_engine,parse_dates=['DSTAMP'])
    ActiveParentOrders['DSTAMP'] = ActiveParentOrders['DSTAMP'].dt.tz_localize('UTC').dt.tz_convert(tz)

    #grab Active Child Order Data for date of report
    ActiveChildOrders = pd.read_sql_query(query.format(row['Table'],date,'Child',row['Instance']),disk_engine,parse_dates=['DSTAMP'])
    ActiveChildOrders['DSTAMP'] = ActiveChildOrders['DSTAMP'].dt.tz_localize('UTC').dt.tz_convert(tz)

    #combine ActiveParentOrder and ActiveChildOrder Data for total ActiveOrders
    ActiveOrders = pd.merge(ActiveParentOrders,ActiveChildOrders,on='DSTAMP')
    ActiveOrders['TOTAL_ORD'] = ActiveOrders['TOTAL_ORD_x'] + ActiveOrders['TOTAL_ORD_y']
    ActiveOrders['STARTING'] = ActiveOrders['STARTING_x'] + ActiveOrders['STARTING_y']

    ##Create Active Orders Summary Stats Table
    #select columns wanted to be used
    ActiveOrders.columns = ['Active Parents','Parents Starting','DSTAMP','Active Children','Children Starting','Active Orders','Orders Starting']
    #rename, transpose and describe column information
    ActiveTable = np.round(ActiveOrders[['Active Orders','Orders Starting','Active Parents','Parents Starting','Active Children','Children Starting']].describe(),0).T
    #find mean and max for each column
    ActiveTable = ActiveTable[['mean','max']].astype(int)
    #format values with commas and no decimals
    ActiveTable['mean'] = ActiveTable['mean'].map('{:,}'.format)
    ActiveTable['max'] = ActiveTable['max'].map('{:,}'.format)
    #rename new column headers
    ActiveTable.columns=[['Mean per Second','Max per Second']]

    ##Create Daily Orders Summary Stats Table
    DailyTable = ActiveOrders[['Orders Starting','Parents Starting','Children Starting']]
    #rename columns headers
    DailyTable.columns = ['Total','Parent','Child']
    #sum each column
    DailyTable = DailyTable.sum()
    #format to include commas and no decimals
    DailyTable = DailyTable.map('{:,}'.format)
    #transpose and format to be a 2x4 matrix
    DailyTable = DailyTable.to_frame()
    #name new header
    DailyTable.columns = ['Daily Orders']

    ##Get Daily C_P_Ratio 
    #gather parent and child starting order figures by second
    C_P_Ratio = ActiveOrders[['Parents Starting','Children Starting']]
    #aggregate them for the entire day to get the daily count
    C_P_Ratio = C_P_Ratio.sum()
    #divid total child by total parent
    parent = C_P_Ratio.loc['Parents Starting',]
    child = C_P_Ratio.loc['Children Starting',]
    C_P_Ratio = child/parent
    #format with comma and no decimals
    "{:,}".format(C_P_Ratio)
    C_P_Ratio = str(int(C_P_Ratio))

    #Send tables to HTML file
    with open('report/SummaryStats'+row['Instance']+'.html','w') as _file:
        _file.write("<font size='6'><strong>"+row['Instance']+" Capacity Stats for "+ date + "</strong></font><br><br>"+ "\n\n" + "<b><i><u>Active Orders Summary</u></i></b>" + "\n\n" + ActiveTable.to_html() + "\n\n"+ "<b><i><u>" + "Daily Order Summary"+ "</u></i></b>" + "\n\n" + DailyTable.to_html() + "\n\n" + "<b><i><u>" + "Child/Parent Ratio:" + "</u></i></b>" + " " + "\n\n" + "<b>" + C_P_Ratio + "</b><br><br>" + "<b>The following link will lead to a confluence page with chart and table descriptions:</b><br>" + "https://confluence.liquidnet.com/display/ETECH/EMEA+IR+Capacity"+ "<br><br>" )

    #define plots function
    def activeplots (x,y1,y2,capacity,title):
        "Creates Active Orders/Starting Orders plot with the Active orders being aligned with the left Y axis and the starting orders being aligned on the right"
        #create subplot for multiple y-axis and lines
        fig, ax1 = plt.subplots()
        plt.grid()
        #name main axis
        ax1.set_xlabel('Time ' + tz)
        ax1.set_ylabel('Orders Active')
        #plot active orders
        l1, = ax1.plot(x,y1, color='tab:red', Label = True)
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.set_title(title)
        #format x-axis
        plt.xticks(rotation=45)
        ax1.xaxis.set_major_formatter(timeFmt)
        #set second plots x-axis to the same as the first
        ax2 = ax1.twinx()
        #name second y-axis
        ax2.set_ylabel('Orders per Second')
        #plot order creation rate
        l2, = ax2.plot(x,y2, color='tab:blue')
        #format line and axis
        ax2.tick_params(axis='y', labelcolor='tab:blue')
        ax2.xaxis.set_major_formatter(timeFmt)
        ax1.set_zorder(ax2.get_zorder()+1)
        ax1.patch.set_visible(False)
        #create horizontal capacity line
        capline = pd.Series(capacity)
        capline = capline.repeat(x.count())
        l3, = ax1.plot(x,capline, color = 'tab:green')
        #create and format legend to hold all three graphs
        ax1.legend([l1,l2,l3], ['Orders Active','Orders Starting','Active Capacity'], loc="upper left")
        fig.tight_layout()
        #save it to open pdf
        plt.savefig(pp, format='pdf')
        return

    ##Total active orders
    #Shows the currently active order (sum of parent and child) by second throughout the day
    activeplots(ActiveOrders['DSTAMP'],ActiveOrders['Active Orders'],ActiveOrders['Orders Starting'],row['TotalConcurrentCap'],row['Instance']+' Total Orders')
    ##Active parent orders
    #Shows the currently active parent order by second throughout the day
    activeplots(ActiveParentOrders['DSTAMP'],ActiveParentOrders['TOTAL_ORD'],ActiveParentOrders['STARTING'],row['ParentConcurrentCap'],row['Instance']+' Parent Orders')
    ##Active child orders
    #Shows the currently active child order by second throughout the day
    activeplots(ActiveChildOrders['DSTAMP'],ActiveChildOrders['TOTAL_ORD'],ActiveChildOrders['STARTING'],row['ChildConcurrentCap'],row['Instance']+' Child Orders')


    ###########################
    #Aggregate Daily Orders
    with open('queries/SQLite/DailyOrders.txt', 'r') as myfile:
        query=myfile.read()
    #Parent Order data
    #query gets historical parent order data aggregated at the day level and filters out any weekends
    ParentOrders = pd.read_sql_query(query.format(row['Table'],row['Region'],'Parent',lastyear,date,row['Instance']),disk_engine,parse_dates=['DSTAMP'])
    ParentOrders['Weekday'] = [datetime.datetime.weekday(d) for d in ParentOrders['DSTAMP']] #0 = monday
    ParentOrders = ParentOrders.loc[ParentOrders['Weekday'] <= 4]
    #Child Order data
    #query gets historical child order data aggregated at the day level and filters out any weekends
    ChildOrders = pd.read_sql_query(query.format(row['Table'],row['Region'],'Child',lastyear,date,row['Instance']),disk_engine,parse_dates=['DSTAMP'])
    ChildOrders['Weekday'] = [datetime.datetime.weekday(d) for d in ChildOrders['DSTAMP']] #0 = monday
    ChildOrders = ChildOrders.loc[ChildOrders['Weekday'] <= 4]
    #Total Order Data
    #merges the two previous queries into a single query 
    TotalOrders = pd.merge(ParentOrders,ChildOrders,on='DSTAMP')
    #combine bursts by second interval
    TotalOrders['Burst'] = TotalOrders['Burst_x'] + TotalOrders['Burst_y']
    #combine orders by second interval
    TotalOrders['Orders'] = TotalOrders['Orders_x'] + TotalOrders['Orders_y']
    #find historical child/parent ratios
    TotalOrders['C_P_Ratio'] = TotalOrders['Orders_y']/TotalOrders['Orders_x']
    #combine active orders at second interval
    TotalOrders['Active'] = TotalOrders['Active_x'] + TotalOrders['Active_y']
    #name columns
    TotalOrders = TotalOrders[['DSTAMP','Burst','Orders','C_P_Ratio','Active']]


    #define plots function
    def forecast(x,y,capacity,ytitle,title):
        "creates line plot of max concurrent orders and a forecasting trendline."
        #create Linear trendline
        y_values = y
        #converts timestamps to epoch numbers that can be used in regression
        x_values = x.map(lambda i: (i - pd.datetime(1970,1,1)).days)
        #desinating linear trendline
        poly_degree = 1
        #finding coefficients
        coeffs = np.polyfit(x_values,y_values,poly_degree)
        #creating polynomial equations (aka equation for best fit line)
        poly_eqn = np.poly1d(coeffs)
        #finding new y-value (y_hat) for forecasted x-value(newx)
        diff = max(x_values) - min(x_values)
        newx = pd.Series([max(x_values)+ diff])
        x_values = pd.concat([x_values,newx])
        y_hat = poly_eqn(x_values)
        #plot max concurrent orders against linear trendline
        fig , ax = plt.subplots()
        plt.grid()
        #labels plot
        ax.set_xlabel('Date')
        ax.set_ylabel(ytitle)
        #plot known figures
        l1,= ax.plot(x,y, color='tab:blue')
        #add date to tradedate to extend forcast
        newx = pd.Series([max(x)+timedelta(days=diff)])
        x = pd.concat([x,newx])
        #declare capacity line
        capline = pd.Series(capacity)
        capline = capline.repeat(x.count())
        #plot trendline
        l2,= ax.plot(x,y_hat, color='tab:red')
        #plot capacity limit line
        l3, = ax.plot(x,capline, color='tab:green')
        #format axis
        ax.set_title(title)
        plt.xticks(rotation=45)
        ax.xaxis.set_major_formatter(dayFormat)
        #create and format lengend
        plt.legend([l1,l2,l3], ['Orders','Forecast','Capacity'], loc="upper left")
        fig.tight_layout()
        #save to pdf
        plt.savefig(pp, format='pdf')
        return

    ##Total Orders 
    ##Daily Orders
    #aggregated total order by day. Shows historical trendline and projection
    forecast(TotalOrders['DSTAMP'],TotalOrders['Orders'],row['TotalCapacity'],'Orders',row['Instance'] + ' Daily Orders')
    ##Daily Max Active Orders
    #max active order by day. Shows historical trendline and projection
    forecast(TotalOrders['DSTAMP'],TotalOrders['Active'],row['TotalConcurrentCap'],'Active Orders per Second',row['Instance'] + ' Daily Max Active Orders')
    ##Max Order Burst
    #max order creation rate by day. Shows historical trendline and projection
    forecast(TotalOrders['DSTAMP'],TotalOrders['Burst'],row['TotalBurstCapacity'],'Orders per Second',row['Instance'] + ' Daily Max Order Creation Rate')
    ##Daily C_P_Ratio
    #child/parent ratio by day. Shows historical trendline and projection
    forecast(TotalOrders['DSTAMP'],TotalOrders['C_P_Ratio'],row['Child/ParentRatioCapacity'],'Child/Parent Ratio',row['Instance'] + ' Daily Child/Parent Ratio')


    ##Parent Orders
    ##Daily Parent Orders
    #aggregated parent order by day. Shows historical trendline and projection
    forecast(ParentOrders['DSTAMP'],ParentOrders['Orders'],row['ParentCapacity'],'Parent Orders',row['Instance'] + ' Daily Parent Orders')
    ##Daily Max Active Parent Orders
    #max active parent order by day. Shows historical trendline and projection
    forecast(ParentOrders['DSTAMP'],ParentOrders['Active'],row['ParentConcurrentCap'],'Active Parent Orders per Second',row['Instance'] + ' Daily Max Active Parent Orders')
    ##Max Parent Order Burst
    #max parent order creation rate by day. Shows historical trendline and projection
    forecast(ParentOrders['DSTAMP'],ParentOrders['Burst'],row['ParentBurstCapacity'],'Parent Orders per Second',row['Instance'] + ' Daily Max Parent Order Creation Rate')


    ##Child Orders
    ##Daily Child Orders
    #aggregated parent order by day. Shows historical trendline and projection
    forecast(ChildOrders['DSTAMP'],ChildOrders['Orders'],row['ChildCapacity'],'Child Orders',row['Instance'] + ' Daily Child Orders')
    ##Daily Max Active Child Orders
    #max active parent order by day. Shows historical trendline and projection
    forecast(ChildOrders['DSTAMP'],ChildOrders['Active'],row['ChildConcurrentCap'],'Active Child Orders per Second',row['Instance'] + ' Daily Max Active Child Orders')
    ##Max Child Order Burst
    #max parent order creation rate by day. Shows historical trendline and projection
    forecast(ChildOrders['DSTAMP'],ChildOrders['Burst'],row['ChildBurstCapacity'],'Child Orders per Second',row['Instance'] + ' Daily Max Child Order Creation Rate')

    #save pdf file
    pp.close()


#close databases
disk_engine.dispose()



