import pandas as pd
from nisicd.dataProcessing import get_dx_cols, ssi_codes
import statsmodels as sm
from scipy.stats import ttest_ind


def prettyprint_or(ct):
    print(ct.table)
    print(f"OR: {ct.oddsratio:.2f}")
    print(f"95% CI: ({ct.oddsratio_confint()[0]:.2f}, {ct.oddsratio_confint()[1]:.2f})")
    print(f"P-value: {ct.oddsratio_pvalue():.4f}")


if __name__ == "__main__":
    df = pd.read_parquet("cache/processed.parquet")

    # Drop anything that got transferred out
    df = df[df["TRAN_OUT"] == 0]

    # Add column to track SSI
    dx_cols = get_dx_cols(df.columns)
    df["ssi"] = df[dx_cols].isin(ssi_codes).any("columns")

    # Track return to OR
    df["or_return"] = (df["I10_NPR"].fillna(0) + df["NPR"].fillna(0)) > 1

    # Track extended LOS
    df["extended_los"] = df["LOS"] > 4

    # Build composite outcome of in-hospital infection and in-hospital mortality
    # Not including LOS b/c it's definitely affected by insurance status, but for other reasons
    df["composite_outcome"] = (df["ssi"] + df["DIED"] + df["or_return"]) > 0

    # Build composite DM
    df["composite_DM"] = (df["CM_DM"].fillna(0) + df["CMR_DIAB_UNCX"].fillna(0)) > 0

    # Split into insured (private insurance) and uninsured (selfpay) groups
    # Subsequently split into dm / no dm groups
    selfpay = df[df["PAY1"] == 4]
    privatepay = df[df["PAY1"] == 2]

    # Average APRDRG severity for insured + complication vs uninsured vs complication
    # Hypothesis: uninsured vs complication is lower avg APRDRG severity than insured + complication

    print(f"Avg. APRDRG Severity for uninsured: {selfpay['APRDRG_Severity'].mean()}")
    print(f"Avg. APRDRG Sevierty for insured: {privatepay['APRDRG_Severity'].mean()}")

    print()
    print(f"Avg. Age ")

    # for col in ["ssi", "or_return", "extended_los", "composite_outcome"]:
    #     selfpay_complicated = selfpay[selfpay[col] == 1]
    #     privatepay_complicated = privatepay[privatepay[col] == 1]
    #     privatepay_uncomplicated = privatepay[privatepay[col] == 0]

    #     selfpay_complicated = selfpay_complicated.dropna(subset=["APRDRG_Severity"])
    #     privatepay_complicated = privatepay_complicated.dropna(
    #         subset=["APRDRG_Severity"]
    #     )

    #     print(
    #         f"Ages: selfpay {selfpay_complicated['AGE'].mean():.2f}, private {privatepay_complicated['AGE'].mean():.2f}"
    #     )

    #     print(
    #         f"Uninsured + {col} mean APRDRG Severity: {selfpay_complicated['APRDRG_Severity'].mean()}"
    #     )
    #     print(
    #         f"Insured + {col}  mean APRDRG Severity: {privatepay_complicated['APRDRG_Severity'].mean()}"
    #     )

    #     stat, pval = ttest_ind(
    #         selfpay_complicated["APRDRG_Severity"].to_numpy(),
    #         privatepay_complicated["APRDRG_Severity"].to_numpy(),
    #     )
    #     print(stat, pval)
