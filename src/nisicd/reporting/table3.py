import pandas as pd

from nisicd.reporting.docUtil import DocTable

if __name__ == "__main__":
    # Table 3
    table3_dt = DocTable(
        [
            "Complication",
            "Adjusted Odds Ratio (Insured vs. Uninsured)",
            "Lower CI",
            "Upper CI",
            "P-Value",
        ]
    )

    for comorbidity_measure in ["DIED", "OR_RETURN", "PROLONGED_LOS", "SSI"]:
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

        table3_dt.add_row(formatted_for_table)

    table3_dt.save("results/table3.docx")
