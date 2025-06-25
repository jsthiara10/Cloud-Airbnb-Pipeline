import pandas as pd
from pipeline import AirbnbCleaner
from pathlib import Path

# Input and Output Paths
input_path = Path("data/raw/AB_NYC_2019.csv")
output_path = Path("data/cleaned/AB_NYC_2019_cleaned.csv")
excel_path = Path("data/cleaned/AB_NYC_2019_cleaned_by_neighbourhood.xlsx")

# Load the raw data

df = pd.read_csv(input_path)

# Run the cleaner

cleaner = AirbnbCleaner(df)
cleaned_df = cleaner.clean()

# Save cleaned CSV
cleaned_df.to_csv(output_path, index=False)

# Save Excel sheets per neighbourhood_group

with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    for group, group_df in cleaned_df.groupby("neighbourhood_group"):
        group_df.to_excel(writer, sheet_name=group, index=False)

print("Data cleaning complete. CSV and Excel generated.")