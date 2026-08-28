from datetime import datetime, timezone, timedelta


def normalize_to_utc(dt: datetime):
    if not dt:
        return None
    if dt.tzinfo is None:
        # Giả định GMT+7 nếu không có múi giờ
        dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
    return dt.astimezone(timezone.utc)