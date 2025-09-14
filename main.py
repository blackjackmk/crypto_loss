import pandas as pd
import yfinance as yf
import datetime as dt
import requests
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.use('QtAgg')


# Read the CSV file
df = pd.read_csv('./transactions.csv')
op_df = df[['Date', 'Operation']].copy()
op_df.dropna(inplace=True)
op_df['Date'] = pd.to_datetime(op_df['Date'])

start_date = op_df['Date'].min()
end_date = op_df['Date'].max()
limit = (datetime.now().date() - start_date.date()).days

data = yf.download("BTC-USD", start=start_date, end=end_date) #return DataFrame
btc_chart = data['Close']
btc_chart.index = btc_chart.index.strftime('%Y-%m-%d')
btc_df = btc_chart.reset_index()
btc_df.columns = ['Date', 'Price']


fag = requests.get(f"https://api.alternative.me/fng/?limit={limit}&date_format=cn") #limit=0 for all data
response = fag.json() # python dict
data = response["data"] #list
fag_df = pd.DataFrame(data)
fag_df = fag_df.dropna(axis=1)
fag_df.drop('value_classification', axis=1, inplace=True)
fag_df['value'] = fag_df['value'].astype(int)
fag_df = fag_df.sort_values(by='timestamp')


btc_df['Date'] = pd.to_datetime(btc_df['Date'])
op_df['Date'] = pd.to_datetime(op_df['Date'])
fag_df['Date'] = pd.to_datetime(fag_df['timestamp'])
fag_df.drop('timestamp', axis=1, inplace=True)

merged_df = pd.merge(op_df, btc_df, on='Date', how='right')
merged_df = pd.merge(merged_df, fag_df, on='Date', how='left')

transactions_df  = merged_df.dropna(axis = 0)
print(transactions_df)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Primary y-axis for Bitcoin price
ax1.set_xlabel('Date')
ax1.set_ylabel('BTC Price ($)', color='blue')
ax1.plot(merged_df['Date'], merged_df['Price'], label='Price', color='blue')
ax1.scatter(merged_df['Date'][merged_df['Operation'] == "Transaction Buy"],
           merged_df['Price'][merged_df['Operation'] == "Transaction Buy"],
           marker='^', color='green', label='Buy')
ax1.scatter(merged_df['Date'][merged_df['Operation'] == "Transaction Sold"],
           merged_df['Price'][merged_df['Operation'] == "Transaction Sold"],
           marker='v', color='red', label='Sell')
ax1.tick_params(axis='y', labelcolor='blue')

# Secondary y-axis for Fear & Greed index
ax2 = ax1.twinx()
ax2.set_ylabel('Fear & Greed Index', color='orange')
ax2.plot(merged_df['Date'], merged_df['value'], label='Index', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')
ax2.set_ylim(0, 100)  # Fear & Greed Index is 0-100

# Title and legend
plt.title("Bitcoin Price vs Fear & Greed Index")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.show()
