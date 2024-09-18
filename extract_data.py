import pandas as pd
import re

# CSVファイルを読み込む
def process_csv(csv_file):
    # CSVデータを読み込む
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.strip()
    print(df.head())
    
    # 速度の単位を除去し、数値に変換
    df['speed'] = df['speed[km/h]'].str.replace(' kilometer_per_hour', '').astype(float)
    
    # 回転数の単位を除去し、数値に変換
    df['RPM'] = df['rpm'].str.replace(' revolutions_per_minute', '').astype(float)
    
    #SPEED, RPM, TIMEから構成されるDFを作成
    df = df['time', 'RPM', 'speed']
    
    return df

# CSVファイルを処理
csv_file = './can_log/20240911000954.csv'
result_df = process_csv(csv_file)

# 結果を表示
#import ace_tools as tools; tools.display_dataframe_to_user(name="Extracted Data", dataframe=result_df)

# 必要に応じてCSVに書き出す
result_df.to_csv('can_log/extracted_data.csv', index=False)