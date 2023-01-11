"""
Test for significance of differences
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as sm
from scipy.stats import ttest_ind
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.proportion import proportions_ztest

from nisicd import logging
from nisicd.reporting import make_crosstab

if __name__ == "__main__":
    all_df = pd.read_parquet("cache/processed.parquet")

    # Binarize outcome columns so that we can just do logistic regression
    # all_df["APRDRG_Severity"] = (all_df["APRDRG_Severity"] > 2).astype(int)
    # all_df["APRDRG_Risk_Mortality"] = (all_df["APRDRG_Risk_Mortality"] > 2).astype(int)
    # all_df["cci_score"] = (all_df["cci_score"] > 0).astype(int)

    insured_df = all_df[all_df["PAY1"] == "Private insurance"]
    uninsured_df = all_df[(all_df["PAY1"] == "Self-pay")]

    insured_df["InsuranceStatus"] = "insured"
    uninsured_df["InsuranceStatus"] = "uninsured"

    combined_df = pd.concat([insured_df, uninsured_df])

    controllable_vars = [
        "C(RACE)",
        "C(SEX)",
        "C(HOSP_LOCTEACH)",
        "C(HOSP_REGION)",
        "C(INCOME_QRTL)",
        "C(condition)",
        "AGE",
    ]

    logging.info(f"# of admissions in insured group: {len(insured_df)}")
    logging.info(f"# of admissions in uninsured group: {len(uninsured_df)}")

    # Signficance of difference between APDRGs (insured vs uninsured)
    for drg_col in ["APRDRG_Severity", "APRDRG_Risk_Mortality", "cci_score"]:
        stat, pval = ttest_ind(
            insured_df[drg_col].to_numpy(), uninsured_df[drg_col].to_numpy()
        )

        insured_avg = insured_df[drg_col].mean()
        uninsured_avg = uninsured_df[drg_col].mean()
        # logging.info(
        #     f"T-Test {drg_col} (insured vs uninsured): {insured_avg:.2f} vs {uninsured_avg:.2f}, {pval:.5f}"
        # )

        # Age-adjusted
        formula_str = (
            f"{drg_col} ~ C(InsuranceStatus, Treatment(reference='uninsured')) + "
        )

        formula_str += " + ".join(controllable_vars)
        res = OrderedModel.from_formula(formula_str, combined_df, distr="probit").fit(
            method="bfgs", disp=0
        )
        pvals = res.pvalues
        assert "InsuranceStatus" in pvals.index[0]

        logging.info(
            f"{drg_col} adjusted p-values (insured, {insured_avg:.2f} vs uninsured, {uninsured_avg:.2f}): {pvals[0]}"
        )

    ors = list()
    upper_cis = list()
    lower_cis = list()
    ps = list()

    for outcome_col in ["SSI", "DIED", "PROLONGED_LOS", "OR_RETURN"]:
        assert insured_df[outcome_col].apply(lambda x: x == 0 or x == 1).all()
        assert uninsured_df[outcome_col].apply(lambda x: x == 0 or x == 1).all()

        crosstab = make_crosstab(insured_df, uninsured_df, outcome_col=outcome_col)
        # logging.info(
        #     f"Odds ratio (insured vs uninsured) for {outcome_col}: {crosstab.oddsratio:.2f} (p {crosstab.oddsratio_pvalue():.4f})"
        # )

        # Do age-adjusted LR
        formula_str = (
            f"{outcome_col} ~ C(InsuranceStatus, Treatment(reference='uninsured')) + "
        )
        formula_str += " + ".join(controllable_vars)

        lr_df = combined_df
        lr_df[outcome_col] = lr_df[outcome_col].astype(int)
        lr = sm.logit(formula_str, data=lr_df)

        try:
            res = lr.fit(disp=0)
        except np.linalg.LinAlgError as e:
            logging.warning(
                f"LR fit failed ({e}) for {outcome_col}. Attempting regularized fit"
            )
            res = lr.fit_regularized(disp=0)

        odds_ratios = np.exp(res.params)
        lower_ci = np.exp(res.conf_int()[0])
        upper_ci = np.exp(res.conf_int()[1])
        pvals = res.pvalues

        # Double check insurance status OR / pval is @ index 1
        assert "InsuranceStatus" in odds_ratios.index[1]
        assert "InsuranceStatus" in pvals.index[1]

        logging.info(
            f"Adjusted odds ratio for {outcome_col}: {odds_ratios[1]:.2f} [{lower_ci[1]:.2f}, {upper_ci[1]:.2f}], (p {pvals[1]:.5f})"
        )

        ors.append(odds_ratios[1])
        lower_cis.append(lower_ci[1])
        upper_cis.append(upper_ci[1])
        ps.append(pvals[1])

    plottable_df = pd.DataFrame(
        data={
            "Outcomes": [
                "Surgical Site Infection",
                "In-hospital Mortality",
                "Prolonged Length of Stay",
                "Reoperation",
            ],
            "OR": ors,
            "lower_ci": lower_cis,
            "upper_ci": upper_cis,
            "pval": ps,
        }
    )

    sns.set_theme()
    ax = sns.pointplot(
        data=plottable_df,
        x="OR",
        y="Outcomes",
        errorbar=("lower_ci", "upper_ci"),
        capsize=0.4,
        join=False,
        color=".5",
    )

    plt.savefig("results/forestplot.png", bbox_inches="tight")
