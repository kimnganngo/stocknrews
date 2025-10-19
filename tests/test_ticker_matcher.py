import pandas as pd
from src.matching.ticker_matcher import match_tickers_context
from src.matching.name_index import build_name_index

def test_match_basic():
    df = pd.DataFrame({"Mã CK": ["VND"], "Tên công ty": ["VNDirect"], "Sàn": ["HOSE"]})
    idx = build_name_index(df)
    title = "Cổ phiếu VND tăng trần trong phiên"
    content = ""
    out = match_tickers_context(title, content, df, idx, ambiguous_codes=set())
    assert out == ["VND"]

def test_ambiguous_needs_context():
    df = pd.DataFrame({"Mã CK": ["CEO"], "Tên công ty": ["CEO Group"], "Sàn": ["HOSE"]})
    idx = build_name_index(df)
    title = "CEO công bố kế hoạch kinh doanh"
    content = ""
    out = match_tickers_context(title, content, df, idx, ambiguous_codes={"CEO"})
    assert out == []
