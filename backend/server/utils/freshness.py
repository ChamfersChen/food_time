from datetime import date, timedelta


def calc_freshness(expire_date: date) -> dict:
    if isinstance(expire_date, str):
        expire_date = date.fromisoformat(expire_date)

    today = date.today()
    days = (expire_date - today).days

    if days > 3:
        status = "fresh"
    elif days >= 0:
        status = "expiring"
    else:
        status = "expired"

    if days > 3:
        label = f"{days}天"
    elif days > 0:
        label = f"还剩 {days} 天"
    elif days == 0:
        label = "今天过期"
    else:
        label = "已过期"

    color_map = {"fresh": "#7BBF8E", "expiring": "#F0A050", "expired": "#E05A50"}
    bar_width = min(days / 30, 1) if status == "fresh" else (max(days / 3, 0.1) if status == "expiring" else 0)

    return {
        "days": days,
        "status": status,
        "label": label,
        "color": color_map.get(status, "#888780"),
        "bar_width": bar_width,
    }