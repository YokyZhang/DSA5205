import time
import datetime as dt
import pandas as pd
import numpy as np
import functools
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from textblob import TextBlob

def get_days_in_month(month):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 30
    elif month == 2:
        return 27
    else:
        return 29

# Start Service
def get_driver():
    service = Service('../../chromedriver_win32/chromedriver')
    service.start()
    driver = webdriver.Remote(service.service_url)
    return driver

def perform_scrape(driver, start_date_str, end_date_str):
    # Find Tool Button
    date_options = driver.find_element(By.XPATH, '//*[@id="hdtbMenus"]/span[2]/g-popup/div[1]')
    ActionChains(driver).click(date_options).perform()

    # Click on Custom Date Range
    cdr = driver.find_element(By.XPATH, '//*[@id="lb"]/div/g-menu/g-menu-item[8]')
    ActionChains(driver).click(cdr).perform()

    # Custom From, To dates and submit
    from_date = driver.find_element(By.XPATH, '//*[@id="OouJcb"]')
    from_date.send_keys(start_date_str)
    to_date = driver.find_element(By.XPATH, '//*[@id="rzG2be"]')
    to_date.send_keys(end_date_str)
    submit_date = driver.find_element(By.XPATH, '//*[@id="T3kYXe"]/g-button')
    ActionChains(driver).click(submit_date).perform()

    # Get titles of articles
    titles = []
    n = 2 # Get a total of n pages of results
    for i in range(n):
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            search = soup.find_all('div', class_="mCBkyc JQe2Ld nDgy9d")
            for h in search:
                title = h.text
                titles.append(title)
            # Click next
            try:
                next_page = driver.find_element(By.ID, 'pnnext')
                ActionChains(driver).click(next_page).perform()
            except Exception as e:
                if i < 1:
                    print('Only 1 page of results. Skipping sentiment calculation.')
                    titles = 'NONE'
                return titles
        except Exception as e:
            print(e)
            continue
    return titles

def get_sentiment(row):
    blob_list = []
    for title in row['titles']:
        blob = TextBlob(title)
        blob_list.append(blob.sentiment.polarity)
        # print(blob.sentiment, blob.sentiment.polarity, title)
    avg_polarity = functools.reduce(lambda a, b: a + b, blob_list)
    row['sentiment'] = avg_polarity
    return row


# Main function
tickers = ['AAPL', 'MRNA', 'AAL', 'TSLA', 'MU', 'SBUX', 'TMUS', 'FITB', 'PEP', 'BABA']
df = pd.DataFrame(columns=['ticker', 'date', 'titles', 'sentiment'])
# final_df = pd.DataFrame(columns=['date', 'AAPL', 'MRNA', 'AAL', 'TSLA', 'MU', 'SBUX', 'TMUS', 'FITB', 'PEP', 'BABA'])
date_str = '09/24/2016'
date = dt.datetime.strptime(date_str, '%m/%d/%Y')
# end_date_str = '09/30/2021'
end_date_str = '09/30/2016'
end_date = dt.datetime.strptime(end_date_str, '%m/%d/%Y')

while date <= end_date:
    # Define start date, end date, interval
    for ticker in tickers:
        query = ticker + ' stock'
        print(query)
        date_str = dt.datetime.strftime(date, '%m/%d/%Y')
        end_week = date + dt.timedelta(days=6)
        end_week_str = dt.datetime.strftime(end_week, '%m/%d/%Y')
        day = int(date_str.split('/')[1])
        month = int(date_str.split('/')[0])
        year = int(date_str.split('/')[2])
        days_in_month = get_days_in_month(month)
        service = Service('../../chromedriver_win32/chromedriver')
        service.start()
        driver = webdriver.Remote(service.service_url)
        driver.get(f'https://www.google.com/search?q={query}&tbm=nws&lr=lang_en&hl=en&sort=date&num=5')
        time.sleep(2)
        titles = perform_scrape(driver, date_str, end_week_str)
        row = {'ticker': ticker, 'date': str(day)+'/'+str(month)+'/'+str(year), 'titles': titles, 'sentiment': np.NaN}
        if titles != 'NONE':
            row = get_sentiment(row)
        df = df.append(row, ignore_index=True)
        print(df)
        driver.quit()
    date = date + dt.timedelta(days=7)

df.to_csv('weekly_data/data_weekly_0916.csv')

final_data = pd.pivot_table(df, values='sentiment', index='date', columns='ticker', dropna=False)
final_data.to_csv('weekly_data/final_data_weekly_0916.csv')
