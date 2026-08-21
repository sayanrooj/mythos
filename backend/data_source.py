"""
data_source.py — Data Source Adapter Interface for AquaPulse
=============================================================

PURPOSE
-------
This module defines the DataSourceAdapter abstraction layer that separates
the "how we get data" concern from the rest of the app.

To swap simulated data for the real India-WRIS / CGWB telemetry API,
you only need to implement one class (IndiaWRISAdapter below) and set:

    DATA_SOURCE=india_wris  (environment variable)

Nothing else in the app needs to change.

ADAPTER CONTRACT
----------------
Any adapter must implement four methods:

  list_stations()          → list[dict]   — all station metadata rows
  get_readings(...)        → list[dict]   — time-series readings
  get_latest(station_id)   → dict | None  — most recent reading
  append_reading(...)      → None         — write a new live reading

INDIA-WRIS API NOTES (for the team swapping in the real feed)
--------------------------------------------------------------
The CGWB / India-WRIS telemetry API is documented at:
  https://indiawris.gov.in/wris/#/DataAnalysis

As of 2025, the relevant endpoints are:
  POST /GWLevel/StationDetails  — station metadata
  POST /GWLevel/GetStationData  — hourly water level readings

Authentication: Bearer token via
  POST /auth/realms/wris/protocol/openid-connect/token

Typical response shape for readings:
  {
    "stationCode": "UP001",
    "date": "2024-08-21T10:00:00",
    "wl": 8.43,           ← water level (m bgl)
    "status": "V"         ← V=valid, S=suspect, M=missing
  }

Map these fields to AquaPulse's (station_id, timestamp, level_m) schema
in IndiaWRISAdapter.get_readings() below.
"""

import os
import abc
import sqlite3
from datetime import datetime, timedelta, timezone
from database import get_connection


# ══════════════════════════════════════════════════════════════════════════════
# Abstract Base — the interface every adapter must implement
# ══════════════════════════════════════════════════════════════════════════════

class DataSourceAdapter(abc.ABC):
    """
    Abstract data source adapter.

    Implement this class to connect AquaPulse to any data backend.
    The rest of the application (evaluation, anomaly, API) never imports
    database.py or seed.py directly — they go through this interface.
    """

    @abc.abstractmethod
    def list_stations(self) -> list[dict]:
        """
        Return a list of all DWLR station metadata dicts.

        Required keys per dict:
          station_id (str), station_name (str), state (str), district (str),
          latitude (float), longitude (float), aquifer_type (str),
          baseline_level (float)
        """

    @abc.abstractmethod
    def get_readings(
        self,
        station_id: str,
        start: str,          # ISO-8601 UTC
        end: str,            # ISO-8601 UTC
        limit: int = 2000,
    ) -> list[dict]:
        """
        Return time-series readings for one station in [start, end].

        Required keys per dict:
          timestamp (str, ISO-8601), level_m (float | None), is_flagged (bool)
        """

    @abc.abstractmethod
    def get_latest(self, station_id: str) -> dict | None:
        """
        Return the most recent non-null reading for a station, or None.

        Required keys: timestamp (str), level_m (float)
        """

    @abc.abstractmethod
    def append_reading(
        self,
        station_id: str,
        timestamp: str,      # ISO-8601 UTC
        level_m: float | None,
    ) -> None:
        """
        Persist one new telemetry reading.
        Called by the simulator on each tick, or by the live-feed ingestion loop.
        """


# ══════════════════════════════════════════════════════════════════════════════
# Adapter 1 — Simulated Data (SQLite)  [DEFAULT]
# ══════════════════════════════════════════════════════════════════════════════

