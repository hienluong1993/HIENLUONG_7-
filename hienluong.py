import pandas as pd


df = pd.read_csv("enterprise_df_10k_utf8_data.csv")


filtered_df = df[df['담당'] == '7번']

filtered_df.to_csv("담당_7번.csv", index=False)

print("담당_7번.csv")
