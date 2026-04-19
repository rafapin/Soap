"""
Synthetic SCADA alarm dataset generator.

Generates:
  - data/raw/alarms_dataset.csv
  - data/raw/alarms_dataset.json

Run:
  python scripts/generate_dataset.py [--size 2000] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

PLANTS = ["PLANT_A", "PLANT_B", "PLANT_C"]
AREAS = ["AREA_01", "AREA_02", "AREA_03", "AREA_04"]
EQUIPMENTS = [f"EQ-{i:03d}" for i in range(1, 31)]
TAGS = [f"TAG_{chr(65 + i % 26)}{i:04d}" for i in range(1, 51)]
SOURCES = ["SIEMENS_SCADA", "ABB_SCADA", "HONEYWELL_DCS", "ROCKWELL_PLC"]
CRITICALITIES_VALID = ["HIGH", "MEDIUM", "LOW"]
STATES_VALID = ["ACTIVE", "ACKNOWLEDGED", "CLEARED", "SHELVED"]

# Intentional error variants
CRITICALITY_VARIANTS = [
    "HIGH", "High", "high", "H",
    "MEDIUM", "Medium", "medium", "MED", "M",
    "LOW", "Low", "low", "L",
]
INVALID_CRITICALITIES = ["CRITICAL", "URGENT", "P1", "1", "unknown", ""]
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
]


def random_datetime(base: datetime, offset_range_hours: int = 720) -> datetime:
    return base - timedelta(hours=random.randint(0, offset_range_hours))


def format_datetime(dt: datetime, fmt_idx: int) -> str:
    return dt.strftime(DATE_FORMATS[fmt_idx % len(DATE_FORMATS)])


def generate_valid_record(rng: random.Random, base_dt: datetime, idx: int) -> dict:
    event_time = random_datetime(base_dt, 720)
    state = rng.choice(STATES_VALID)
    ack_time = event_time + timedelta(minutes=rng.randint(1, 60)) if state in {"ACKNOWLEDGED", "CLEARED"} else None
    clear_time = ack_time + timedelta(minutes=rng.randint(5, 120)) if state == "CLEARED" else None

    return {
        "external_alarm_id": f"ALM-{idx:06d}",
        "source_system": rng.choice(SOURCES),
        "tag": rng.choice(TAGS),
        "message": f"Process variable out of range on {rng.choice(EQUIPMENTS)}",
        "priority": rng.randint(1, 5),
        "criticality": rng.choice(CRITICALITIES_VALID),
        "state": state,
        "event_time": format_datetime(event_time, 0),
        "ack_time": format_datetime(ack_time, 0) if ack_time else "",
        "clear_time": format_datetime(clear_time, 0) if clear_time else "",
        "plant": rng.choice(PLANTS),
        "area": rng.choice(AREAS),
        "equipment": rng.choice(EQUIPMENTS),
    }


def inject_errors(records: list[dict], rng: random.Random) -> list[dict]:
    """Inject intentional data quality problems into a copy of the records list."""
    errored: list[dict] = []
    error_pool = [
        lambda r: {**r, "tag": ""},                                          # missing tag
        lambda r: {**r, "event_time": ""},                                    # missing event_time
        lambda r: {**r, "criticality": rng.choice(INVALID_CRITICALITIES)},   # invalid criticality
        lambda r: {**r, "criticality": rng.choice(CRITICALITY_VARIANTS)},    # variant criticality (many will normalize)
        lambda r: {**r, "event_time": "32/13/2024 99:99:99"},               # invalid date
        lambda r: {**r, "event_time": format_datetime(                        # alternative date format
            random_datetime(datetime(2024, 1, 1), 720), rng.randint(1, 4))},
        lambda r: {**r, "priority": "HIGH"},                                  # priority as text
        lambda r: {**r, "tag": f"  {r['tag']}  "},                          # whitespace in tag
        lambda r: {**r, "message": None, "criticality": None},               # multiple nulls
        lambda r: {**r,                                                       # ack_time before event_time
            "ack_time": format_datetime(
                datetime.fromisoformat(r["event_time"][:19] if "T" in r["event_time"] else r["event_time"])
                - timedelta(hours=2), 0
            ) if r.get("event_time") and r["event_time"] else r["ack_time"]
        },
        lambda r: {**r, "state": "UNKNOWN_STATE"},                           # unexpected state
        lambda r: {**r, "source_system": None},                              # null source
    ]

    # Generate ~200 erroneous records
    n_errors = max(int(len(records) * 0.10), 50)
    for i in range(n_errors):
        base = rng.choice(records)
        fn = rng.choice(error_pool)
        try:
            errored.append(fn(dict(base)))
        except Exception:
            errored.append({**base, "tag": ""})  # safe fallback

    # Add ~30 exact duplicates
    for _ in range(30):
        errored.append(dict(rng.choice(records)))

    return errored


def main(size: int = 2000, seed: int = 42) -> None:
    rng = random.Random(seed)
    base_dt = datetime(2024, 6, 1, 0, 0, 0)

    print(f"Generating {size} valid records + error records (seed={seed})...")

    valid_records = [generate_valid_record(rng, base_dt, i) for i in range(1, size + 1)]
    error_records = inject_errors(valid_records, rng)
    all_records = valid_records + error_records
    rng.shuffle(all_records)

    # Normalize None to empty string for CSV compatibility
    for r in all_records:
        for k, v in r.items():
            if v is None:
                r[k] = ""

    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV
    import csv
    csv_path = output_dir / "alarms_dataset.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)
    print(f"CSV written: {csv_path} ({len(all_records)} rows)")

    # Write JSON
    json_path = output_dir / "alarms_dataset.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2, default=str)
    print(f"JSON written: {json_path} ({len(all_records)} rows)")

    print(
        f"\nSummary:\n"
        f"  Valid records:   {len(valid_records)}\n"
        f"  Error records:   {len(error_records)}\n"
        f"  Duplicates:      ~30\n"
        f"  Total:           {len(all_records)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic SCADA alarm dataset")
    parser.add_argument("--size", type=int, default=2000, help="Number of valid records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    main(size=args.size, seed=args.seed)
