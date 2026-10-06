import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# 1. Extract: Fetch data from API
url = "https://open.er-api.com/v6/latest/USD"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    last_update = data.get("time_last_update_utc")
    base_currency = data.get("base_code")
    rates = data.get("rates", {})
    
    # 2. Transform: Select specific currencies
    target_currencies = ['EGP', 'EUR', 'GBP', 'SAR', 'AED', 'KWD']
    
    extracted_data = []
    for currency in target_currencies:
        if currency in rates:
            extracted_data.append({
                "base_currency": base_currency,
                "target_currency": currency,
                "exchange_rate": rates[currency],
                "api_last_update": last_update,
                "fetched_at": datetime.now()
            })
            
    df = pd.DataFrame(extracted_data)
    
    # 3. Load: Save to SQL Server (SSMS)
    # ملاحظة: إذا كان اسم السيرفر عندك ليس localhost، استبدليه باسم السيرفر الخاص بكِ
    server = '.'  # النقطة تعني الاتصال بالسيرفر المحلي الحالي مباشرة
    database = 'CurrencyDB'
    
    # نص الاتصال باستخدام Windows Authentication
    connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    
    engine = create_engine(connection_string)
    
    # رفع البيانات إلى جدول exchange_rates
    df.to_sql("exchange_rates", engine, if_exists="append", index=False)
    
    print("Data loaded successfully to SQL Server!")
    
else:
    print(f"API Request Failed. Status code: {response.status_code}")
