from os import truncate
import pandas as pd
import datetime as dt

sep_16 = pd.read_csv('./weekly_data/final_data_weekly_0916.csv')
q4_16 = pd.read_csv('./weekly_data/final_data_weekly_1016_1216.csv')
h1_17 = pd.read_csv('./weekly_data/final_data_weekly_0117_0617.csv')
h2_17 = pd.read_csv('./weekly_data/final_data_weekly_0717_1217.csv')
h1_18 = pd.read_csv('./weekly_data/final_data_weekly_0118_0618.csv')
h2_18 = pd.read_csv('./weekly_data/final_data_weekly_0718_1218.csv')
h1_19 = pd.read_csv('./weekly_data/final_data_weekly_0119_0619.csv')
h2_19 = pd.read_csv('./weekly_data/final_data_weekly_0719_1219.csv')
h1_20 = pd.read_csv('./weekly_data/final_data_weekly_0120_0620.csv')
h2_20 = pd.read_csv('./weekly_data/final_data_weekly_0720_1220.csv')
h1_21 = pd.read_csv('./weekly_data/final_data_weekly_0121_0921.csv')

final_data = pd.concat([sep_16, q4_16, h1_17, h2_17, h1_18, h2_18, h1_19, h2_19, h1_20, h2_20, h1_21]).reset_index(drop=True)
final_data['date'] = final_data['date'].apply(lambda x: dt.datetime.strptime(x, '%d/%m/%Y'))

final_data = final_data.sort_values(by='date').reset_index(drop=True)
print(final_data)
final_data.to_csv('final_data.csv', index=False)