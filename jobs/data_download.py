import yfinance as yf
import pandas as pd
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
        'Length': len(df),
        'Start': df['Date'].min().strftime('%Y-%m-%d'),
        'End': df['Date'].max().strftime('%Y-%m-%d'),
        'Median': round(df['Close'].median(), 2),
        'SD': round(df['Close'].std(), 2)
    }

def save_to_data_upload(df, tags, ticker):
    current_date = datetime.now().strftime('%Y%m%d')
    yaml_content = {
        '$schema': 'https://azuremlschemas.azureedge.net/latest/data.schema.json',
        'type': 'uri_file',
        'name': ticker,
        'description': f"Stock data for {ticker} during {tags['Start']}:{tags['End']} in 1d interval.",
        'path': f'../data/{ticker}.csv',
        'tags': tags,
        'version': current_date
    }
    
    with open('data_upload.yml', 'w') as file:
        yaml.dump(yaml_content, file, default_flow_style=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', type=str, default='MASB.JK')
    parser.add_argument('--start', type=str, default='2020-01-01')
    parser.add_argument('--end', type=str, default='2023-12-31')
    args = parser.parse_args()

    df = get_ticker_data(args.ticker, args.start, args.end)
    df.to_csv(f'data/{args.ticker}.csv', index=False)
    
    tags = get_dataset_tags(df)
    save_to_data_upload(df, tags, args.ticker)

    print(f"Data downloaded and saved for {args.ticker}")
    print(f"Dataset tags: {tags}")
