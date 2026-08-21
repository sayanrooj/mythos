"""
Tests for evaluation.py — classification rules and decline rate computation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlite3
import pytest
from datetime import datetime, timedelta, timezone

from evaluation import (
    _classify_by_value,
    _worse,
    _compute_decline_rate,
    LEVEL_THRESHOLDS,
    RATE_THRESHOLDS,
    STRESS_ORDER,
    get_station_status,
)
from database import init_db, get_connection


# ── Unit tests for classification helpers ──────────────────────────────────────

class TestClassifyByValue:
    def test_safe_level(self):
        assert _classify_by_value(1.5, LEVEL_THRESHOLDS) == "safe"

    def test_semi_critical_level(self):
        assert _classify_by_value(3.0, LEVEL_THRESHOLDS) == "semi-critical"

    def test_critical_level(self):
        assert _classify_by_value(7.5, LEVEL_THRESHOLDS) == "critical"

    def test_over_exploited_level(self):
        assert _classify_by_value(15.0, LEVEL_THRESHOLDS) == "over-exploited"

    def test_boundary_safe_semi(self):
        # Exactly at boundary → safe
        assert _classify_by_value(2.0, LEVEL_THRESHOLDS) == "safe"

    def test_boundary_semi_critical(self):
        assert _classify_by_value(5.0, LEVEL_THRESHOLDS) == "semi-critical"

    def test_boundary_critical_over(self):
        assert _classify_by_value(10.0, LEVEL_THRESHOLDS) == "critical"


class TestClassifyByRate:
    def test_safe_rate(self):
        assert _classify_by_value(0.005, RATE_THRESHOLDS) == "safe"

    def test_semi_critical_rate(self):
        assert _classify_by_value(0.020, RATE_THRESHOLDS) == "semi-critical"

    def test_critical_rate(self):
        assert _classify_by_value(0.045, RATE_THRESHOLDS) == "critical"

    def test_over_exploited_rate(self):
        assert _classify_by_value(0.090, RATE_THRESHOLDS) == "over-exploited"


class TestWorseClassification:
    def test_same_level(self):
        assert _worse("safe", "safe") == "safe"

    def test_takes_worse(self):
        assert _worse("safe", "critical") == "critical"
        assert _worse("over-exploited", "safe") == "over-exploited"
        assert _worse("semi-critical", "critical") == "critical"

    def test_order(self):
        levels = ["safe", "semi-critical", "critical", "over-exploited"]
        for i, a in enumerate(levels):
            for j, b in enumerate(levels):
                result = _worse(a, b)
                assert result == levels[max(i, j)]


# ── Integration test: get_station_status with in-memory DB ────────────────────

def _make_test_db(station_level_series: list[float]) -> sqlite3.Connection:
    """Create an in-memory DB with one station and the given daily level series."""
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
        INSERT INTO stations VALUES ('TEST_001','Test Station','TestState',
        'TestDistrict',12.0,77.0,'alluvial',10.0,0)
    """)

    now = datetime.now(timezone.utc)
    for i, level in enumerate(station_level_series):
        ts = (now - timedelta(hours=len(station_level_series) - i)).isoformat()
        conn.execute(
            "INSERT INTO readings (station_id, timestamp, level_m) VALUES (?,?,?)",
            ("TEST_001", ts, level)
        )
    conn.commit()
    return conn


class TestGetStationStatus:
    def test_safe_station(self):
        # Flat series around baseline 10 → should be safe
        levels = [10.0 + 0.1 * (i % 3) for i in range(400)]
        conn = _make_test_db(levels)
        result = get_station_status("TEST_001", conn)
        assert result["stress_level"] in ("safe", "semi-critical")

    def test_over_exploited_level_deviation(self):
        # Current level is 15m above (worse than) the historical avg of 10
        base = [10.0] * 350
        steep = [22.0] * 50   # recent readings are 12 m deeper than avg
        conn = _make_test_db(base + steep)
        result = get_station_status("TEST_001", conn)
        assert result["stress_level"] in ("critical", "over-exploited")

    def test_decline_rate_triggers(self):
        # Steadily declining: 0.1 m/day = well above 0.06 threshold
        levels = [10.0 + 0.1 * i / 24 for i in range(400)]
        conn = _make_test_db(levels)
        result = get_station_status("TEST_001", conn)
        assert result["decline_rate_m_per_day"] > 0

    def test_returns_required_keys(self):
        levels = [10.0] * 400
        conn = _make_test_db(levels)
        result = get_station_status("TEST_001", conn)
        required = ["latest_level", "avg_30d", "avg_365d",
                    "deviation_from_avg", "decline_rate_m_per_day",
                    "stress_level", "metric_a", "metric_b"]
        for key in required:
            assert key in result, f"Missing key: {key}"


class TestDeclineRate:
    def test_flat_series(self):
        from datetime import timezone
        rows = []
        now = datetime.now(timezone.utc)
        for i in range(100):
            ts = (now - timedelta(hours=100 - i)).isoformat()
            rows.append({"timestamp": ts, "level_m": 10.0})
        rate = _compute_decline_rate(rows)
        assert abs(rate) < 0.001

    def test_increasing_series(self):
        # 0.1 m/day increase
        rows = []
        now = datetime.now(timezone.utc)
        for i in range(240):
            ts = (now - timedelta(hours=240 - i)).isoformat()
            level = 10.0 + (i / 24) * 0.1
            rows.append({"timestamp": ts, "level_m": level})
        rate = _compute_decline_rate(rows)
        assert 0.09 <= rate <= 0.11  # ~0.1 m/day
