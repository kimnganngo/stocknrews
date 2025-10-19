import re
from typing import List, Set
import pandas as pd

CONTEXT_WORDS = {
    "mã", "mã cổ phiếu", "cổ phiếu", "cp", "giá", "khớp lệnh", "giao dịch",
    "niêm yết", "hose", "hnx", "upcom", "sàn", ":", "("
}

def _window_has_context(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in CONTEXT_WORDS)

def match_tickers_context(title: str, content: str, df_tickers: pd.DataFrame,
                          name_index: dict, ambiguous_codes: Set[str]) -> List[str]:
    title = title or ""
    content_head = (content or "")[:400]
    combined = f"{title}\n{content_head}"

    codes = set(df_tickers["Mã CK"].astype(str).str.upper().tolist())
    found = set()

    for code in codes:
        for m in re.finditer(rf"\b{re.escape(code)}\b", combined):
            span = combined[max(0, m.start()-20): m.end()+20]
            if len(code) <= 3 or code in ambiguous_codes:
                if not _window_has_context(span):
                    continue
            found.add(code)
            break

    if not found:
        tokens = re.findall(r"\w+", title.lower())
        candidates = {}
        for t in tokens:
            if len(t) >= 4 and t in name_index:
                for code in name_index[t]:
                    candidates[code] = candidates.get(code, 0) + 1
        for code, score in candidates.items():
            if score >= 2:
                found.add(code)
            elif score >= 1:
                if _window_has_context(combined[:120]):
                    found.add(code)
    return sorted(found)
