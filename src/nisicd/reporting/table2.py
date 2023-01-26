import pandas as pd

from nisicd.reporting.docUtil import DocTable

if __name__ == "__main__":
    # Table 2
    table2_dt = DocTable(
        [
            "Comorbidity Metric",
            "Adjusted Odds Ratio for Metric > 1 (Insured vs. Uninsured)",
            "Lower CI",
            "Upper CI",
            "P-Value",
        ]
    )

    for comorbidity_measure in [
        "APRDRG_Risk_Mortality",
        "APRDRG_Severity",
        "cci_score",
    ]:
        results = pd.read_csv(
            f"results/{comorbidity_measure}_regression.csv", index_col=0
        )

        # Insurance status should be first
        assert results.index[1].startswith("C(InsuranceStatus,")

        formatted_for_table = [comorbidity_measure]

        for cname in ["odds_ratio", "lower_ci", "upper_ci"]:
            formatted_for_table.append(f"{results.iloc[1][cname]:.2f}")

        pval = results.iloc[1]["pval"]

        if pval < 0.001:
            formatted_for_table.append("< 0.001")
        else:
            formatted_for_table.append(f"{pval:.3f}")

        table2_dt.add_row(formatted_for_table)

    table2_dt.save("results/table2.docx")
