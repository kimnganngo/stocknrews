# StockNews – Bộ lọc tin chứng khoán (VN)

Tool Streamlit cào/lọc/tóm tắt tin từ CafeF & Vietstock theo danh sách mã CK, có strict time filter, nhận diện mã theo **ngữ cảnh**, sentiment & risk rule-based, xuất Excel.

## Chạy local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy trên Streamlit Cloud
1. Push repo này lên GitHub.
2. Tạo app mới, chọn `App file = app.py`.
3. (Tuỳ chọn) Thêm `OPENAI_API_KEY` vào Secrets nếu muốn dùng LLM.
4. Wide layout mặc định; không cần DB.

## Input danh sách mã
- Dùng `data/sample_stocks.csv` hoặc upload file của bạn với cột: `Mã CK, Tên công ty, Sàn`.

## Cấu hình nguồn & từ khoá
- `config/sources.yaml` để thêm/chỉnh nguồn.
- `config/keywords.yaml` để chỉnh sentiment/risk & mã mơ hồ.

## Lưu ý
- **Strict mode** mặc định bật: bài không rõ ngày sẽ bị loại.
- Có retry/backoff nhẹ, cache theo URL.
- Tôn trọng robots.txt; không cào quá gắt.
