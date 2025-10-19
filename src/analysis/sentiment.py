from typing import Dict, Tuple, List

def load_keywords(cfg: Dict) -> Dict:
    return {
        "pos": set(cfg.get("sentiment", {}).get("positive", [])),
        "neg": set(cfg.get("sentiment", {}).get("negative", [])),
        "sev": set(cfg.get("risk", {}).get("severe", [])),
        "warn": set(cfg.get("risk", {}).get("warning", [])),
    }

def score_sentiment_and_risk(text: str, kw: Dict) -> Tuple[str, int, str, List[str]]:
    text_l = (text or "").lower()
    score = 0
    hits = []
    for k in kw["pos"]:
        if k in text_l:
            score += 1
            hits.append(k)
    for k in kw["neg"]:
        if k in text_l:
            score -= 1
            hits.append(k)
    if score > 1:
        senti = "Tích cực"
    elif score < 0:
        senti = "Tiêu cực"
    else:
        senti = "Trung lập"
    risk = "Normal"
    if any(k in text_l for k in kw["sev"]):
        risk = "Severe"
    elif any(k in text_l for k in kw["warn"]):
        risk = "Warning"
    return senti, max(min(score, 5), -5), risk, hits
