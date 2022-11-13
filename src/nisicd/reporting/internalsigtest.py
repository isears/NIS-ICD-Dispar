"""
Test for significance of differences
"""
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.proportion import proportions_ztest
from nisicd.reporting import make_crosstab
import statsmodels.formula.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel


from nisicd import logging


if __name__ == "__main__":
    df = pd.read_parquet("cache/processed.parquet")

    # Binarize outcome columns so that we can just do logistic regression
    df["APRDRG_Severity"] = (df["APRDRG_Severity"] > 2).astype(int)
    df["APRDRG_Risk_Mortality"] = (df["APRDRG_Risk_Mortality"] > 2).astype(int)
    df["cci_score"] = (df["cci_score"] > 1).astype(int)

    payer_subgroups = ["Private insurance", "Self-pay", "Medicare", "Medicaid"]

    controllable_vars = [
        # "C(RACE)",
        # "C(SEX)",
        # "C(HOSP_LOCTEACH)",
        # "C(HOSP_REGION)",
        # "C(INCOME_QRTL)",
        "AGE",
    ]

    # For each group, LR to see if APR-DRGs / CCI correlate with outcomes
    data_out = {
        "payer": list(),
        "predictor_var": list(),
        "dependent_var": list(),
        "OR": list(),
        "lower_ci": list(),
        "upper_ci": list(),
        "pval": list(),
    }

    for payer in payer_subgroups:

        payer_df = df[df["PAY1"] == payer]
        logging.info(f"# of admissions for {payer}: {len(payer_df)}")

        for outcome_col in ["SSI", "DIED", "PROLONGED_LOS", "OR_RETURN"]:

            for risk_metric in [
                "APRDRG_Severity",
                "APRDRG_Risk_Mortality",
                "cci_score",
            ]:
                # Do age-adjusted LR
                formula_str = f"{outcome_col} ~ {risk_metric} + "
                formula_str += " + ".join(controllable_vars)

                lr_df = payer_df
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

                # # Double check insurance status OR / pval is @ index 1
                # assert "InsuranceStatus" in odds_ratios.index[1]
                # assert "InsuranceStatus" in pvals.index[1]

                logging.info(
                    f"{payer}: {risk_metric} -> {outcome_col} OR {odds_ratios[risk_metric]:.2f} ({lower_ci[risk_metric]:.2f} - {upper_ci[risk_metric]:.2f})"
                )

                data_out["payer"].append(payer)
                data_out["predictor_var"].append(risk_metric)
                data_out["dependent_var"].append(outcome_col)
                data_out["OR"].append(odds_ratios[risk_metric])
                data_out["lower_ci"].append(lower_ci[risk_metric])
                data_out["upper_ci"].append(upper_ci[risk_metric])
                data_out["pval"].append(pvals[risk_metric])

    df_out = pd.DataFrame(data=data_out)
    df_out.to_csv("results/internal_dependencies.csv", index=False)
