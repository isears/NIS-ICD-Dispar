from dataclasses import dataclass

import docx
import numpy as np
import pandas as pd

from nisicd.dataProcessing import categorical_lookup, composite_comorbidities
from nisicd.reporting.docUtil import DocTable

if __name__ == "__main__":
    processed_df = pd.read_parquet("cache/processed.parquet")

    insured_df = processed_df[processed_df["PAY1"] == "Private insurance"]
    uninsured_df = processed_df[processed_df["PAY1"] == "Self-pay"]

    @dataclass
    class T1Column:
        name: str
        type: str

    ordered_t1_columns = [
        T1Column("AGE", "continuous"),
        T1Column("RACE", "categorical"),
    ]

    # make_t1(insured_df, "t1_insured")
    # make_t1(uninsured_df, "t1_uninsured")

    dt = DocTable(["Variable", "All", "Private Insurance Group", "Self-pay Group"])

    for t1_col in ordered_t1_columns:

        if t1_col.type == "continuous":
            all_mean = processed_df[t1_col.name].mean()
            all_std = processed_df[t1_col.name].std()

            insured_mean = insured_df[t1_col.name].mean()
            insured_std = insured_df[t1_col.name].std()

            uninsured_mean = uninsured_df[t1_col.name].mean()
            uninsured_std = uninsured_df[t1_col.name].std()

            dt.add_row(
                [
                    t1_col.name,
                    f"{all_mean:.2f}±{all_std:.2f}",
                    f"{insured_mean:.2f}±{insured_std:.2f}",
                    f"{uninsured_mean:.2f}±{uninsured_std:.2f}",
                ]
            )

        elif t1_col.type == "categorical":
            dt.add_row([t1_col.name])

            all_vcs = processed_df[t1_col.name].value_counts().sort_index().to_dict()
            insured_vcs = insured_df[t1_col.name].value_counts().sort_index().to_dict()
            uninsured_vcs = (
                uninsured_df[t1_col.name].value_counts().sort_index().to_dict()
            )

            for label, all_count in all_vcs.items():
                if label not in insured_vcs:
                    insured_vcs[label] = 0

                if label not in uninsured_vcs:
                    uninsured_vcs[label] = 0

                dt.add_row(
                    [
                        f"  {label}",
                        f"{all_count} ({all_count / len(processed_df):.2f})",
                        f"{insured_vcs[label]} ({insured_vcs[label] / len(insured_df):.2f})",
                        f"{uninsured_vcs[label]} ({uninsured_vcs[label] / len(uninsured_df):.2f})",
                    ]
                )
        else:
            raise ValueError(f"Can't handle this type: {t1_col.type}")

    dt.save("results/table1.docx")
