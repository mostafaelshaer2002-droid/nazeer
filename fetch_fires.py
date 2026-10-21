"""
نذير - المرحلة 1: تحميل حرائق مصر من أقمار ناسا (FIRMS) وحفظها في ملف JSON.

التشغيل (على جهازك):
    set FIRMS_MAP_KEY=مفتاحك_هنا        (في Windows CMD)
    python fetch_fires.py

مفيش مكتبات خارجية. Python بس.
"""
import csv
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

# مستطيل يغطي مصر: غرب, جنوب, شرق, شمال
BBOX = "24.7,21.9,36.9,31.7"
SOURCES = ["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT"]  # لو اسم مصدر غلط، شغّل check_sources.py
DAYS = 3  # الواجهة بتقبل من 1 لـ 5 أيام
OUT_FILE = os.path.join("docs", "data", "fires.json")


def fetch_csv(key, source):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{BBOX}/{DAYS}"
    with urllib.request.urlopen(url, timeout=60) as r:
        text = r.read().decode("utf-8")
    if "Invalid" in text[:200] or not text.startswith("latitude"):
        raise RuntimeError(f"رد غير متوقع من ناسا ({source}): {text[:120]}")
    return text


def parse(text):
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            rows.append({
                "lat": round(float(r["latitude"]), 4),
                "lon": round(float(r["longitude"]), 4),
                "date": r["acq_date"],
                "time": r["acq_time"].zfill(4),  # توقيت UTC
                "conf": r.get("confidence", ""),
                "frp": float(r["frp"]) if r.get("frp") else None,
                "dn": r.get("daynight", ""),
            })
        except (KeyError, ValueError):
            continue  # نتخطى أي سطر بايظ بدل ما البرنامج يقع
    return rows


def main():
    key = os.environ.get("FIRMS_MAP_KEY", "").strip()
    if not key:
        sys.exit("مفيش مفتاح. ضيف FIRMS_MAP_KEY (شوف الشرح).")

    fires, errors = [], []
    for src in SOURCES:
        try:
            fires.extend(parse(fetch_csv(key, src)))
        except Exception as e:  # لو مصدر فشل نكمل بالباقي
            errors.append(f"{src}: {e}")

    # لو كل المصادر فشلت: نسيب ملف امبارح زي ما هو
    if not fires and errors:
        print("فشل التحميل، هنسيب الملف القديم:", *errors, sep="\n  ")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    out = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "days": DAYS,
        "count": len(fires),
        "warnings": errors,
        "fires": fires,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"تمام: {len(fires)} حريق اتحفظوا في {OUT_FILE}")
    for e in errors:
        print("تنبيه:", e)


if __name__ == "__main__":
    main()
