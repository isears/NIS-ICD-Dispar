import pandas as pd
from nisicd.dataProcessing import get_dx_cols, ssi_codes
from nisicd.reporting import make_crosstab
from scipy.stats import fisher_exact
import statsmodels as sm


def prettyprint_or(ct):
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

    # Build composite outcome of in-hospital infection and in-hospital mortality
    # df["composite_outcome"] = df.apply(
    #     lambda row: row["ssi"] == 1 or row["DIED"] == 1, axis=1
    # )
    # assert df["composite_outcome"].sum() > df["DIED"].sum()
    # assert df["composite_outcome"].sum() > df["ssi"].sum()
    # assert df["composite_outcome"].sum() < (df["ssi"].sum() + df["DIED"].sum())

    # Split into insured (private insurance) and uninsured (selfpay) groups
    # Subsequently split into dm / no dm groups
    selfpay = df[df["PAY1"] == 4]
    privatepay = df[df["PAY1"] == 3]

    selfpay_dm = selfpay[selfpay["has_DM"] == 1]
    selfpay_nodm = selfpay[selfpay["has_DM"] == 0]

    privatepay_dm = privatepay[privatepay["has_DM"] == 1]
    privatepay_nodm = privatepay[privatepay["has_DM"] == 0]

    # Odds of ssi / ihm in no diabetes group if no insurance (hypothesis: > 1)
    print(
        "Odds of outcome (in hospital ssi / mortality) given uninsured (no dm gorup):"
    )
    crosstab = make_crosstab(selfpay_nodm, privatepay_nodm, outcome_col="ssi")
    prettyprint_or(crosstab)

    # Odds of ssi / ihm in diabetes group if no insurance (hypothesis: insignificant)
    print("Odds of outcome (in hospital ssi / mortality) given uninsured (dm group):")
    crosstab = make_crosstab(selfpay_dm, privatepay_dm, outcome_col="ssi")
    prettyprint_or(crosstab)

    # Odds of ssi / ihm in everyone if no insurance
    print("Odds of outcome given no insurance (everyone)")
    crosstab = make_crosstab(selfpay, privatepay, outcome_col="ssi")
    prettyprint_or(crosstab)
