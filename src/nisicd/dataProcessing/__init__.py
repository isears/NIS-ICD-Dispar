import re

ssi_codes = ["99859", "T8149XA", "T8141XA"]

dm_startswith_cods = ["6480", "249", "250", "E08", "E09", "E10", "E11", "E13"]

appendicitis_codes = [
    "5409",
    "5400",
    "5401",
    "K3580",
    "K358",
    "K35890",
    "K35891",
    "K352",
    "K3520",
    "K3521",
    "K353",
    "K3530",
    "K3531",
    "K3532",
    "K3533",
]
DX_CODES = {
    "acute_appendicitis": [
        "5409",
        "5400",
        "5401",
        "K3580",
        "K358",
        "K35890",
        "K35891",
        "K352",
        "K3520",
        "K3521",
        "K353",
        "K3530",
        "K3531",
        "K3532",
        "K3533",
    ],
    "acute_cholecystitis": ["5750", "K810"],
    # "perforated_diverticulitis": [
    #     "56213",
    #     "56203",
    #     "K5700",
    #     "K5701",
    #     "K570",
    #     "K573",
    #     "K5730",
    #     "K5731",
    #     "K5732",
    #     "K5733",
    # ],
    # "nonperforated_diverticulitis": ["56211"]
    # "acute_perforated_duodenal_ulcer": ["5321"],  # Acute perforated duodenal ulcer
    # "postoperative_infection": ["9985", "99851", "99859"]
}


def get_proc_cols(all_cols):
    icd9_proc_cols = [col for col in all_cols if re.search("^PR[0-9]{1,2}$", col)]
    icd10_proc_cols = [col for col in all_cols if re.search("^I10_PR[0-9]{1,2}$", col)]

    return icd9_proc_cols + icd10_proc_cols


def get_dx_cols(all_cols):
    icd9_cols = [col for col in all_cols if re.search("^DX[0-9]{1,2}$", col)]
    icd10_cols = [col for col in all_cols if re.search("^I10_DX[0-9]{1,2}$", col)]

    return icd9_cols + icd10_cols


categorical_lookup = {
    "SEX": ["Male", "Female", "Unknown"],
    "RACE": [
        "White",
        "Black",
        "Hispanic",
        "Asian or Pacific Islander",
        "Native American",
        "Other",
        "Unknown",
    ],
    "PAY1": [
        "Medicare",
        "Medicaid",
        "Private insurance",
        "Self-pay",
        "No charge",
        "Other",
    ],
    "HOSP_LOCTEACH": ["Rural", "Urban nonteaching", "Urban teaching"],
    # "HOSP_DIVISION": [
    #     "New England",
    #     "Middle Atlantic",
    #     "East North Central",
    #     "West North Central",
    #     "South Atlantic",
    #     "East South Central",
    #     "West South Central",
    #     "Mountain",
    #     "Pacific",
    # ],
    "HOSP_REGION": ["Northeast", "Midwest", "South", "West"],
}

composite_comorbidities = {
    "AIDS": ("CMR_AIDS", "CM_AIDS"),
    "ALCOHOL": ("CMR_ALCOHOL", "CM_ALCOHOL"),
    "ARTHRITIS": ("CMR_ARTH", "CM_ARTH"),
    "CANCER, LYMPHOMA": ("CMR_CANCER_LYMPH", "CM_LYMPH"),
    "CANCER, METASTATIC": ("CMR_CANCER_METS", "CM_METS"),
    "CANCER, SOLID": ("CMR_CANCER_SOLID", "CM_TUMOR"),
    "DEPRESSION": ("CMR_DEPRESS", "CM_DEPRESS"),
    "DIABETES, UNCOMPLICATED": ("CMR_DIAB_UNCX", "CM_DM"),
    "DIABETES, COMPLICATED": ("CMR_DIAB_CX", "CM_DMCX"),
    # Hack to combine columns, will have to handled in processor
    "HYPERTENSION 1": ("CMR_HTN_UNCX", "CM_HTN_C"),
    "HYPERTENSION 2": ("CMR_HTN_CX", "CM_HTN_C"),
    "CHRONIC LUNG": ("CMR_LUNG_CHRONIC", "CM_CHRNLUNG"),
    "OBESITY": ("CMR_OBESE", "CM_OBESE"),
    "PERIPHERAL VASCULAR": ("CMR_PERIVASC", "CM_PERIVASC"),
    "HYPOTHYROIDISM": ("CMR_THYROID_HYPO", "CM_HYPOTHY"),
}
