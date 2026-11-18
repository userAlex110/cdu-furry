#!/usr/bin/env python3
"""Offline scenario calculator for docs/backend-selection.md.
Prices: official public pages read 2026-11-18 Asia/Shanghai.
Outputs are priced CORE SUBTOTALS, never full bills. Unknown extras remain None.
Physical byte amounts use decimal GB; memory uses GiB. COS tariff GB is 2**30 bytes.
No cloud API, network, credentials, or paid services used.
Run: python3 docs/backend-metered-cost.py
"""
import json
import math
from pathlib import Path

GB = 10**9
COS_GB = 2**30
DAYS = 30
HOURS = DAYS * 24
TIMER = DAYS * 24 * 12
BACKUPS = 4
SCENARIOS = [
    dict(name="idle", visits=0, photos=0, writes=0, db_gb=.05, objects_gb=2, original_views=0),
    dict(name="light", visits=1000, photos=50, writes=200, db_gb=.10, objects_gb=5, original_views=20),
    dict(name="regular", visits=10000, photos=300, writes=2000, db_gb=.30, objects_gb=15, original_views=200),
]
# DCloud price table, SCF public rates, BTS, COS Guangzhou sample. See docs/backend-selection-sources.md.
RATES = {
    "uni": dict(gbs=.000110592, calls_per_10k=.0133, function_gb=.8,
                db_gb_day=.07, read_per_10k=.015, write_per_10k=.05,
                object_gb_day=.004, get_per_10k=.01, put_per_10k=.01,
                cdn_gb=.18, origin_gb=.15),
    "scf": dict(gbs=.00011108, calls_per_10k=.0133, network_gb=.8),
    "bts": dict(read_per_10k=.0027, write_per_10k=.0054, db_gb_hour=.00042, network_gb=.75),
    "cos": dict(object_gb_month=.118, requests_per_10k=.01, network_gb=.5),
    "cfc": dict(gbs=.00011, calls_per_1m=1.3, network_gb=.76),
}

def usage(s):
    api = s["visits"] * 8
    images = s["visits"] * 12
    calls = api + s["photos"] + TIMER + BACKUPS
    gbs = api * .25 * .2 + s["photos"] * .5 * 5 + TIMER * .25 * .2 + BACKUPS * .5 * 10
    reads = api * 4 + TIMER + math.ceil(BACKUPS * s["db_gb"] * GB / 4096)
    writes = s["writes"] * 3  # explicit assumed write amplification, not a provider guarantee
    image_bytes = images * 80000 + s["original_views"] * 800000
    db_response_bytes = api * 4 * 2000 + TIMER * 256 + BACKUPS * s["db_gb"] * GB
    db_request_bytes = (api + TIMER + BACKUPS + writes) * 512
    return dict(api=api, images=images, calls=calls, gbs=gbs, read_units=reads,
                write_units=writes, image_bytes=image_bytes,
                db_response_bytes=db_response_bytes, db_request_bytes=db_request_bytes,
                client_response_bytes=api*8000, client_request_bytes=api*1000,
                get=images+s["original_views"]+s["photos"], put=s["photos"]*3+BACKUPS)

