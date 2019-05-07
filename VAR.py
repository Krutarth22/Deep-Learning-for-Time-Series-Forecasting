#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR, DynamicVAR
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return dt.date(year,month,day)


data = pd.read_csv('Recent_toBeUsed.csv')
data.drop(['e','YearMonth','Unnamed: 4', 'y', 'y_US','m_in_billion_rupees', 'm_US_in billion rupees','m_in_billion_rupees.1','i', 'i_US','m_US_in billion', 'Dummy', 'Dummy2'],inplace=True,axis=1)
DTTMFormat = '%d-%m-%Y'
data['DTTM'] = pd.to_datetime(data['DTTM'],format=DTTMFormat)
data.set_index('DTTM', inplace = 'True')
data_diff = data.diff().dropna() #differencing


ForecastTime = dt.datetime.strptime('1-7-2006', DTTMFormat)

#Choose lag length
#model.select_order(8) # lag = 1 best
lag = 13

cnt =0
outputPredDF = pd.DataFrame()
se = pd.DataFrame()
while cnt < 110:
    train_period = [ForecastTime - relativedelta(years=10), add_months(ForecastTime,-1)]
    if cnt == 0:
        train = data_diff[add_months(train_period[0],1):train_period[1]]
    else:
        train = data_diff[train_period[0]:train_period[1]]
    test = data[ForecastTime:add_months(ForecastTime+relativedelta(years=1),-1)]
    
    # make a VAR model
    model = VAR(train)
    results = model.fit(lag)

    #results
    #print(results.summary())
    #results.plot() # plot fitted values
    #results.plot_acorr() #Plotting time series autocorrelation function

    #forecast
    n_steps_ahead = 12
    forecasts = results.forecast(np.array(train[-lag:]), n_steps_ahead)[:,0]
    final_pred = np.exp(np.r_[data['ln_e'][train_period[1]], forecasts].cumsum())[1:]
    
    #save predictions and errors 
    columName = str(ForecastTime.year)+'M'+str(ForecastTime.month)
    outputPredDF[columName+'_pred'] = final_pred
    se[columName+'_err'] = np.array((np.exp(test.ln_e) - final_pred)**2)
      
    cnt +=1
    ForecastTime = add_months(ForecastTime,1)
    print(train_period)

rmse = np.sqrt(se.mean(axis = 1)) #T_0 = 110
    
      
    
