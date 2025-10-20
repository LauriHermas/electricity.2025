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
interval_choice = st.selectbox('Select a period', ['Daily', 'Weekly', 'Monthly'], index=2)
freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}
freq = freq_map[interval_choice]

# group by using the selected frequency
df_filtered = df.groupby(pd.Grouper(key='datetime', freq=freq)).agg(
    avg_price=('Price', 'mean'),
    avg_temp=('Temperature', 'mean'),
    total_consumption=('kWh', 'sum'),
    total_bill=('bill', 'sum')
).reset_index()

# convert bill to euros
df_filtered['total_bill'] = df_filtered['total_bill'] / 100

# draw the line charts using aggregated column names
st.line_chart(df_filtered.set_index('datetime')[['avg_price']], width=700, height=300)
st.line_chart(df_filtered.set_index('datetime')[['avg_temp']], width=700, height=300)
st.line_chart(df_filtered.set_index('datetime')[['total_bill']], width=700, height=300)
st.line_chart(df_filtered.set_index('datetime')[['total_consumption']], width=700, height=300)


