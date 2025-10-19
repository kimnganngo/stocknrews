import io
import pandas as pd
from datetime import datetime

def _prep(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df.copy()
    dfx["Ngày"] = pd.to_datetime(dfx["Ngày"]).dt.strftime("%d/%m/%Y %H:%M")
    return dfx

def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    dfx = _prep(df)
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        dfx.to_excel(w, index=False, sheet_name="All")
        for risk in ["Severe", "Warning", "Normal"]:
            dfr = dfx[dfx["Risk"] == risk]
            if not dfr.empty:
                dfr.to_excel(w, index=False, sheet_name=risk)
        for sheet in w.book.worksheets:
            sheet.freeze_panes = "A2"
            for col in sheet.columns:
                maxlen = max((len(str(c.value)) if c.value is not None else 0) for c in col)
                col_letter = col[0].column_letter
                sheet.column_dimensions[col_letter].width = min(maxlen + 2, 60)
    out.seek(0)
    return out.read()
