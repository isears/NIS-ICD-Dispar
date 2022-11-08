import pandas as pd
import numpy as np
import docx
from nisicd.dataProcessing import categorical_lookup


def make_cell_bold(cell):
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.bold = True


def make_t1(df: pd.DataFrame, savename: str):

    # TODO: oooof
    # categorical_lookup["INCOME_QRTL"] = list(range(1, 5))

    doc = docx.Document()
    table_doc = doc.add_table(rows=1, cols=2)
    table_doc.autofit = True
    table_doc.allow_autofit = True

    header_row = table_doc.row_cells(0)
    header_row[0].text = "Demographics and Preoperative Characteristics"
    header_row[1].text = "N (%)"

    categoricals = df[[c for c in df.columns if c in categorical_lookup]]

    table1_df = pd.DataFrame()

    # Get age mean / sem
    age_mean = df["AGE"].mean()
    age_sem = df["AGE"].std() / np.sqrt(len(df))
    as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
    table1_df = pd.concat(
        [table1_df, pd.DataFrame(data={"N (%)": as_str}, index=["Age mean"])]
    )

    row = table_doc.add_row().cells
    row[0].text = "Age"
    make_cell_bold(row[0])
    row[1].text = as_str

    # Get > 65
    over65_count = (df["AGE"] > 65).sum()
    as_str = f"{over65_count:,} ({100 * over65_count / len(df):.2f})"
    table1_df = pd.concat(
        [table1_df, pd.DataFrame(data={"N (%)": as_str}, index=["AGE > 65"])]
    )

    row = table_doc.add_row().cells
    row[0].text = ">65"
    row[1].text = as_str

    # Get APDRG stats
    row = table_doc.add_row().cells
    row[0].text = "APDRG"
    make_cell_bold(row[0])

    for aprdrg_col in ["APRDRG_Severity", "APRDRG_Risk_Mortality"]:
        over2_count = (df[aprdrg_col] > 2).sum()
        as_str = f"{over2_count:,} ({100 * over2_count / len(df):.2f})"
        table1_df = pd.concat(
            [
                table1_df,
                pd.DataFrame(data={"N (%)": as_str}, index=[f"{aprdrg_col} > 2"]),
            ]
        )

        row = table_doc.add_row().cells
        row[0].text = f"{aprdrg_col} > 2"
        row[1].text = as_str

    for variable_name in categoricals.columns:
        row = table_doc.add_row().cells
        row[0].text = variable_name
        make_cell_bold(row[0])

        vc = categoricals[variable_name].value_counts()

        def format_n(n):
            percent = n / len(df) * 100
            return f"{n:,} ({percent:.2f})"

        this_var_df = pd.DataFrame(
            data={"N (%)": vc.apply(format_n).values},
            index=vc.index.map(lambda x: f"[{vc.name}] {x}"),
        )

        table1_df = table1_df.append(this_var_df)

        for subcat, n in zip(vc.index.to_list(), vc.to_list()):
            row = table_doc.add_row().cells
            row[0].text = str(subcat)
            row[1].text = format_n(n)

    for outcome_col in ["SSI", "PROLONGED_LOS", "DIED", "OR_RETURN"]:
        positive_count = df[outcome_col].sum()
        as_str = f"{positive_count:,} ({100 * positive_count / len(df):.2f})"
        table1_df = pd.concat(
            [
                table1_df,
                pd.DataFrame(data={"N (%)": as_str}, index=[f"{outcome_col}"]),
            ]
        )

        row = table_doc.add_row().cells
        row[0].text = f"{outcome_col}"
        row[1].text = as_str

    table1_df.to_csv(f"results/{savename}.csv")

    table_doc.style = "Table Grid"

    doc.save(f"results/{savename}.docx")

    return doc, table1_df


if __name__ == "__main__":
    processed_df = pd.read_parquet("cache/processed.parquet")

    insured_df = processed_df[processed_df["PAY1"] == "Private insurance"]
    uninsured_df = processed_df[processed_df["PAY1"] == "Self-pay"]

    make_t1(insured_df, "t1_insured")
    make_t1(uninsured_df, "t1_uninsured")
