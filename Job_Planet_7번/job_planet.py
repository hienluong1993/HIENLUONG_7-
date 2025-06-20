import pandas as pd

# Đọc dữ liệu từ file CSV gốc
df = pd.read_csv("enterprise_df_10k_utf8_data.csv")

# Lọc các dòng có 담당 là '7번'
filtered_df = df[df['담당'] == '7번']

# Xuất ra file CSV mới
filtered_df.to_csv("filtered_by_담당_7번.csv", index=False)

print("Đã xuất file filtered_by_담당_7번.csv thành công.")