class SimulatedDataSource(DataSourceAdapter):
    """
    Reads from the local SQLite database populated by seed.py.
    This is the default adapter used in the prototype.
    """

    def _conn(self) -> sqlite3.Connection:
        return get_connection()

    def list_stations(self) -> list[dict]:
        conn = self._conn()
        try:
            return [dict(r) for r in conn.execute("SELECT * FROM stations").fetchall()]
        finally:
            conn.close()

    def get_readings(
        self,
        station_id: str,
        start: str,
        end: str,
        limit: int = 2000,
    ) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute("""
                SELECT timestamp, level_m, is_flagged
                FROM readings
                WHERE station_id=? AND timestamp BETWEEN ? AND ?
                  AND level_m IS NOT NULL
                ORDER BY timestamp
                LIMIT ?
            """, (station_id, start, end, limit)).fetchall()
            return [
                {
                    "timestamp": r["timestamp"],
                    "level_m": r["level_m"],
                    "is_flagged": bool(r["is_flagged"]),
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_latest(self, station_id: str) -> dict | None:
        conn = self._conn()
        try:
            row = conn.execute("""
                SELECT timestamp, level_m FROM readings
                WHERE station_id=? AND level_m IS NOT NULL
                ORDER BY timestamp DESC LIMIT 1
            """, (station_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def append_reading(self, station_id: str, timestamp: str, level_m: float | None) -> None:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO readings (station_id, timestamp, level_m) VALUES (?,?,?)",
                (station_id, timestamp, level_m),
            )
            conn.commit()
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Adapter 2 — India-WRIS Live Feed  [STUB — implement to go live]
# ══════════════════════════════════════════════════════════════════════════════

class IndiaWRISAdapter(DataSourceAdapter):
    """
    Stub adapter for the real CGWB / India-WRIS telemetry API.

    ┌─────────────────────────────────────────────────────────────────────┐
    │  TO IMPLEMENT: fill in the four methods below, adapting the         │
    │  India-WRIS API responses to AquaPulse's expected dict shapes.      │
    │  See module docstring at the top of this file for API details.      │
    └─────────────────────────────────────────────────────────────────────┘

    Required environment variables:
      WRIS_BASE_URL     e.g. https://indiawris.gov.in/api/2.0
      WRIS_CLIENT_ID    OAuth2 client ID
      WRIS_CLIENT_SECRET OAuth2 client secret
    """

    def __init__(self):
        self.base_url    = os.environ.get("WRIS_BASE_URL", "https://indiawris.gov.in/api/2.0")
        self.client_id   = os.environ.get("WRIS_CLIENT_ID", "")
        self.client_secret = os.environ.get("WRIS_CLIENT_SECRET", "")
        self._token: str | None = None
        self._token_expiry: datetime | None = None

    def _get_token(self) -> str:
        """
        Fetch or refresh the WRIS OAuth2 bearer token.

        TODO: implement using requests.post() to the WRIS token endpoint.
        """
        raise NotImplementedError(
            "IndiaWRISAdapter._get_token: set WRIS_CLIENT_ID and WRIS_CLIENT_SECRET "
            "and implement OAuth2 token fetch."
        )

    def list_stations(self) -> list[dict]:
        """
        TODO: Call POST {base_url}/GWLevel/StationDetails
        Map response fields:
          stationCode  → station_id
          stationName  → station_name
          stateName    → state
          districtName → district
          latitude     → latitude
          longitude    → longitude
          aquiferType  → aquifer_type  ('alluvial' | 'hard-rock' | 'coastal')
          baseLevel    → baseline_level
        """
        raise NotImplementedError("IndiaWRISAdapter.list_stations: not yet implemented")

    def get_readings(self, station_id, start, end, limit=2000) -> list[dict]:
        """
        TODO: Call POST {base_url}/GWLevel/GetStationData
        Request body: { stationCode, fromDate, toDate }
        Map response:
          date   → timestamp (ensure UTC ISO-8601)
          wl     → level_m
          status → is_flagged (True if status == 'S' or status == 'M')
        """
        raise NotImplementedError("IndiaWRISAdapter.get_readings: not yet implemented")

    def get_latest(self, station_id) -> dict | None:
        """
        TODO: Call get_readings with end=now, limit=1, return first result.
        """
        raise NotImplementedError("IndiaWRISAdapter.get_latest: not yet implemented")

    def append_reading(self, station_id, timestamp, level_m) -> None:
        """
        For a live API feed, readings come FROM the API — we don't push TO it.
        Store incoming readings locally for caching/analysis:
        """
        # Cache in local SQLite for analysis without re-fetching
        conn = get_connection()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO readings (station_id, timestamp, level_m) VALUES (?,?,?)",
                (station_id, timestamp, level_m),
            )
            conn.commit()
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Factory — select adapter via DATA_SOURCE environment variable
# ══════════════════════════════════════════════════════════════════════════════

_ADAPTERS = {
    "simulated":   SimulatedDataSource,
    "india_wris":  IndiaWRISAdapter,
}

def get_data_source() -> DataSourceAdapter:
    """
    Return the active data source adapter.

    Set the DATA_SOURCE environment variable to switch:
      DATA_SOURCE=simulated    (default — uses local SQLite seed data)
      DATA_SOURCE=india_wris   (live CGWB telemetry — implement stub first)
    """
    key = os.environ.get("DATA_SOURCE", "simulated").lower()
    cls = _ADAPTERS.get(key)
    if cls is None:
        raise ValueError(
            f"Unknown DATA_SOURCE='{key}'. Choose from: {list(_ADAPTERS.keys())}"
        )
    return cls()


# Singleton — import this in any module that needs data access
data_source: DataSourceAdapter = get_data_source()
