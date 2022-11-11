"""
Apply study inclusion criteria:
- Age > 18
- Diagnosis codes of interest
- Procedure codes of interest
"""
import pandas as pd
from nisicd import logging
from nisicd.dataProcessing import get_dx_cols


class InclusionCriteria:
    def __init__(self, base_df) -> None:
        self.base_df = base_df
        logging.info(
            f"Inclusion criteria filter instantiated with n={len(self.base_df)}"
        )

    @staticmethod
    def _ic_dropna(df_in: pd.DataFrame) -> pd.DataFrame:
        # We can handle FEMALE and RACE missing, but need other columns
        cols = [
            "AGE",
            "PAY1",
            "APRDRG_Severity",
            "APRDRG_Risk_Mortality",
            "HOSP_LOCTEACH",
            # "HOSP_DIVISION",
            "HOSP_REGION",
            "DIED",
            "LOS",
        ]

        df_in = df_in.dropna(subset=cols, how="any")

        # Can have either ZIPINC OR ZIPINC_QRTL
        df_in = df_in.dropna(subset=["ZIPINC", "ZIPINC_QRTL"], how="all")

        return df_in

    @staticmethod
    def _ic_age(df_in: pd.DataFrame) -> pd.DataFrame:
        # df_in = df_in[df_in["AGE"] < 65]
        # df_in = df_in[df_in["AGE"] > 18]
        return df_in

    @staticmethod
    def _ic_tranout(df_in: pd.DataFrame) -> pd.DataFrame:
        return df_in[df_in["TRAN_OUT"] == 0]

    def apply_ic(self) -> pd.DataFrame:
        ic_methods = [m for m in dir(self) if m.startswith("_ic")]
        df = self.base_df

        for method_name in ic_methods:
            before_count = len(df)
            func = getattr(self, method_name)
            df = func(df)
            after_count = len(df)
            logging.info(
                f"{method_name} diff: {before_count - after_count} ({before_count} -> {after_count})"
            )

        logging.info(f"Success, final size: {len(df)}")
        return df


if __name__ == "__main__":
    # Have to cut down on number of cols or run out of mem
    all_cols = pd.read_parquet("cache/appendicitis.parquet").columns
    dx_cols = get_dx_cols(all_cols)
    cm_cols = [c for c in all_cols if c.startswith("CM_")]
    cm_cols += [c for c in all_cols if c.startswith("CMR_")]

    used_cols = (
        [
            "AGE",
            "FEMALE",
            "RACE",
            "PAY1",
            "APRDRG_Severity",
            "APRDRG_Risk_Mortality",
            "HOSP_LOCTEACH",
            # "HOSP_DIVISION",
            "HOSP_REGION",
            "DIED",
            "LOS",
            "ZIPINC",
            "ZIPINC_QRTL",
            "TRAN_OUT",
            "I10_NPR",
            "NPR",
        ]
        + dx_cols
        + cm_cols
    )
    df = pd.read_parquet("cache/appendicitis.parquet", columns=used_cols)
    ic = InclusionCriteria(df)
    filtered = ic.apply_ic()
    filtered.to_parquet("cache/filtered.parquet")
