import pandas as pd
import json
import glob

csv_files = glob.glob("/home/foysal_munna/Downloads/all_csv/*.csv")

print("Found:", csv_files)

data = []

for file in csv_files:
    df = pd.read_csv(file)
    data.extend(df.to_dict(orient="records"))

with open("clubview_merged.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("clubview_merged.json ready-----------------------------------------")
