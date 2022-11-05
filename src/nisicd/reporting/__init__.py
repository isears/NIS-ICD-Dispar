import pandas as pd
import numpy as np
import statsmodels.api as sm

"""
Cross tab format:

            Disease     No Disease
Exposure
No Exposure
"""


def make_crosstab(
    exposure_group: pd.DataFrame,
    control_group: pd.DataFrame,
    outcome_col: str = "outcome",
) -> np.ndarray:
    crosstab = np.zeros((2, 2))
    crosstab[0, 0] = len(exposure_group[exposure_group[outcome_col] == 1])
    crosstab[0, 1] = len(exposure_group[exposure_group[outcome_col] == 0])
    crosstab[1, 0] = len(control_group[control_group[outcome_col] == 1])
    crosstab[1, 1] = len(control_group[control_group[outcome_col] == 0])

    return sm.stats.Table2x2(crosstab)
