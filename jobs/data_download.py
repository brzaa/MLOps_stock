import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import yaml
import re

def sanitize_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', name)
    if not sanitized[0].isalnum():
        sanitized = 'a' + sanitized
    return sanitized[:255]

def get_ticker_data(ticker, start, end):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end)
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def get_dataset_tags(df):
    return {
        'Length': int(len(df)),
        'Start': df['Date'].min().strftime('%Y-%m-%d'),
        'End': df['Date'].max().strftime('%Y-%m-%d'),
        'Median': float(df['Close'].median()),
        'SD': float(df['Close'].std())
    }

def save_to_data_upload(df, tags, ticker):
    current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    sanitized_ticker = sanitize_name(ticker)
    yaml_content = {
        '$schema': 'https://azuremlschemas.azureedge.net/latest/data.schema.json',
        'type': 'mltable',
        'name': f"{sanitized_ticker}_data",
        'description': f"Stock data for {ticker} during {tags['Start']}:{tags['End']} in 1d interval.",
        'path': f'./data/{sanitized_ticker}.csv',
        'tags': tags,
        'version': current_timestamp
    }

def create_mltable_file(ticker):
    sanitized_ticker = sanitize_name(ticker)
    mltable_content = {
        'type': 'mltable',
        'paths': [
            {
                'file': f'{sanitized_ticker}.csv',
                'delimiter': ','
            }
        ]
    }
    
    with open(f'data/{sanitized_ticker}.mltable', 'w') as file:
        yaml.dump(mltable_content, file, default_flow_style=False)
    
    class FloatDumper(yaml.SafeDumper):
        def represent_float(self, data):
            if np.isnan(data):
                return self.represent_scalar('tag:yaml.org,2002:null', 'null')
            return super().represent_float(data)

    FloatDumper.add_representer(float, FloatDumper.represent_float)
    
    with open('data_upload.yml', 'w') as file:
        yaml.dump(yaml_content, file, default_flow_style=False, Dumper=FloatDumper)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', type=str, default='MASB.JK')
    parser.add_argument('--start', type=str, default='2020-01-01')
    parser.add_argument('--end', type=str, default='2023-12-31')
    args = parser.parse_args()

    df = get_ticker_data(args.ticker, args.start, args.end)
    
    import os
    os.makedirs('data', exist_ok=True)
    
    sanitized_ticker = sanitize_name(args.ticker)
    df.to_csv(f'data/{sanitized_ticker}.csv', index=False)
    
    tags = get_dataset_tags(df)
    save_to_data_upload(df, tags, args.ticker)

    print(f"Data downloaded and saved for {args.ticker}")
    print(f"Dataset tags: {tags}")
    print("data_upload.yml file created successfully")
