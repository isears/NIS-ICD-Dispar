import pandas as pd
from nisicd.dataProcessing import get_dx_cols, dm_startswith_cods
from statsmodels.stats.proportion import proportions_ztest


if __name__ == "__main__":
    dx_cols = get_dx_cols(pd.read_parquet("cache/processed.parquet").columns)

    ssi = pd.read_parquet(
        "cache/processed.parquet", columns=dx_cols + ["PAY1", "AGE", "has_DM"]
    )

    private_ins = ssi[ssi["PAY1"] == 3]
    selfpay_ins = ssi[ssi["PAY1"] == 4]

    total_dm_count = ssi["has_DM"].sum()
    private_dm = private_ins[private_ins["has_DM"] == 1]
    selfpay_dm = selfpay_ins[selfpay_ins["has_DM"] == 1]

    print(f"Private DM %: {100 * len(private_dm) / len(private_ins):.2f}")
    print(f"Selfpay DM %: {100 * len(selfpay_dm) / len(selfpay_ins):.2f}")

    print(f"Private age avg: {private_ins['AGE'].mean():.2f}")
    print(f"Selfpay age avg: {selfpay_ins['AGE'].mean():.2f}")

    # Get significance
    count_dm_private = len(private_dm)
    count_dm_selfpay = len(selfpay_dm)
    nobs_private = len(private_ins)
    nobs_selfpay = len(selfpay_ins)

    stat, pval = proportions_ztest(
        [count_dm_private, count_dm_selfpay], [nobs_private, nobs_selfpay]
    )
    print(f"Stat: {stat}")
    print(f"P value: {pval}")
