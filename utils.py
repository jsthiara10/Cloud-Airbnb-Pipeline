import pandas as pd
import json
import os


# Schema validation - checks to see if the final table in BQ matches the schema in our final CSV

def load_schema(schema_path):
    with open(schema_path, "r") as f:
        schema = json.load(f)
    return schema["columns"]


def validate_columns(df, expected_columns):
    actual_columns = list(df.columns)
    if actual_columns != expected_columns:
        raise ValueError(
            f"Column mismatch detected!\n"
            f"Expected columns ({len(expected_columns)}): {expected_columns}\n"
            f"Actual columns ({len(actual_columns)}): {actual_columns}"
        )
    else:
        print("✅ Column validation passed.")


def remove_index_like_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols_to_drop = []

    for col in df.columns:
        col_clean = col.strip().lower()

        # Remove index columns

        if col_clean in {'index', 'row', 'unnamed: 0'}:
            cols_to_drop.append(col)
            continue

        # Column is integer-like and looks like an auto-generated index

        if pd.api.types.is_integer_dtype(df[col]) and df[col].is_monotonic_increasing:
            if df[col].equals(pd.Series(range(df.shape[0]))) or \
                    df[col].equals(pd.Series(range(1, df.shape[0] + 1))):
                cols_to_drop.append(col)

    return df.drop(columns=cols_to_drop)
