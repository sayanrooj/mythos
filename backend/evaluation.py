"""
evaluation.py — Core groundwater stress evaluation engine for AquaPulse

CLASSIFICATION RULES (document for hackathon judges)
=====================================================

We classify each station into one of four stress levels based on TWO metrics,
taking the worse of the two:

  Metric A: Current level vs. 12-month rolling average (m bgl deviation)
  -----------------------------------------------------------------------
  Safe           : current <= avg + 2 m
  Semi-Critical  : avg + 2 m < current <= avg + 5 m
  Critical       : avg + 5 m < current <= avg + 10 m
  Over-Exploited : current > avg + 10 m

  Metric B: 30-day rate of decline (m/day, positive = worsening)
  --------------------------------------------------------------
  Safe           : rate <= 0.010 m/day
  Semi-Critical  : 0.010 < rate <= 0.030 m/day
  Critical       : 0.030 < rate <= 0.060 m/day
  Over-Exploited : rate > 0.060 m/day

  Final status = MAX severity of Metric A and Metric B.

Note: "depth to water level in m bgl" — HIGHER value = DEEPER = WORSE.
A positive deviation means the water table has dropped below its average.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import sqlite3
from database import get_connection

STRESS_ORDER = ["safe", "semi-critical", "critical", "over-exploited"]

# --- Metric A thresholds (m bgl deviation above 12-month avg) ---
LEVEL_THRESHOLDS = [
    (2.0, "safe"),
    (5.0, "semi-critical"),
    (10.0, "critical"),
    (float("inf"), "over-exploited"),
]

# --- Metric B thresholds (m/day decline rate) ---
RATE_THRESHOLDS = [
    (0.010, "safe"),
    (0.030, "semi-critical"),
    (0.060, "critical"),
    (float("inf"), "over-exploited"),
]


def _classify_by_value(value: float, thresholds: list) -> str:
    for limit, label in thresholds:
        if value <= limit:
            return label
    return "over-exploited"


def _worse(a: str, b: str) -> str:
    ia = STRESS_ORDER.index(a) if a in STRESS_ORDER else 0
    ib = STRESS_ORDER.index(b) if b in STRESS_ORDER else 0
    return STRESS_ORDER[max(ia, ib)]


def get_station_status(station_id: str, conn: Optional[sqlite3.Connection] = None) -> dict:
    """
    Compute rolling averages, decline rate, and stress classification
    for a single station.

    Returns:
      {
        station_id, latest_level, avg_30d, avg_365d,
        deviation_from_avg, decline_rate_m_per_day,
        stress_level, metric_a, metric_b
      }
    """
    _own_conn = conn is None
    if _own_conn:
        conn = get_connection()

    try:
        now = datetime.now(timezone.utc)
        cutoff_30d = (now - timedelta(days=30)).isoformat()
        cutoff_365d = (now - timedelta(days=365)).isoformat()

        rows_365 = conn.execute("""
            SELECT timestamp, level_m FROM readings
            WHERE station_id=? AND timestamp >= ? AND level_m IS NOT NULL
            ORDER BY timestamp
        """, (station_id, cutoff_365d)).fetchall()

        if not rows_365:
            return {"station_id": station_id, "stress_level": "unknown",
                    "error": "No data available"}

        levels_365 = [r["level_m"] for r in rows_365]
        avg_365 = sum(levels_365) / len(levels_365)

        # Last 30 days
        rows_30 = [r for r in rows_365 if r["timestamp"] >= cutoff_30d]
        levels_30 = [r["level_m"] for r in rows_30] if rows_30 else levels_365[-720:]
        avg_30 = sum(levels_30) / len(levels_30)

        # Latest non-null reading
        latest_row = conn.execute("""
            SELECT level_m, timestamp FROM readings
            WHERE station_id=? AND level_m IS NOT NULL
            ORDER BY timestamp DESC LIMIT 1
        """, (station_id,)).fetchone()

        if not latest_row:
            return {"station_id": station_id, "stress_level": "unknown",
                    "error": "No valid readings"}

        latest_level = latest_row["level_m"]
        latest_ts = latest_row["timestamp"]

        # Metric A: deviation from 365-day avg
        deviation = latest_level - avg_365

        # Metric B: 30-day linear decline rate using simple least squares
        decline_rate = _compute_decline_rate(rows_30)

        metric_a = _classify_by_value(max(0, deviation), LEVEL_THRESHOLDS)
        metric_b = _classify_by_value(max(0, decline_rate), RATE_THRESHOLDS)
        stress_level = _worse(metric_a, metric_b)

        return {
            "station_id": station_id,
            "latest_level": round(latest_level, 3),
            "latest_timestamp": latest_ts,
            "avg_30d": round(avg_30, 3),
            "avg_365d": round(avg_365, 3),
            "deviation_from_avg": round(deviation, 3),
            "decline_rate_m_per_day": round(decline_rate, 5),
            "stress_level": stress_level,
            "metric_a": metric_a,
            "metric_b": metric_b,
        }
    finally:
        if _own_conn:
            conn.close()


def _compute_decline_rate(rows: list) -> float:
    """
    Simple linear regression slope (m/day) for a list of {timestamp, level_m} rows.
    Positive value = levels increasing (deepening = worsening).
    """
    if len(rows) < 2:
        return 0.0

    # Convert timestamps to fractional days from first point
    t0_str = rows[0]["timestamp"]
    t0 = datetime.fromisoformat(t0_str.replace("Z", "+00:00"))

    xs, ys = [], []
    for r in rows:
        ts = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
        xs.append((ts - t0).total_seconds() / 86400)
        ys.append(r["level_m"])

    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    return num / den if den else 0.0


def get_all_station_statuses(conn: Optional[sqlite3.Connection] = None) -> list:
    """Return status dicts for all stations."""
    _own_conn = conn is None
    if _own_conn:
        conn = get_connection()
    try:
        station_ids = [r["station_id"] for r in
                       conn.execute("SELECT station_id FROM stations").fetchall()]
        return [get_station_status(sid, conn) for sid in station_ids]
    finally:
        if _own_conn:
            conn.close()
