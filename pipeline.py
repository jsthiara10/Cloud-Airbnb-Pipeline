import pandas as pd
import regex as re
import argparse
import logging
import os
from datetime import datetime

# Configure the logger

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log")


logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

class AirbnbCleaner:
    def __init__(self, df: pd.DataFrame): # the constructor takes the pandas df as input and makes a copy of it to
        # avoid modifying the original
        self.df = df.copy()

    def clean(self): # these apply all the individual cleaning steps in order
        self.drop_duplicates()
        self.drop_nulls()
        self.clean_host_name()
        self.remove_zero_reviews()
        logging.info("Finished cleaning process")
        return self.df

    def drop_duplicates(self):
        before = self.df.shape[0]
        self.df.drop_duplicates(inplace=True)
        after = self.df.shape[0]
        logging.info(f"Removed duplicates: {before - after} rows dropped.")

    def drop_nulls(self):
        before = self.df.shape[0]
        self.df.dropna(inplace=True)
        after = self.df.shape[0]
        logging.info(f"Removed nulls: {before - after} rows dropped.")

    def clean_host_name(self):
        def clean_name(name):
            if pd.isnull(name):
                return name
            name = str(name).strip()
            name = self._split_camel_case(name)
            name = self._replace_and(name)
            name = name.title()
            return name

        self.df["host_name"] = self.df["host_name"].apply(clean_name)

    def _split_camel_case(self, name: str) -> str: # makes strings consistent e.g. John Smith, instead of 'John smith'
        return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)

    def _replace_and(self, name: str) -> str:
        return re.sub(r"\band\b", "&", name, flags=re.IGNORECASE)

    """Remove listings that have 0 number of reviews"""

    def remove_zero_reviews(self):
        before = self.df.shape[0]
        self.df = self.df[self.df["number_of_reviews"] > 0]
        after = self.df.shape[0]
        logging.info(f"Removed 0-review listings: {before-after} rows dropped. ")

# 🧪 CLI Runner
def run_pipeline(input_path, output_path):
    df = pd.read_csv(input_path)
    cleaner = AirbnbCleaner(df)
    cleaned_df = cleaner.clean()
    cleaned_df.to_csv(output_path, index=False)
    print("✅ Data cleaned and saved to:", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the raw input CSV")
    parser.add_argument("--output", required=True, help="Path to save the cleaned CSV")
    args = parser.parse_args()

    run_pipeline(args.input, args.output)
