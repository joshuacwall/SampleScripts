import pandas as pd
from sqlalchemy import create_engine
import datetime
from datetime import timedelta 
import cx_Oracle


with open('query.txt', 'r') as myfile:
    query=myfile.read()

day = datetime.datetime.today()-timedelta(days=1)
weekday = day.weekday()

user = 'user'
password = 'password'

db = cx_Oracle.connect(user, password, 'database')
date = day.strftime('%Y-%m-%d')


data = pd.read_sql(query,db) 

with open('results.csv', 'a') as f:
    data.to_csv(f)

db.close()
    




