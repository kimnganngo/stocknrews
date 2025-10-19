from collections import defaultdict
import re
import pandas as pd

def build_name_index(df: pd.DataFrame):
    idx = defaultdict(set)  # token -> set(ticker)
    for _, row in df.iterrows():
        code = str(row.get("Mã CK", "")).upper().strip()
        name = str(row.get("Tên công ty", "")).lower()
        tokens = [t for t in re.split(r"[^\w]+", name) if len(t) >= 4]
        for t in tokens:
            idx[t].add(code)
    return idx
