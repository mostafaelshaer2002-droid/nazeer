"""اختبار بدون إنترنت: بنتأكد إن القراءة شغالة على عينة شبه رد ناسا."""
from fetch_fires import parse

SAMPLE = (
    "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight\n"
    "31.1234,30.5678,330.1,0.4,0.4,2026-10-20,0112,N,VIIRS,n,2.0NRT,290.2,3.5,N\n"
    "30.9,31.2,345.0,0.4,0.4,2026-10-20,1115,N,VIIRS,h,2.0NRT,295.0,12.1,D\n"
    "ده سطر بايظ\n"
)
rows = parse(SAMPLE)
assert len(rows) == 2, rows
assert rows[0]["time"] == "0112" and rows[1]["conf"] == "h"
print("الاختبار نجح:", rows)
