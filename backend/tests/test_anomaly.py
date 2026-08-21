"""
Tests for anomaly.py — gap, spike, and sustained decline detection.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlite3
import pytest
from datetime import datetime, timedelta, timezone

from anomaly import (
    detect_gaps,
    detect_spikes,
    detect_sustained_decline,
    detect_downgrades,
    GAP_HOURS,
    SPIKE_THRESHOLD_M,
    DECLINE_RATE_THRESHOLD,
)


def _make_anomaly_db(readings: list[tuple]) -> sqlite3.Connection:
    """
    readings: list of (timestamp_str, level_or_None)
    Creates in-memory DB with single station TEST_001.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE stations (
            station_id TEXT PRIMARY KEY, station_name TEXT, state TEXT,
            district TEXT, latitude REAL, longitude REAL,
            aquifer_type TEXT, baseline_level REAL, is_anomaly_seed INTEGER DEFAULT 0
        );
        CREATE TABLE readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT, timestamp TEXT, level_m REAL, is_flagged INTEGER DEFAULT 0
        );
        CREATE INDEX idx_r ON readings(station_id, timestamp);
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT, alert_type TEXT, severity TEXT,
            reason TEXT, timestamp TEXT, resolved INTEGER DEFAULT 0
        );
    """)
    conn.execute("""
        INSERT INTO stations VALUES ('TEST_001','Test','TS','TD',12.0,77.0,'alluvial',10.0,0)
    """)
    for ts, lvl in readings:
        conn.execute(
            "INSERT INTO readings (station_id, timestamp, level_m) VALUES (?,?,?)",
            ("TEST_001", ts, lvl)
        )
    conn.commit()
    return conn


def _make_timestamps(n: int, start_hours_ago: int = 200) -> list[str]:
    now = datetime.now(timezone.utc)
    return [
        (now - timedelta(hours=start_hours_ago - i)).isoformat()
        for i in range(n)
    ]


class TestGapDetection:
    def test_no_gap_no_alert(self):
        ts = _make_timestamps(20)
        readings = [(t, 10.0) for t in ts]
        conn = _make_anomaly_db(readings)
        count = detect_gaps("TEST_001", conn)
        assert count == 0

    def test_short_gap_no_alert(self):
        ts = _make_timestamps(20)
        readings = [(t, 10.0 if i not in (5, 6, 7) else None) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_gaps("TEST_001", conn)
        assert count == 0  # only 3 hours, below GAP_HOURS=6

    def test_gap_triggers_alert(self):
        ts = _make_timestamps(30)
        gap_indices = set(range(5, 5 + GAP_HOURS + 1))  # 7+ consecutive nulls
        readings = [(t, None if i in gap_indices else 10.0) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_gaps("TEST_001", conn)
        assert count >= 1
        alerts = conn.execute("SELECT * FROM alerts WHERE alert_type='GAP'").fetchall()
        assert len(alerts) >= 1
        assert "gap" in alerts[0]["reason"].lower()

    def test_exact_boundary_gap(self):
        # Exactly GAP_HOURS nulls (= threshold) should trigger
        ts = _make_timestamps(GAP_HOURS + 10)
        gap_indices = set(range(2, 2 + GAP_HOURS))
        readings = [(t, None if i in gap_indices else 10.0) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_gaps("TEST_001", conn)
        assert count >= 1


class TestSpikeDetection:
    def test_normal_readings_no_spike(self):
        ts = _make_timestamps(50)
        readings = [(t, 10.0 + 0.1 * (i % 3)) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_spikes("TEST_001", conn)
        assert count == 0

    def test_spike_triggers_alert(self):
        ts = _make_timestamps(20)
        # Insert a spike at position 10: jump of 8m
        readings = [(t, 10.0) for t in ts]
        readings = list(readings)
        readings[10] = (ts[10], 10.0 + SPIKE_THRESHOLD_M + 1)
        conn = _make_anomaly_db(readings)
        count = detect_spikes("TEST_001", conn)
        assert count >= 1
        alerts = conn.execute("SELECT * FROM alerts WHERE alert_type='SPIKE'").fetchall()
        assert len(alerts) >= 1
        assert "spike" in alerts[0]["reason"].lower()

    def test_negative_spike(self):
        # A sudden drop (sensor reads implausibly shallow)
        ts = _make_timestamps(20)
        readings = [(t, 15.0) for t in ts]
        readings = list(readings)
        readings[10] = (ts[10], 15.0 - SPIKE_THRESHOLD_M - 2)  # sudden rise
        conn = _make_anomaly_db(readings)
        count = detect_spikes("TEST_001", conn)
        assert count >= 1

    def test_just_below_threshold_no_alert(self):
        ts = _make_timestamps(20)
        readings = [(t, 10.0) for t in ts]
        readings = list(readings)
        # Exactly at threshold but not exceeding
        readings[10] = (ts[10], 10.0 + SPIKE_THRESHOLD_M)
        conn = _make_anomaly_db(readings)
        count = detect_spikes("TEST_001", conn)
        # delta == threshold should NOT trigger (strict >)
        assert count == 0


class TestSustainedDeclineDetection:
    def test_flat_series_no_alert(self):
        ts = _make_timestamps(200)
        readings = [(t, 10.0) for t in ts]
        conn = _make_anomaly_db(readings)
        count = detect_sustained_decline("TEST_001", conn)
        assert count == 0

    def test_steep_decline_triggers_alert(self):
        # 0.15 m/day decline — well above 0.05 threshold
        ts = _make_timestamps(200)
        readings = [(t, 10.0 + 0.15 * i / 24) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_sustained_decline("TEST_001", conn)
        assert count >= 1
        alerts = conn.execute(
            "SELECT * FROM alerts WHERE alert_type='SUSTAINED_DECLINE'"
        ).fetchall()
        assert len(alerts) >= 1
        assert "decline" in alerts[0]["reason"].lower()

    def test_mild_decline_no_alert(self):
        # 0.005 m/day — well below threshold
        ts = _make_timestamps(200)
        readings = [(t, 10.0 + 0.005 * i / 24) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_sustained_decline("TEST_001", conn)
        assert count == 0


class TestDowngradeDetection:
    def test_safe_station_no_downgrade(self):
        ts = _make_timestamps(100)
        readings = [(t, 10.0) for t in ts]
        conn = _make_anomaly_db(readings)
        count = detect_downgrades("TEST_001", conn)
        assert count == 0

    def test_critical_level_triggers_downgrade(self):
        # Reading is 18m vs baseline 10m (+8m deviation -> critical)
        ts = _make_timestamps(100)
        readings = [(t, 10.0 if i < 90 else 18.0) for i, t in enumerate(ts)]
        conn = _make_anomaly_db(readings)
        count = detect_downgrades("TEST_001", conn)
        assert count == 1
        alert = conn.execute("SELECT * FROM alerts WHERE alert_type='STATUS_DOWNGRADE'").fetchone()
        assert alert is not None
        assert alert["severity"] == "CRITICAL"
        assert "OVER-EXPLOITED" in alert["reason"] or "CRITICAL" in alert["reason"]

