"""
Test for significance of differences
"""
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.proportion import proportions_ztest
from nisicd.reporting import make_crosstab


from nisicd import logging


if __name__ == "__main__":
    all_df = pd.read_parquet("cache/processed.parquet")
    insured_df = all_df[all_df["PAY1"] == "Private insurance"]
    uninsured_df = all_df[all_df["PAY1"] == "Self-pay"]

    logging.info(f"# of admissions in insured group: {len(insured_df)}")
    logging.info(f"# of admissions in uninsured group: {len(uninsured_df)}")

    # Signficance of difference between APDRGs (insured vs uninsured)
    for drg_col in ["APRDRG_Severity", "APRDRG_Risk_Mortality", "cci_score"]:
        stat, pval = ttest_ind(
            insured_df[drg_col].to_numpy(), uninsured_df[drg_col].to_numpy()
        )

        insured_avg = insured_df[drg_col].mean()
        uninsured_avg = uninsured_df[drg_col].mean()
        logging.info(
            f"T-Test {drg_col} (insured vs uninsured): {insured_avg:.2f} vs {uninsured_avg:.2f}, {pval:.5f}"
        )

    for outcome_col in ["SSI", "DIED", "PROLONGED_LOS", "OR_RETURN"]:
        assert insured_df[outcome_col].apply(lambda x: x == 0 or x == 1).all()
        assert uninsured_df[outcome_col].apply(lambda x: x == 0 or x == 1).all()

        # count_insured = insured_df[outcome_col].sum()
        # count_uninsured = uninsured_df[outcome_col].sum()
        # stat, pval = proportions_ztest(
        #     [count_insured, count_uninsured], [len(insured_df), len(uninsured_df)]
        # )

        # logging.info(f"Z-Test {outcome_col} (insured vs uninsured): {stat}, {pval}")
        crosstab = make_crosstab(insured_df, uninsured_df, outcome_col=outcome_col)
        logging.info(
            f"Odds ratio (insured vs uninsured) for {outcome_col}: {crosstab.oddsratio:.2f} (p {crosstab.oddsratio_pvalue():.4f})"
        )
