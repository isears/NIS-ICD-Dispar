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

    total_dm_count = len(ssi[ssi[dx_cols].apply(get_dm, axis=1)])
    private_dm = private_ins[private_ins[dx_cols].apply(get_dm, axis=1)]
    selfpay_dm = selfpay_ins[selfpay_ins[dx_cols].apply(get_dm, axis=1)]

    print(f"Private DM %: {100 * len(private_dm) / len(private_ins):.2f}")
    print(f"Selfpay DM %: {100 * len(selfpay_dm) / len(selfpay_ins):.2f}")

    print(f"Private age avg: {private_ins['AGE'].mean():.2f}")
    print(f"Selfpay age avg: {selfpay_ins['AGE'].mean():.2f}")
