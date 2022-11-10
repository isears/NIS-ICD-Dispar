"""
Prepare raw (filtered) NIS data for use in models
"""
import pandas as pd
from nisicd import logging
from nisicd.dataProcessing import (
    get_dx_cols,
    categorical_lookup,
    ssi_codes,
    composite_comorbidities,
)
import json
from nisicd.cci import CCI


def get_cci_score(codes):
    score = 0

    # drop empty columns
    codes_revised = [c for c in codes if c is not None]

    for code in codes_revised:
        for cci_category, cci_data in CCI.items():
            match_codes = cci_data["Match Codes"]
            startswith_codes = cci_data["Startswith Codes"]

            if code in match_codes:
                score += cci_data["Points"]

            elif any(code.startswith(swcode) for swcode in startswith_codes):
                score += cci_data["Points"]

    return score


if __name__ == "__main__":
    df_in = pd.read_parquet("cache/filtered.parquet")

    df_out = pd.DataFrame()

    copy_cols = [
        "AGE",
        "APRDRG_Severity",
        "APRDRG_Risk_Mortality",
        "DIED",
        "PAY1",
        "RACE",
        "FEMALE",
        "HOSP_LOCTEACH",
        "HOSP_REGION",
    ]

    # FEMALE, RACE may have NAs
    df_in["FEMALE"] = df_in["FEMALE"].fillna(2)
    df_in["RACE"] = df_in["RACE"].fillna(7)

    for cc in copy_cols:
        df_out[cc] = df_in[cc].astype(int)

    df_out["INCOME_QRTL"] = df_in["ZIPINC_QRTL"].fillna(df_in["ZIPINC"])
    assert not df_out["INCOME_QRTL"].isna().any()
    df_out["INCOME_QRTL"] = df_out["INCOME_QRTL"].astype(int)

    # Prolonged LOS
    df_out["PROLONGED_LOS"] = df_in["LOS"] > 4

    # OR return
    df_out["OR_RETURN"] = (df_in["I10_NPR"].fillna(0) + df_in["NPR"].fillna(0)) > 1

    # SSI
    dx_cols = get_dx_cols(df_in.columns)
    df_out["SSI"] = df_in[dx_cols].isin(ssi_codes).any("columns")

    for key, lookup_table in categorical_lookup.items():
        # FEMALE is 0, 1, but all other columns don't have a 0 val
        if key == "SEX":
            df_out["FEMALE"] = df_out["FEMALE"].apply(lambda x: lookup_table[x])
        else:
            df_out[key] = df_out[key].apply(lambda x: lookup_table[x - 1])

    df_out = df_out.rename(columns={"FEMALE": "SEX"})

    # Get CCI score
    df_out["cci_score"] = df_in[dx_cols].apply(
        lambda row: get_cci_score(row.to_list()), axis=1
    )

    # Build composite comorbidities
    for new_col, (cmr_col, cm_col) in composite_comorbidities.items():
        # If there's not at least 1, we probably got the column name wrong
        assert df_in[cmr_col].fillna(0).sum() > 0
        assert df_in[cm_col].fillna(0).sum() > 0

        df_out[new_col] = df_in[cmr_col].fillna(0) + df_in[cm_col].fillna(0)
        df_out[new_col] = df_out[new_col].astype(int)

    df_out.to_parquet("cache/processed.parquet", index=False)
    df_out.to_csv("cache/processed.csv", index=False)
