from fyers_api import fyersModel, accessToken
import webbrowser as wb
import datetime as dt
import os
import pandas as pd
import numpy as np
 
app_id = ""
app_secret = ""
redirect_url = "https://www.google.com/"

symbols = []

start_date = dt.date(2023,6,1)
end_date =  dt.datetime.now().date()

time_zone = 'Asia/Kolkata'

def login():
    if not os.path.exists(f'{dt.date.today().strftime("%b-%d-%Y")}_access_token.txt'):
        session = accessToken.SessionModel(client_id=app_id,
                                           secret_key=app_secret,
                                           redirect_uri=redirect_url,
                                           response_type='code',
                                           grant_type='authorization_code')
        
        response = session.generate_authcode()
        wb.open(response)
        auth_code=input("Enter auth code:")
        session.set_token(auth_code)
        access_token = session.generate_token()['access_token']
        
        with open(f'{dt.date.today().strftime("%b-%d-%Y")}_access_token.txt', 'w') as f:
            f.write(access_token)
        
    else:
        with open(f'{dt.date.today().strftime("%b-%d-%Y")}_access_token.txt', 'r') as f:
            access_token = f.read().strip()
        
    return access_token

access_token = login()
fyers1 = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path=os.getcwd())

sdata = None
df1 = None

def get_data(symbol,res,start,end,date_format=1,cont=0):
    global sdata
    global df1
    data = {'symbol':symbol, 'resolution':res, 'date_format':date_format, 
            'range_from':start, 'range_to':end, 'cont_flag':cont}
    
    sdata = fyers1.history(data=data)
    
    df1 = pd.DataFrame(sdata['candles'])
    df1[0]  = pd.to_datetime(df1[0], unit='s').dt.tz_localize('utc').dt.tz_convert(time_zone)
    df1.columns = ['date','open','high','low','close','volume']
    
    return df1
    

total_days = abs((start_date-end_date).days)

for symbol in symbols:

    df = pd.DataFrame()

    total_days = abs((start_date-end_date).days)
    
    loop = None
    print('fetching',symbol,'data')
    while loop == None:
        start_date = (end_date - dt.timedelta(days=total_days))
        ed = (start_date + dt.timedelta(days = 99 if total_days>100 else total_days)).strftime("%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")
        
        new_data = get_data(f'{symbol}',1,start_date,ed)
        df = pd.concat([df,new_data])
             
        total_days = total_days-100 if total_days>100 else total_days-total_days
        print(symbol,start_date,'to',ed,'data fetched')
        if total_days == 0:
            loop='done'
            print('data fetched')
            
    
    df.to_csv(f"{symbol}.csv")
    print('Data Saved')
