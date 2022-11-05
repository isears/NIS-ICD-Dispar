"""
Add a boolean column for presence of diabetes based on ICD codes

This is a slow step so best to do once in preprocessing
"""
import pandas as pd
from nisicd.dataProcessing import get_dx_cols, dm_startswith_cods


if __name__ == "__main__":
    dx_cols = get_dx_cols(pd.read_parquet("cache/ssi.parquet").columns)

    ssi = pd.read_parquet("cache/ssi.parquet", columns=dx_cols + ["PAY1", "AGE"])

    private_ins = ssi[ssi["PAY1"] == 3]
    selfpay_ins = ssi[ssi["PAY1"] == 4]

    def get_dm(row):
        for c in dm_startswith_cods:
            if row.str.startswith(c).any():
                return True

        return False

    ssi["has_DM"] = ssi[dx_cols].apply(get_dm, axis=1)

    ssi.to_parquet("cache/processed.parquet", index=False)
