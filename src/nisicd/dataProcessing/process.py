"""
Add a boolean column for presence of diabetes based on ICD codes

This is a slow step so best to do once in preprocessing
"""
import pandas as pd
from nisicd.dataProcessing import get_dx_cols, dm_startswith_cods


if __name__ == "__main__":

    df = pd.read_parquet("cache/filtered.parquet")
    dx_cols = get_dx_cols(df.columns)

    def get_dm(row):
        for c in dm_startswith_cods:
            if row.str.startswith(c).any():
                return True

        return False

    df["has_DM"] = df[dx_cols].apply(get_dm, axis=1)

    df.to_parquet("cache/processed.parquet", index=False)
