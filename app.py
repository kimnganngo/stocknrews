import io
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from src.scraping.router import ScraperRouter
from src.parsing.date_parser import parse_article_datetime
from src.matching.ticker_matcher import match_tickers_context
from src.matching.name_index import build_name_index
from src.analysis.summarizer import summarize_text
from src.analysis.sentiment import score_sentiment_and_risk, load_keywords
from src.export.excel_export import dataframe_to_excel_bytes
from src.utils.time_utils import get_cutoff_time, now_tz
from src.utils.logging import LogCounter

st.set_page_config(page_title="StockNews – VN", layout="wide")
st.title("📰 StockNews – Bộ lọc tin chứng khoán (VN)")

# --- Sidebar controls ---
st.sidebar.header("⚙️ Cấu hình")

uploaded = st.sidebar.file_uploader("Upload danh sách mã (Excel/CSV)", type=["xlsx", "xls", "csv"], accept_multiple_files=False)
interval_label = st.sidebar.selectbox("Khoảng thời gian", ["6h", "12h", "24h", "48h", "7 ngày", "30 ngày"], index=2)
strict_mode = st.sidebar.toggle("Strict date filter (loại bài không rõ ngày)", value=True)

# Load config
with open("config/sources.yaml", "r", encoding="utf-8") as f:
    sources_cfg = yaml.safe_load(f)
with open("config/keywords.yaml", "r", encoding="utf-8") as f:
    kw_cfg = yaml.safe_load(f)

use_sources = st.sidebar.multiselect(
    "Nguồn",
    [s["name"] for s in sources_cfg["sources"]],
    default=[s["name"] for s in sources_cfg["sources"]],
)

use_llm = False
if "OPENAI_API_KEY" in st.secrets:
    use_llm = st.sidebar.toggle("Dùng LLM tóm tắt (cần key)", value=False)

if st.sidebar.button("🚀 Bắt đầu", type="primary"):
    st.session_state["run"] = True

# --- Helper: load tickers file ---
def load_tickers(file) -> pd.DataFrame:
    if file is None:
        return pd.read_csv("data/sample_stocks.csv")
    suffix = Path(file.name).suffix.lower()
    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)
    # Normalize
    mapping = {}
    for expected in ["mã ck", "ma ck", "ticker", "ma"]:
        for c in df.columns:
            if c.lower().strip() == expected:
                mapping[c] = "Mã CK"
    for expected in ["tên công ty", "ten cong ty", "company", "ten"]:
        for c in df.columns:
            if c.lower().strip() == expected:
                mapping[c] = "Tên công ty"
    for expected in ["sàn", "san", "exchange"]:
        for c in df.columns:
            if c.lower().strip() == expected:
                mapping[c] = "Sàn"
    df = df.rename(columns=mapping)
    for col in ["Mã CK", "Tên công ty", "Sàn"]:
        if col not in df.columns:
            df[col] = None
    df["Mã CK"] = df["Mã CK"].astype(str).str.upper().str.strip()
    df = df.dropna(subset=["Mã CK"]).drop_duplicates("Mã CK")
    return df[["Mã CK", "Tên công ty", "Sàn"]]

