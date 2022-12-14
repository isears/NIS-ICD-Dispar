"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
from nisicd import logging
from nisicd.dataProcessing import DX_CODES
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import re
import os


class ParallelFilter:
    def __init__(
        self, dx_codes=[], dx_as_primary=False, proc_codes=[], proc_as_primary=False
    ) -> None:
        logging.info("Initializing parallel filter...")
        self.dx_codes = dx_codes
        self.proc_codes = proc_codes
        self.dx_as_primary = dx_as_primary
        self.proc_as_primary = proc_as_primary

        self.cores_available = len(os.sched_getaffinity(0))

        logging.info(f"[*] Dx codes ({len(self.dx_codes)}):")
        logging.info(self.dx_codes)

        logging.info(f"[*] Proc codes ({len(self.proc_codes)}):")
        logging.info(self.proc_codes)

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

    def __find_in_cols(self, df, cols, vals):
        return df[df[cols].isin(vals).any(axis="columns")]

    def _get_relevant_dx(self, df):

        if len(self.dx_codes) == 0:
            return df

        dx_cols = self.get_dx_cols(df.columns)

        if self.dx_as_primary:
            dx_cols = [c for c in dx_cols if c in ["DX1", "I10_DX1"]]

        return self.__find_in_cols(df, dx_cols, self.dx_codes)

    def _get_relevant_proc(self, df):
        if len(self.proc_codes) == 0:
            return df

        proc_cols = self.get_proc_cols(df.columns)

        if self.proc_as_primary:
            proc_cols = [c for c in proc_cols if c in ["PR1", "I10_PR1"]]

        return self.__find_in_cols(df, proc_cols, self.proc_codes)

    def single_file_filter(self, fname):
        df = pd.read_parquet(fname)
        relevant = self._get_relevant_dx(df)
        relevant = self._get_relevant_proc(relevant)
        return relevant

    def parallel_file_filter(self, fnames):
        logging.info(f"Running filter with {self.cores_available} processes")
        with ProcessPoolExecutor(max_workers=self.cores_available) as executor:
            res = list(
                tqdm(executor.map(self.single_file_filter, fnames), total=len(fnames))
            )

        filtered_df = pd.concat(res)
        # Pyarrow (parquet) complains if this column is dealt with
        filtered_df.HOSPSTCO = filtered_df.HOSPSTCO.astype("str")
        filtered_df.to_parquet("./cache/appendicitis.parquet", index=False)

        logging.info(f"[+] Parallel filter done final count: {len(filtered_df)}")


if __name__ == "__main__":
    dx_codes = []

    for key, val in DX_CODES.items():
        dx_codes += val

    parallel_filter = ParallelFilter(dx_codes=dx_codes, dx_as_primary=True)
    fnames = glob.glob("data/*.parquet")

    parallel_filter.parallel_file_filter(fnames)
