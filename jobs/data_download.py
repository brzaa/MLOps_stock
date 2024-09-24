import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import yaml

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
    current_date = datetime.now().strftime('%Y%m%d')
    yaml_content = {
        '$schema': 'https://azuremlschemas.azureedge.net/latest/data.schema.json',
        'type': 'uri_file',
        'name': ticker,
        'description': f"Stock data for {ticker} during {tags['Start']}:{tags['End']} in 1d interval.",
        'path': f'data/{ticker}.csv',
        'tags': tags,
        'version': current_date
    }
    
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
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    df.to_csv(f'data/{args.ticker}.csv', index=False)
    
    tags = get_dataset_tags(df)
    save_to_data_upload(df, tags, args.ticker)

    print(f"Data downloaded and saved for {args.ticker}")
    print(f"Dataset tags: {tags}")
    print("data_upload.yml file created successfully")