def result(s):
    u = usage(s)
    p = RATES["uni"]
    # Viewer bytes: 100% on CDN, 20% origin. Compressor original fetch: CDN plus 100% origin.
    # These are two metered lines, not a second copy of the same CDN charge.
    # This model does not also add a COS egress line for the same images.
    cdn_gb = u["image_bytes"]/GB + s["photos"]*.0008
    origin_gb = u["image_bytes"]/GB*.2 + s["photos"]*.0008
    origin_get = (u["images"]+s["original_views"])*.2 + s["photos"]
    uni = dict(function=u["gbs"]*p["gbs"]+u["calls"]/10000*p["calls_per_10k"],
               function_network=u["client_response_bytes"]/GB*p["function_gb"],
               db_storage=s["db_gb"]*DAYS*p["db_gb_day"],
               db_io=u["read_units"]/10000*p["read_per_10k"]+u["write_units"]/10000*p["write_per_10k"],
               object_storage=s["objects_gb"]*DAYS*p["object_gb_day"],
               object_requests=(u["get"]+origin_get+u["put"])/10000*p["get_per_10k"],
               cdn=cdn_gb*p["cdn_gb"], origin=origin_gb*p["origin_gb"])
    free = dict(function=max(0,u["gbs"]-1000)*p["gbs"]+max(0,u["calls"]-15000)/10000*p["calls_per_10k"],
                function_network=max(0,u["client_response_bytes"]/GB-1)*p["function_gb"],
                db_storage=max(0,s["db_gb"]*DAYS-6.2)*p["db_gb_day"],
                db_io=max(0,u["read_units"]-620000)/10000*p["read_per_10k"]+max(0,u["write_units"]-310000)/10000*p["write_per_10k"],
                object_storage=max(0,s["objects_gb"]*DAYS-155)*p["object_gb_day"],
                object_requests=max(0,u["get"]+origin_get-2000)/10000*p["get_per_10k"]+max(0,u["put"]-1000)/10000*p["put_per_10k"],
                cdn=max(0,cdn_gb-1)*p["cdn_gb"], origin=max(0,origin_gb-.5)*p["origin_gb"])
    t, b = RATES["scf"], RATES["bts"]
    mixed = dict(function=u["gbs"]*t["gbs"]+u["calls"]/10000*t["calls_per_10k"],
                 function_network=(u["client_response_bytes"]+u["db_request_bytes"])/GB*t["network_gb"],
                 db_storage=s["db_gb"]*HOURS*b["db_gb_hour"],
                 db_io=u["read_units"]/10000*b["read_per_10k"]+u["write_units"]/10000*b["write_per_10k"],
                 db_network=u["db_response_bytes"]/GB*b["network_gb"],
                 object_storage=s["objects_gb"]*GB/COS_GB*RATES["cos"]["object_gb_month"],
                 object_requests=(u["get"]+u["put"])/10000*RATES["cos"]["requests_per_10k"],
                 images=u["image_bytes"]/COS_GB*RATES["cos"]["network_gb"])
    # Cross-cloud: COS egress and CFC public traffic are different vendors' lines.
    # Viewer image bytes are on COS only, not also inside function_network.
    cfcmixed = mixed.copy()
    cfcmixed["function"] = u["gbs"]*RATES["cfc"]["gbs"]+u["calls"]/1e6*RATES["cfc"]["calls_per_1m"]
    cfcmixed["function_network"] = (u["client_request_bytes"]+u["client_response_bytes"]+u["db_request_bytes"]+u["db_response_bytes"]+s["photos"]*960000)/GB*RATES["cfc"]["network_gb"]
    cfcmixed["compression_cos_egress"] = s["photos"]*800000/COS_GB*RATES["cos"]["network_gb"]
    models = {"uni_pure_metered": uni, "uni_free_plus_overage": free,
              "scf_bts_cos": mixed, "cfc_bts_cos_conservative_public": cfcmixed}
    for v in models.values():
        v["priced_core_subtotal"] = sum(x for x in v.values() if isinstance(x, (int, float)))
        v["unknown_extras"] = None
        v["full_bill"] = None
    return dict(scenario=s, usage=u, models=models)

if __name__ == "__main__":
    out = {"date": "2026-11-18 Asia/Shanghai", "rates": RATES, "months_days": DAYS,
           "unknowns": "logs, moderation, certificates/domain amortization, hidden billing floors, actual account availability, required gateway extras",
           "fc_timer_floor_per_function": HOURS * .01,
           "tdsql_unpaused_compute_at_025_ccu": .25 * .000095 * DAYS * 86400,
           "memory_basis_gib": 0.25,
           "note": "256MiB is a scenario assumption. uniCloud Alipay default memory on the functions page is 512MB. full_bill stays null.",
           "results": [result(s) for s in SCENARIOS]}
    path = Path(__file__).with_name("backend-metered-cost-results.json")
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    for row in out["results"]:
        print(row["scenario"]["name"], row["usage"]["calls"], row["usage"]["gbs"])
        for name, vals in row["models"].items():
            print(" ", name, round(vals["priced_core_subtotal"], 4), "+ U")
    assert out["fc_timer_floor_per_function"] == 7.2
    assert abs(out["tdsql_unpaused_compute_at_025_ccu"] - 61.56) < 1e-8
    assert all(v["full_bill"] is None for r in out["results"] for v in r["models"].values())
    assert [r["usage"]["gbs"] for r in out["results"]] == [452.0, 977.0, 5202.0]
    cores = [round(r["models"]["uni_pure_metered"]["priced_core_subtotal"], 4) for r in out["results"]]
    assert cores == [0.4927, 1.4347, 6.8726], cores
    print(path)
