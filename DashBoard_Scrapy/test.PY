import pandas as pd

dt = pd.read_csv('unlimited_results.csv') 
df = pd.read_csv('concatenated_FFA.csv')
df['competition_date'] = pd.to_datetime(df['competition_date'], errors='coerce').dt.strftime('%d/%m') + '/24'
merged_df = pd.concat([dt, df], axis=0, ignore_index=True)
merged_df = merged_df.drop_duplicates(subset='competition_name', keep='first')
merged_df = merged_df.drop(columns=['club','athlete','time','rank','Minute_Time','vitesse','results_url','competition_date','category','distance'])
merged_df.to_csv('resultat_course.csv', index=False)