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
        assert results.index[1].startswith("C(InsuranceStatus,")

        results["variable"] = comorbidity_measure
        plottable_df = plottable_df.append(results.iloc[1], ignore_index=True)

    print("Done")

    plt.figure(figsize=(10, 1), dpi=150)
    plt.errorbar(
        x=plottable_df["odds_ratio"].to_numpy(),
        y=plottable_df["variable"].to_numpy(),
        xerr=plottable_df[["lower_ci", "upper_ci"]].transpose().to_numpy(),
        color="black",
        capsize=3,
        linestyle="None",
        linewidth=1,
        marker="o",
        markersize=5,
        mfc="black",
        mec="black",
    )

    plt.savefig("results/fig1.png", bbox_inches="tight")
