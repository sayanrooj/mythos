"""
anomaly.py — Anomaly detection engine for AquaPulse

Three anomaly types are detected:

  1. GAP          — any window > 6 consecutive hours of NULL readings
                    (sensor dropout, communication failure)
                    Severity: WARNING

  2. SPIKE        — single-reading jump |Δlevel| > SPIKE_THRESHOLD_M (default 5 m)
                    (sensor fault, electromagnetic interference, data error)
                    Severity: WARNING

  3. SUSTAINED_DECLINE — 7-day rolling slope > DECLINE_RATE_THRESHOLD (default 0.05 m/day)
                         sustained for at least MIN_SUSTAINED_DAYS days
                         (over-extraction event)
                         Severity: CRITICAL

Each anomaly generates an alert record saved to the `alerts` table.
Re-running detection will not duplicate alerts that already exist
for the same (station, type, approximate timestamp window).
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional
from database import get_connection

# --- Configurable thresholds ---
GAP_HOURS = 6                   # consecutive null hours that trigger a gap alert
SPIKE_THRESHOLD_M = 5.0         # single-hour delta (m bgl) that triggers a spike alert
DECLINE_RATE_THRESHOLD = 0.05   # m/day — 7-day slope above this triggers decline alert
MIN_SUSTAINED_HOURS = 7 * 24    # 7 days to confirm sustained decline


def _insert_alert(cur: sqlite3.Cursor, station_id, alert_type, severity, reason, timestamp):
    """Insert alert only if no unresolved alert of same type for this station within 48h."""
    window_start = (
        datetime.fromisoformat(timestamp.replace("Z", "+00:00")) - timedelta(hours=48)
    ).isoformat()
    existing = cur.execute("""
        SELECT id FROM alerts
        WHERE station_id=? AND alert_type=? AND resolved=0 AND timestamp >= ?
    """, (station_id, alert_type, window_start)).fetchone()
    if not existing:
        cur.execute("""
            INSERT INTO alerts (station_id, alert_type, severity, reason, timestamp)
            VALUES (?,?,?,?,?)
        """, (station_id, alert_type, severity, reason, timestamp))


def detect_gaps(station_id: str, conn: sqlite3.Connection) -> int:
    """Detect data gaps > GAP_HOURS. Returns number of new alerts inserted."""
    rows = conn.execute("""
        SELECT timestamp, level_m FROM readings
        WHERE station_id=? ORDER BY timestamp
    """, (station_id,)).fetchall()

    cur = conn.cursor()
    count = 0
    gap_start = None
    gap_count = 0

    for r in rows:
        if r["level_m"] is None:
            if gap_start is None:
                gap_start = r["timestamp"]
            gap_count += 1
        else:
            if gap_count >= GAP_HOURS:
                reason = (
                    f"Data gap detected: {gap_count} consecutive hours of missing readings "
                    f"starting at {gap_start}. Possible sensor dropout or telemetry failure."
                )
                _insert_alert(cur, station_id, "GAP", "WARNING", reason, gap_start)
                count += 1
            gap_start = None
            gap_count = 0

    # Handle gap extending to end of data
    if gap_count >= GAP_HOURS and gap_start:
        reason = (
            f"Ongoing data gap: {gap_count} consecutive hours of missing readings "
            f"starting at {gap_start}. Station may be offline."
        )
        _insert_alert(cur, station_id, "GAP", "CRITICAL", reason, gap_start)
        count += 1

    conn.commit()
    return count


def detect_spikes(station_id: str, conn: sqlite3.Connection) -> int:
    """Detect implausible single-reading jumps. Returns number of new alerts."""
    rows = conn.execute("""
        SELECT timestamp, level_m FROM readings
        WHERE station_id=? AND level_m IS NOT NULL ORDER BY timestamp
    """, (station_id,)).fetchall()

    cur = conn.cursor()
    count = 0
    prev_level = None

    for r in rows:
        lvl = r["level_m"]
        if prev_level is not None:
            delta = abs(lvl - prev_level)
            if delta > SPIKE_THRESHOLD_M:
                direction = "rise" if lvl < prev_level else "drop"
                reason = (
                    f"Implausible spike detected at {r['timestamp']}: "
                    f"level changed by {delta:.2f} m ({direction}) in a single hour. "
                    f"Previous={prev_level:.2f} m bgl, Current={lvl:.2f} m bgl. "
                    f"Likely sensor fault or data transmission error."
                )
                _insert_alert(cur, station_id, "SPIKE", "WARNING", reason, r["timestamp"])
                count += 1
        prev_level = lvl

    conn.commit()
    return count


def detect_sustained_decline(station_id: str, conn: sqlite3.Connection) -> int:
    """
    Detect sustained over-extraction decline using a rolling 7-day slope.
    Returns number of new alerts.
    """
    rows = conn.execute("""
        SELECT timestamp, level_m FROM readings
        WHERE station_id=? AND level_m IS NOT NULL ORDER BY timestamp
    """, (station_id,)).fetchall()

    if len(rows) < MIN_SUSTAINED_HOURS:
        return 0

    cur = conn.cursor()
    count = 0
    window = MIN_SUSTAINED_HOURS  # 168 readings = 7 days of hourly data

    for i in range(window, len(rows), 24):  # stride by 1 day
        segment = rows[i - window:i]
        t0 = datetime.fromisoformat(segment[0]["timestamp"].replace("Z", "+00:00"))

        xs, ys = [], []
        for r in segment:
            ts = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            xs.append((ts - t0).total_seconds() / 86400)
            ys.append(r["level_m"])

        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den = sum((x - mean_x) ** 2 for x in xs)
        slope = num / den if den else 0.0

        if slope > DECLINE_RATE_THRESHOLD:
            ts_str = segment[-1]["timestamp"]
            reason = (
                f"Sustained decline detected ending at {ts_str}: "
                f"7-day average decline rate = {slope:.4f} m/day "
                f"(threshold: {DECLINE_RATE_THRESHOLD} m/day). "
                f"Possible over-extraction or aquifer depletion event."
            )
            _insert_alert(cur, station_id, "SUSTAINED_DECLINE", "CRITICAL", reason, ts_str)
            count += 1

    conn.commit()
    return count


def detect_downgrades(station_id: str, conn: sqlite3.Connection) -> int:
    """
    Detect stress level downgrade (Safe -> Semi-Critical, Critical, Over-Exploited).
    Returns number of new alerts.
    """
    from evaluation import get_station_status
    status = get_station_status(station_id, conn)
    stress = status.get("stress_level", "safe")
    if stress in ("semi-critical", "critical", "over-exploited"):
        cur = conn.cursor()
        severity = "CRITICAL" if stress in ("critical", "over-exploited") else "WARNING"
        ts = status.get("latest_timestamp") or datetime.now(timezone.utc).isoformat()
        dev = status.get("deviation_from_avg", 0)
        rate = status.get("decline_rate_m_per_day", 0)
        reason = (
            f"Classification downgrade alert: Station assessed as {stress.upper()} "
            f"(Deviation: {dev:+.2f} m vs 12m avg, 30-day decline: {rate:.4f} m/day). "
            f"Groundwater resource threshold exceeded."
        )
        _insert_alert(cur, station_id, "STATUS_DOWNGRADE", severity, reason, ts)
        conn.commit()
        return 1
    return 0


def run_detection_all(conn: Optional[sqlite3.Connection] = None) -> dict:
    """Run all anomaly detectors for every station. Returns summary dict."""
    _own = conn is None
    if _own:
        conn = get_connection()
    try:
        stations = [r["station_id"] for r in
                    conn.execute("SELECT station_id FROM stations").fetchall()]
        summary = {"gaps": 0, "spikes": 0, "declines": 0, "downgrades": 0, "total": 0}
        for sid in stations:
            summary["gaps"] += detect_gaps(sid, conn)
            summary["spikes"] += detect_spikes(sid, conn)
            summary["declines"] += detect_sustained_decline(sid, conn)
            summary["downgrades"] += detect_downgrades(sid, conn)
        summary["total"] = (
            summary["gaps"] + summary["spikes"] + summary["declines"] + summary["downgrades"]
        )
        return summary
    finally:
        if _own:
            conn.close()

