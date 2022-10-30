"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
from nisicd import logging
from nisicd.dataProcessing import ssi_codes
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import re


class ParallelFilter:
    def __init__(self) -> None:
        logging.info("Initializing parallel filter...")
        self.all_dx_codes = ssi_codes

        logging.info(f"[*] Dx codes ({len(self.all_dx_codes)}):")
        logging.info(self.all_dx_codes)

    @staticmethod
    def get_proc_cols(all_cols):
        icd9_proc_cols = [col for col in all_cols if re.search("^PR[0-9]{1,2}$", col)]
        icd10_proc_cols = [
            col for col in all_cols if re.search("^I10_PR[0-9]{1,2}$", col)
        ]

        return icd9_proc_cols + icd10_proc_cols

    @staticmethod
    def get_dx_cols(all_cols):
        icd9_cols = [col for col in all_cols if re.search("^DX[0-9]{1,2}$", col)]
        icd10_cols = [col for col in all_cols if re.search("^I10_DX[0-9]{1,2}$", col)]

        return icd9_cols + icd10_cols

    def _get_relevant_dx(self, df):
        proc_cols = self.get_dx_cols(df.columns)

        relevant = df[df[proc_cols].isin(self.all_dx_codes).any(axis="columns")]

        return relevant

    def single_file_filter(self, fname):
        df = pd.read_parquet(fname)
        relevant = self._get_relevant_dx(df)
        return relevant

    def single_file_yearcount(self, fname):
        """
        For building fig 1
        """
        df = pd.read_parquet(fname)
        relevant_procs = self._get_relevant_dx(df)

        def organaze_as_counts(df: pd.DataFrame):
            counts = df["YEAR"].value_counts().sort_index()
            counts = counts.reset_index()
            counts.columns = ["Year", "Count"]

            return counts

        proc_counts = organaze_as_counts(relevant_procs)

        return proc_counts


if __name__ == "__main__":
    parallel_filter = ParallelFilter()

    with ProcessPoolExecutor(max_workers=16) as executor:
        fnames = glob.glob("data/*.parquet")
        res = list(
            tqdm(
                executor.map(parallel_filter.single_file_filter, fnames),
                total=len(fnames),
            )
        )

    filtered_df = pd.concat(res)

    print(filtered_df)

    # Pyarrow (parquet) complains if this column is dealt with
    filtered_df.HOSPSTCO = filtered_df.HOSPSTCO.astype("str")

    filtered_df.to_parquet("./cache/ssi.parquet", index=False)
