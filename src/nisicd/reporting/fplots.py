import forestplot as fp
import matplotlib.pyplot as plt
import pandas as pd

from nisicd.reporting.docUtil import DocTable

if __name__ == "__main__":
    dt = DocTable(["Characteristic", "Adjusted Odds Ratio (Insured vs. Uninsured)"])
    plottable_df = pd.DataFrame()
    # First figure
    for comorbidity_measure in [
        "APRDRG_Risk_Mortality",
        "APRDRG_Severity",
        "cci_score",
    ]:
        results = pd.read_csv(
            f"results/{comorbidity_measure}_regression.csv", index_col=0
        )

        # Insurance status should be first
        assert results.index[0].startswith("C(InsuranceStatus,")

        results["variable"] = comorbidity_measure
        plottable_df = plottable_df.append(results.iloc[0], ignore_index=True)

    print("Done")

    fp.forestplot(
        plottable_df,
        estimate="odds_ratio",
        varlabel="variable",
        ll="lower_ci",
        hl="upper_ci",
        pval="pval",
        sort=True,
        color_alt_rows=True,
    )

    plt.savefig("results/fig1.png", bbox_inches="tight")
