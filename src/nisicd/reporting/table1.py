import string
from dataclasses import dataclass

import docx
import numpy as np
import pandas as pd

from nisicd.dataProcessing import categorical_lookup, composite_comorbidities
from nisicd.reporting.docUtil import DocTable

if __name__ == "__main__":
    processed_df = pd.read_parquet("cache/processed.parquet")

    # Some initial cleaning
    processed_df["condition"] = processed_df["condition"].apply(
        lambda x: string.capwords(x.replace("_", " "))
    )

    insured_df = processed_df[processed_df["PAY1"] == "Private insurance"]
    uninsured_df = processed_df[processed_df["PAY1"] == "Self-pay"]

    @dataclass
    class T1Column:
        df_col: str
        name: str
        type: str

    ordered_t1_columns = [
        T1Column("AGE", "Age -- yr.", "continuous"),
        T1Column("RACE", "Race", "categorical"),
        T1Column("SEX", "Sex", "categorical"),
        T1Column("INCOME_QRTL", "Income Quartile", "categorical"),
        T1Column("HOSP_LOCTEACH", "Hospital Status", "categorical"),
        T1Column("HOSP_REGION", "Hospital Region", "categorical"),
        T1Column("condition", "Presenting Condition", "categorical"),
        T1Column("APRDRG_Severity", "APRDRG Severity", "categorical"),
        T1Column("APRDRG_Risk_Mortality", "APRDRG Risk Mortality", "categorical"),
        T1Column("cci_score", "CCI Score", "continuous"),
        T1Column("DIED", "In-hospital Mortality", "binary"),
        T1Column("OR_RETURN", "Reoperation", "binary"),
        T1Column("PROLONGED_LOS", "Prolonged LOS", "binary"),
        T1Column("SSI", "In-hospital Surgical Site Infection", "binary"),
    ]

    dt = DocTable(
        [
            "Characteristic",
            f"All (n={len(processed_df)})",
            f"Private Insurance Group (n={len(insured_df)})",
            f"Self-pay Group (n={len(uninsured_df)})",
        ]
    )

    for t1_col in ordered_t1_columns:

        if t1_col.type == "continuous":
            all_mean = processed_df[t1_col.df_col].mean()
            all_std = processed_df[t1_col.df_col].std()

            insured_mean = insured_df[t1_col.df_col].mean()
            insured_std = insured_df[t1_col.df_col].std()

            uninsured_mean = uninsured_df[t1_col.df_col].mean()
            uninsured_std = uninsured_df[t1_col.df_col].std()

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

            all_vcs = processed_df[t1_col.df_col].value_counts().sort_index().to_dict()
            insured_vcs = (
                insured_df[t1_col.df_col].value_counts().sort_index().to_dict()
            )
            uninsured_vcs = (
                uninsured_df[t1_col.df_col].value_counts().sort_index().to_dict()
            )

            for label, all_count in all_vcs.items():
                if label not in insured_vcs:
                    insured_vcs[label] = 0

                if label not in uninsured_vcs:
                    uninsured_vcs[label] = 0

                dt.add_row(
                    [
                        f"  {label}",
                        f"{all_count} ({100* all_count / len(processed_df):.2f})",
                        f"{insured_vcs[label]} ({100* insured_vcs[label] / len(insured_df):.2f})",
                        f"{uninsured_vcs[label]} ({100*uninsured_vcs[label] / len(uninsured_df):.2f})",
                    ]
                )
        elif t1_col.type == "binary":
            for df in [processed_df, insured_df, uninsured_df]:
                assert df[t1_col.df_col].apply(lambda x: x == 1 or x == 0).all()

            all_count = processed_df[t1_col.df_col].sum()
            insured_count = insured_df[t1_col.df_col].sum()
            uninsured_count = uninsured_df[t1_col.df_col].sum()

            dt.add_row(
                [
                    t1_col.name,
                    f"{all_count} ({100 * all_count / len(processed_df):.2f})",
                    f"{insured_count} ({100 * insured_count / len(insured_df):.2f})",
                    f"{uninsured_count} ({100 * uninsured_count / len(uninsured_df):.2f})",
                ]
            )
        else:
            raise ValueError(f"Can't handle this type: {t1_col.type}")

    dt.save("results/table1.docx")