# --- Main run ---
if st.session_state.get("run"):
    df_tickers = load_tickers(uploaded)
    st.sidebar.success(f"Đã nạp {len(df_tickers)} mã")
    name_index = build_name_index(df_tickers)
    ambiguous_codes = set(kw_cfg.get("ambiguous_codes", []))
    sentiment_kw = load_keywords(kw_cfg)

    cutoff = get_cutoff_time(interval_label)
    st.write(f"**Cutoff:** {cutoff.strftime('%d/%m/%Y %H:%M')} (UTC+7) | Strict: {strict_mode}")

    router = ScraperRouter(sources_cfg)
    sources = [router.get_scraper_by_name(n) for n in use_sources]

    log = LogCounter()
    status = st.status("Đang cào dữ liệu...", expanded=True)

    rows = []
    with status:
        for src in sources:
            st.write(f"**Nguồn:** {src.name}")
            links = src.list_article_links()
            st.write(f"- Thu thập link: {len(links)}")
            for i, url in enumerate(links, start=1):
                try:
                    art = src.fetch_article(url)
                except Exception as e:
                    log.http_errors += 1
                    continue
                # Date parse + strict filter
                dt_obj, dt_str = parse_article_datetime(art.html, art.url, src.date_configs)
                if dt_obj is None:
                    log.no_date += 1
                    if strict_mode:
                        continue
                else:
                    if dt_obj < cutoff:
                        log.out_of_time += 1
                        continue
                # Ticker match
                matched = match_tickers_context(
                    title=art.title,
                    content=art.content,
                    df_tickers=df_tickers,
                    name_index=name_index,
                    ambiguous_codes=ambiguous_codes,
                )
                if not matched:
                    log.no_ticker += 1
                    continue
                # Summarize
                summary = summarize_text(art.content, use_llm=use_llm)
                # Sentiment / Risk
                senti, score, risk, hits = score_sentiment_and_risk(art.title + "\n" + art.content, sentiment_kw)

                for code in matched:
                    row = {
                        "Ngày": dt_obj,
                        "Mã CK": code,
                        "Tên công ty": df_tickers.set_index("Mã CK").get("Tên công ty").get(code),
                        "Sàn": df_tickers.set_index("Mã CK").get("Sàn").get(code),
                        "Nguồn": src.name,
                        "Tiêu đề": art.title,
                        "Tóm tắt": summary,
                        "Sentiment": senti,
                        "Điểm": score,
                        "Risk": risk,
                        "Keywords": ", ".join(hits),
                        "Link": art.url,
                    }
                    rows.append(row)
                log.valid += 1
                if i % 10 == 0:
                    st.write(f".. đã xử lý {i} bài từ {src.name}")
            st.write("—")
    status.update(label="Hoàn tất", state="complete")

    if not rows:
        st.warning("Không có bài phù hợp bộ lọc. Hãy nới rộng thời gian hoặc tắt strict mode.")
        st.stop()

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["Ngày"], ascending=False).reset_index(drop=True)

    # Filters
    st.subheader("📊 Bảng kết quả")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_code = st.multiselect("Lọc Mã CK", sorted(df["Mã CK"].dropna().unique().tolist()))
    with col2:
        f_san = st.multiselect("Lọc Sàn", sorted(df["Sàn"].dropna().unique().tolist()))
    with col3:
        f_risk = st.multiselect("Lọc Risk", sorted(df["Risk"].dropna().unique().tolist()))
    with col4:
        f_src = st.multiselect("Lọc Nguồn", sorted(df["Nguồn"].dropna().unique().tolist()))

    def apply_filters(_df):
        out = _df.copy()
        if f_code:
            out = out[out["Mã CK"].isin(f_code)]
        if f_san:
            out = out[out["Sàn"].isin(f_san)]
        if f_risk:
            out = out[out["Risk"].isin(f_risk)]
        if f_src:
            out = out[out["Nguồn"].isin(f_src)]
        return out

    dff = apply_filters(df)
    st.dataframe(dff.assign(**{"Ngày": dff["Ngày"].dt.strftime("%d/%m/%Y %H:%M")}), use_container_width=True)

    # Export
    st.markdown("---")
    st.subheader("⬇️ Xuất Excel")
    from src.export.excel_export import dataframe_to_excel_bytes
    bio = dataframe_to_excel_bytes(df)
    st.download_button(
        label="Tải file Excel",
        data=bio,
        file_name=f"stocknews_{now_tz().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Stats
    st.markdown("---")
    st.subheader("📈 Trạng thái")
    st.json(log.as_dict())
else:
    st.info("Upload danh sách mã (hoặc dùng mẫu), cấu hình ở sidebar rồi bấm **Bắt đầu**.")
