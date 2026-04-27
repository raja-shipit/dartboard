#!/usr/bin/env python3
"""
GitHub Action script — pulls BESS data from EIA API,
writes bess_plants.js and metadata.json.
Runs in GitHub's cloud on schedule or manual trigger.
"""
import os, sys, json, requests
from datetime import datetime, timezone

API_KEY = os.environ.get("EIA_API_KEY", "")
if not API_KEY:
    print("ERROR: EIA_API_KEY secret not set in GitHub repo settings")
    sys.exit(1)

EIA_BASE = "https://api.eia.gov/v2"
ISO_MAP  = {
    "CISO":"CAISO","ERCO":"ERCOT","PJM":"PJM",
    "MISO":"MISO","NYIS":"NYISO","ISNE":"ISONE","SWPP":"SPP",
}
EIA_STATUS = {
    "OP":"Operating","SB":"Operating","OS":"Operating",
    "P":"Planned","L":"Planned","V":"Planned",
    "U":"Under Construction","T":"Under Construction","TS":"Under Construction",
    "RE":"Retired","CN":"Retired",
}

def eia_fetch(status_code):
    """Fetch battery storage generators by status from EIA API."""
    url = f"{EIA_BASE}/electricity/operating-generator-capacity/data/"
    all_rows, offset = [], 0
    while True:
        params = {
            "api_key":                       API_KEY,
            "facets[energy_source_code][]":  "BA",
            "facets[status][]":              status_code,
            "data[0]":  "nameplate-capacity-mw",
            "data[1]":  "nameplate-energy-capacity-mwh",
            "data[2]":  "latitude",
            "data[3]":  "longitude",
            "data[4]":  "county",
            "data[5]":  "balancing_authority_code",
            "length":   5000,
            "offset":   offset,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        resp = r.json().get("response", {})
        rows = resp.get("data", [])
        all_rows.extend(rows)
        total = resp.get("total", 0)
        offset += len(rows)
        print(f"  status={status_code}: fetched {offset}/{total}")
        if offset >= total or not rows:
            break
    return all_rows

def to_record(row, default_status):
    try:
        lat = float(row.get("latitude")  or 0)
        lon = float(row.get("longitude") or 0)
        mw  = float(row.get("nameplate-capacity-mw") or 0)
        mwh = float(row.get("nameplate-energy-capacity-mwh") or 0)
    except (ValueError, TypeError):
        return None
    if not (-90<=lat<=90 and -180<=lon<=180) or mw <= 0:
        return None
    ba     = str(row.get("balancing_authority_code") or "").strip()
    raw_st = str(row.get("status") or "").strip()
    try:   yr = int(row.get("operating_year") or row.get("planned_operation_year") or 0)
    except: yr = 0
    return {
        "name":   str(row.get("plant-name")    or "").strip(),
        "owner":  str(row.get("utility-name")  or "Unknown").strip(),
        "state":  str(row.get("state")         or "").strip(),
        "city":   str(row.get("city")          or "").strip(),
        "county": str(row.get("county")        or "").strip(),
        "addr":   "",
        "mw":     round(mw, 1),
        "mwh":    round(mwh, 1),
        "chem":   "Lithium-ion",
        "app":    "Grid Services",
        "status": EIA_STATUS.get(raw_st, default_status),
        "lat":    round(lat, 6),
        "lon":    round(lon, 6),
        "year":   yr,
        "iso":    ISO_MAP.get(ba, "Non-ISO"),
        "ba":     ba,
        "gen":    str(row.get("generator-id") or "").strip(),
    }

# ── Pull all statuses ─────────────────────────────────────────────────────────
print("Pulling BESS data from EIA API...")
records = []

status_groups = [
    (["OP", "SB"], "Operating"),
    (["P", "L", "V"], "Planned"),
    (["U", "T", "TS"], "Under Construction"),
    (["RE", "CN"], "Retired"),
]

for codes, label in status_groups:
    print(f"\n{label}:")
    for code in codes:
        try:
            rows = eia_fetch(code)
            for row in rows:
                rec = to_record(row, label)
                if rec:
                    records.append(rec)
        except Exception as e:
            print(f"  WARNING: status={code} failed: {e}")

records.sort(key=lambda x: -x["mw"])

# ── Stats ─────────────────────────────────────────────────────────────────────
by_status = {}
for r in records:
    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
total_mw = sum(r["mw"] for r in records)
now_utc  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

print(f"\n{'='*50}")
print(f"Total records: {len(records)}")
print(f"By status: {by_status}")
print(f"Total MW: {total_mw:,.0f}")

# ── Write bess_plants.js ──────────────────────────────────────────────────────
js = f"// EIA API pull: {now_utc} | {len(records)} sites | {total_mw:,.0f} MW\n"
js += "const EIA_BESS_PLANTS = " + json.dumps(records, separators=(",",":")) + ";"
open("bess_plants.js", "w").write(js)
print(f"\nbess_plants.js written: {len(js):,} chars")

# ── Write metadata.json ───────────────────────────────────────────────────────
# Calculate data_as_of (EIA-860M is ~1 month lagged)
from datetime import timedelta
data_as_of_dt = datetime.now(timezone.utc) - timedelta(days=35)
data_as_of    = data_as_of_dt.strftime("%Y-%m-%d")

meta = {
    "last_updated":      now_utc,
    "last_updated_date": today,
    "source":            "EIA Form 860M (monthly)",
    "site_count":        len(records),
    "total_mw":          round(total_mw, 1),
    "by_status":         by_status,
    "data_as_of":        data_as_of,
    "lag_days":          35,
    "lag_note":          "EIA-860M data is typically lagged ~1 month. This is normal — EIA publishes on the 22nd of each month.",
    "next_eia_release":  (datetime.now(timezone.utc).replace(day=22) + timedelta(days=32)).strftime("%Y-%m-22"),
    "eia_source_url":    "https://www.eia.gov/electricity/data/eia860m/",
}
open("metadata.json", "w").write(json.dumps(meta, indent=2))
print(f"metadata.json written")
print(f"\n✅ Done — dashboard will show data as of {data_as_of}")
