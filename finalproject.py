import pandas as pd
import streamlit as st
#import csv files
dfA = pd.read_csv("https://raw.githubusercontent.com/LauriHermas/electricity.2025/refs/heads/main/Electricity_consumption_2015-2025.csv")
dfB = pd.read_csv("https://raw.githubusercontent.com/LauriHermas/electricity.2025/refs/heads/main/Electricity_price_2015-2025.csv",delimiter = ';',decimal=',')

#convert time to pandas dateatime
dfA['datetime'] = pd.to_datetime(dfA['time'],format = '%Y-%m-%d %H:%M:%S')
dfB['datetime'] = pd.to_datetime(dfB['timestamp'],format = '%H:%M %m/%d/%Y')

#merge the two dataframes by datetime
df = pd.merge(dfA,dfB, on = 'datetime', how = 'outer')

#drop undeed time and timestamp columns
df = df[['datetime','Price','kWh','Temperature']]

#calcute the hourly bill paid for electricity
df['bill']=df['Price']*df['kWh']

#calculate total bill and total consumption togeter with average price and average temperature
#for later use in the visualization part. The intervals ashould be daily, weekly and monthly

#start by defining the interval variable

Interval = 'D' or 'W' or 'M'  #D=Daily W=Weekly M=Monthly

#visualization part
st.title('Energy Consumption and price')

#Selector for start date
start_date = st.date_input("Select a start date", value=df['datetime'].min().date())
date_after_start = df['datetime'] >= pd.to_datetime(start_date)
#Selector for end date
end_date = st.date_input("Select an end date", value=df['datetime'].max().date())
date_before_end = df['datetime'] <= pd.to_datetime(end_date)

#filter the data frame according to the selected dates
df =  df[date_after_start & date_before_end]

st.write("Showing range: ", start_date, " - ", end_date)
st.write("Total consumption over the period: ", df['kWh'].sum().round(1), "kWh")
st.write("Total bill over the period: ", (df['bill'].sum()/100).round(1), "€")
st.write("Average hourly price: ", df['Price'].mean().round(2), "cents")
st.write("Average paid price: ", (df['bill'].sum()/df['kWh'].sum()).round(2), "cents")

#selector for interval
interval_group = st.multiselect(label='Select a period',options=['Daily','Weekly','Monthly'],default='Monthly',max_selections=1)
interval = ''
if(len(interval_group)>=1):
    if(interval_group[0]=='Daily'):
        interval = 'D'
    elif(interval_group[0]=='Weekly'):
        interval = 'W'
    elif(interval_group[0]=='Monthly'):
        interval = 'M'

df_avgP=df.groupby(pd.Grouper(key = 'datetime', freq = Interval))[['Price']].mean().reset_index()
df_avgT=df.groupby(pd.Grouper(key = 'datetime', freq = Interval))[['Temperature']].mean().reset_index()
df_totalC=df.groupby(pd.Grouper(key = 'datetime', freq = Interval))[['kWh']].sum().reset_index()
df_totalB=df.groupby(pd.Grouper(key = 'datetime', freq = Interval))[['bill']].sum().reset_index()

#convert bill to euros
df_totalB['bill'] = df_totalB['bill']/100

#draw the line charts
st.line_chart(df_avgP, x = 'datetime', y = 'Price', x_label ='Time', y_label='Average Price €,cents')
st.line_chart(df_avgT, x = 'datetime', y = 'Temperature', x_label ='Time', y_label='Average Temperature °C')
st.line_chart(df_totalB, x = 'datetime', y = 'bill', x_label ='Time', y_label='Total Bill €')
st.line_chart(df_totalC, x = 'datetime', y = 'kWh', x_label ='Time', y_label='Total Consumption kWh')


