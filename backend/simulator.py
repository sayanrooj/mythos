"""
simulator.py — Live telemetry simulator for AquaPulse

POST /simulate/tick  →  appends one new synthetic hourly reading per station,
advancing the virtual "now" by one hour. Also re-runs anomaly detection.

This mimics the CGWB's hourly DWLR transmission pipeline.
"""

import math
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from database import get_connection
from anomaly import run_detection_all


def _seasonal_level(baseline, amplitude, trend, noise_std, day_of_year, days_elapsed,
                    peak_day=270):
    phase = 2 * math.pi * (day_of_year - peak_day) / 365
    seasonal = amplitude * math.sin(phase)
    level = baseline + seasonal + trend * days_elapsed + random.gauss(0, noise_std)
    return max(0.5, round(level, 3))


def tick(conn: sqlite3.Connection | None = None) -> dict:
    """Append one new reading per station. Returns summary."""
    from seed import STATIONS  # local import to avoid circular at module level

    _own = conn is None
    if _own:
        conn = get_connection()

    try:
        # Find the latest timestamp across all stations
        row = conn.execute(
            "SELECT MAX(timestamp) as latest FROM readings"
        ).fetchone()
        if row["latest"] is None:
            return {"error": "No data — seed first"}

        last_ts = datetime.fromisoformat(row["latest"].replace("Z", "+00:00"))
        new_ts = last_ts + timedelta(hours=1)

        # Days elapsed since data start (approx 365 days ago from first reading)
        first_row = conn.execute("SELECT MIN(timestamp) as t FROM readings").fetchone()
        first_ts = datetime.fromisoformat(first_row["t"].replace("Z", "+00:00"))
        days_elapsed = (new_ts - first_ts).total_seconds() / 86400

        doy = new_ts.timetuple().tm_yday
        ts_str = new_ts.isoformat()

        cur = conn.cursor()
        inserted = 0
        for s in STATIONS:
            sid = s["station_id"]
            baseline = s["baseline_level"]
            trend = s["trend"]
            amplitude = baseline * 0.15
            noise = baseline * 0.01

            # 1% chance of a simulated dropout per tick
            if random.random() < 0.01:
                level = None
            else:
                level = _seasonal_level(baseline, amplitude, trend, noise, doy, days_elapsed)

            cur.execute(
                "INSERT INTO readings (station_id, timestamp, level_m) VALUES (?,?,?)",
                (sid, ts_str, level)
            )
            inserted += 1

        conn.commit()

        # Re-run anomaly detection for new readings only (lightweight)
        anomaly_summary = run_detection_all(conn)

        return {
            "tick_timestamp": ts_str,
            "stations_updated": inserted,
            "new_alerts": anomaly_summary["total"],
        }
    finally:
        if _own:
            conn.close()
