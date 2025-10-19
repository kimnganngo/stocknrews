from datetime import datetime, timedelta
from dateutil import tz

TZ = tz.gettz("Asia/Bangkok")

def now_tz():
    return datetime.now(tz=TZ)

def get_cutoff_time(label: str) -> datetime:
    mapping = {
        "6h": 6,
        "12h": 12,
        "24h": 24,
        "48h": 48,
        "7 ngày": 24 * 7,
        "30 ngày": 24 * 30,
    }
    hours = mapping.get(label, 24)
    return now_tz() - timedelta(hours=hours)
