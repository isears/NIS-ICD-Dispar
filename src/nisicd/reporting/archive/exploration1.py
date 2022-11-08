import pandas as pd
from nisicd.dataProcessing import get_dx_cols, ssi_codes
from nisicd.reporting import make_crosstab
from scipy.stats import fisher_exact
import statsmodels as sm


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
    # assert df["composite_outcome"].sum() > df["DIED"].sum()
    # assert df["composite_outcome"].sum() > df["ssi"].sum()
    # assert df["composite_outcome"].sum() < (df["ssi"].sum() + df["DIED"].sum())

    # Build composite DM
    df["composite_DM"] = (df["CM_DM"].fillna(0) + df["CMR_DIAB_UNCX"].fillna(0)) > 0
    df["composite_DMCX"] = (df["CM_DMCX"].fillna(0) + df["CMR_DIAB_CX"].fillna(0)) > 0
    df["composite_VASC"] = (
        df["CM_PERIVASC"].fillna(0) + df["CMR_PERIVASC"].fillna(0)
    ) > 0
    df["composite_ALCOHOL"] = (
        df["CM_ALCOHOL"].fillna(0) + df["CMR_ALCOHOL"].fillna(0)
    ) > 0
    df["composite_DRUG"] = (
        df["CM_DRUG"].fillna(0) + df["CMR_DRUG_ABUSE"].fillna(0)
    ) > 0

    # Split into insured (private insurance) and uninsured (selfpay) groups
    # Subsequently split into dm / no dm groups
    selfpay = df[df["PAY1"] == 4]
    privatepay = df[df["PAY1"] == 2]

    comorbidity_col = "composite_DMCX"
    selfpay_dm = selfpay[selfpay[comorbidity_col] == 1]
    selfpay_nodm = selfpay[selfpay[comorbidity_col] == 0]

    privatepay_dm = privatepay[privatepay[comorbidity_col] == 1]
    privatepay_nodm = privatepay[privatepay[comorbidity_col] == 0]

    # Odds of ssi / ihm in no diabetes group if no insurance (hypothesis: > 1)
    print(
        "Odds of outcome (in hospital ssi / mortality) given uninsured (no dm gorup):"
    )
    crosstab = make_crosstab(
        selfpay_nodm, privatepay_nodm, outcome_col="composite_outcome"
    )
    prettyprint_or(crosstab)

    # Odds of ssi / ihm in diabetes group if no insurance (hypothesis: insignificant)
    print("Odds of outcome (in hospital ssi / mortality) given uninsured (dm group):")
    crosstab = make_crosstab(selfpay_dm, privatepay_dm, outcome_col="composite_outcome")
    prettyprint_or(crosstab)

    # Odds of ssi / ihm in everyone if no insurance
    print("Odds of outcome given no insurance (everyone)")
    crosstab = make_crosstab(selfpay, privatepay, outcome_col="composite_outcome")
    prettyprint_or(crosstab)

    # Average APRDRG severity for insured + complication vs uninsured vs complication
    # Hypothesis: uninsured vs complication is lower avg APRDRG severity than insured + complication

    for col in ["ssi", "or_return", "extended_los", "composite_outcome"]:
        selfpay_complicated = selfpay[selfpay[col] == 1]
        privatepay_complicated = privatepay[privatepay[col] == 1]

        print(
            f"Uninsured + {col} mean APRDRG Severity: {selfpay_complicated['APRDRG_Severity'].mean()}"
        )
        print(
            f"Insured + {col}  mean APRDRG Severity: {privatepay_complicated['APRDRG_Severity'].mean()}"
        )
