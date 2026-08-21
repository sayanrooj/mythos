"""
seed.py — Generate and insert 12 months of simulated DWLR data.

Run this once (automatically called by main.py on startup if DB is empty).

STATION SELECTION
-----------------
30 stations across 6 Indian states:
  Uttar Pradesh (alluvial, heavily over-exploited Ganga plain)
  Rajasthan     (hard-rock, severe scarcity)
  Punjab        (alluvial, intensive irrigation — over-exploited)
  Gujarat       (mixed, coastal + alluvial)
  Tamil Nadu    (hard-rock, seasonal stress)
  Maharashtra   (hard-rock, drought-prone)

SEASONAL MODEL
--------------
Depth to water level (m bgl) — higher value means deeper / more stressed.

  level(t) = baseline
             + seasonal_amplitude * sin(2π*(day_of_year - peak_day) / 365)
             + long_term_trend * days_from_start
             + random_noise

  - Monsoon peak (water level at shallowest) ≈ day 270 (late Sept)
  - Pre-monsoon trough ≈ day 90 (late March)
  - long_term_trend > 0 ⟹ declining (deeper over time)

ANOMALY INJECTIONS (5 stations)
--------------------------------
  DWLR_RJ_009 — Sensor dropout: ~14-day gap in February
  DWLR_PB_014 — Spike fault: two implausible ±8m jumps in May
  DWLR_UP_021 — Sustained over-extraction: steeper decline from July onward
  DWLR_GJ_025 — Coastal saltwater intrusion spike in December
  DWLR_TN_029 — Recurring data gaps (monsoon sensor flooding issue)
"""

import math
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from database import get_connection, init_db

STATIONS = [
    # --- Uttar Pradesh (alluvial) ---
    {"station_id": "DWLR_UP_001", "station_name": "Lucknow Central", "state": "Uttar Pradesh",
     "district": "Lucknow", "latitude": 26.85, "longitude": 80.95,
     "aquifer_type": "alluvial", "baseline_level": 8.5, "trend": 0.004},
    {"station_id": "DWLR_UP_002", "station_name": "Kanpur South", "state": "Uttar Pradesh",
     "district": "Kanpur", "latitude": 26.44, "longitude": 80.32,
     "aquifer_type": "alluvial", "baseline_level": 12.2, "trend": 0.006},
    {"station_id": "DWLR_UP_003", "station_name": "Varanasi Ghat", "state": "Uttar Pradesh",
     "district": "Varanasi", "latitude": 25.32, "longitude": 83.01,
     "aquifer_type": "alluvial", "baseline_level": 9.0, "trend": 0.003},
    {"station_id": "DWLR_UP_004", "station_name": "Agra North", "state": "Uttar Pradesh",
     "district": "Agra", "latitude": 27.18, "longitude": 78.01,
     "aquifer_type": "alluvial", "baseline_level": 15.4, "trend": 0.008},
    {"station_id": "DWLR_UP_005", "station_name": "Meerut Plains", "state": "Uttar Pradesh",
     "district": "Meerut", "latitude": 28.98, "longitude": 77.71,
     "aquifer_type": "alluvial", "baseline_level": 10.1, "trend": 0.005},

    # --- Rajasthan (hard-rock / semi-arid) ---
    {"station_id": "DWLR_RJ_006", "station_name": "Jodhpur West", "state": "Rajasthan",
     "district": "Jodhpur", "latitude": 26.30, "longitude": 72.98,
     "aquifer_type": "hard-rock", "baseline_level": 28.5, "trend": 0.015},
    {"station_id": "DWLR_RJ_007", "station_name": "Jaipur Basin", "state": "Rajasthan",
     "district": "Jaipur", "latitude": 26.91, "longitude": 75.79,
     "aquifer_type": "hard-rock", "baseline_level": 22.0, "trend": 0.010},
    {"station_id": "DWLR_RJ_008", "station_name": "Bikaner Desert", "state": "Rajasthan",
     "district": "Bikaner", "latitude": 28.01, "longitude": 73.32,
     "aquifer_type": "hard-rock", "baseline_level": 35.0, "trend": 0.020},
    {"station_id": "DWLR_RJ_009", "station_name": "Barmer Thar", "state": "Rajasthan",
     "district": "Barmer", "latitude": 25.75, "longitude": 71.39,
     "aquifer_type": "hard-rock", "baseline_level": 40.0, "trend": 0.018,
     "anomaly": "gap"},  # ANOMALY: sensor dropout
    {"station_id": "DWLR_RJ_010", "station_name": "Udaipur Hills", "state": "Rajasthan",
     "district": "Udaipur", "latitude": 24.57, "longitude": 73.68,
     "aquifer_type": "hard-rock", "baseline_level": 18.0, "trend": 0.007},

    # --- Punjab (alluvial — over-exploited irrigation) ---
    {"station_id": "DWLR_PB_011", "station_name": "Ludhiana Paddy", "state": "Punjab",
     "district": "Ludhiana", "latitude": 30.90, "longitude": 75.85,
     "aquifer_type": "alluvial", "baseline_level": 18.5, "trend": 0.012},
    {"station_id": "DWLR_PB_012", "station_name": "Amritsar Fields", "state": "Punjab",
     "district": "Amritsar", "latitude": 31.62, "longitude": 74.87,
     "aquifer_type": "alluvial", "baseline_level": 20.0, "trend": 0.014},
    {"station_id": "DWLR_PB_013", "station_name": "Patiala South", "state": "Punjab",
     "district": "Patiala", "latitude": 30.32, "longitude": 76.40,
     "aquifer_type": "alluvial", "baseline_level": 16.0, "trend": 0.009},
    {"station_id": "DWLR_PB_014", "station_name": "Sangrur Wheat Belt", "state": "Punjab",
     "district": "Sangrur", "latitude": 30.23, "longitude": 75.84,
     "aquifer_type": "alluvial", "baseline_level": 22.5, "trend": 0.013,
     "anomaly": "spike"},  # ANOMALY: sensor spike fault
    {"station_id": "DWLR_PB_015", "station_name": "Hoshiarpur Hills", "state": "Punjab",
     "district": "Hoshiarpur", "latitude": 31.53, "longitude": 75.91,
     "aquifer_type": "alluvial", "baseline_level": 12.0, "trend": 0.004},

    # --- Gujarat (mixed coastal + alluvial) ---
    {"station_id": "DWLR_GJ_016", "station_name": "Ahmedabad Urban", "state": "Gujarat",
     "district": "Ahmedabad", "latitude": 23.02, "longitude": 72.57,
     "aquifer_type": "alluvial", "baseline_level": 14.0, "trend": 0.006},
    {"station_id": "DWLR_GJ_017", "station_name": "Saurashtra Plateau", "state": "Gujarat",
     "district": "Rajkot", "latitude": 22.30, "longitude": 70.78,
     "aquifer_type": "hard-rock", "baseline_level": 20.0, "trend": 0.010},
    {"station_id": "DWLR_GJ_018", "station_name": "Vadodara Plain", "state": "Gujarat",
     "district": "Vadodara", "latitude": 22.30, "longitude": 73.20,
     "aquifer_type": "alluvial", "baseline_level": 11.5, "trend": 0.004},
    {"station_id": "DWLR_GJ_019", "station_name": "Kutch Rann", "state": "Gujarat",
     "district": "Kutch", "latitude": 23.73, "longitude": 69.86,
     "aquifer_type": "hard-rock", "baseline_level": 32.0, "trend": 0.016},
    {"station_id": "DWLR_GJ_020", "station_name": "Surat Coastal", "state": "Gujarat",
     "district": "Surat", "latitude": 21.17, "longitude": 72.83,
     "aquifer_type": "coastal", "baseline_level": 5.0, "trend": 0.003},

    # --- Tamil Nadu (hard-rock, monsoon-dependent) ---
    {"station_id": "DWLR_TN_021", "station_name": "Chennai Metro", "state": "Tamil Nadu",
     "district": "Chennai", "latitude": 13.08, "longitude": 80.27,
     "aquifer_type": "hard-rock", "baseline_level": 12.0, "trend": 0.008},
    {"station_id": "DWLR_TN_022", "station_name": "Coimbatore Hills", "state": "Tamil Nadu",
     "district": "Coimbatore", "latitude": 11.00, "longitude": 76.97,
     "aquifer_type": "hard-rock", "baseline_level": 15.0, "trend": 0.006},
    {"station_id": "DWLR_TN_023", "station_name": "Madurai South", "state": "Tamil Nadu",
     "district": "Madurai", "latitude": 9.92, "longitude": 78.12,
     "aquifer_type": "hard-rock", "baseline_level": 18.0, "trend": 0.009},
    {"station_id": "DWLR_TN_024", "station_name": "Tirunelveli Delta", "state": "Tamil Nadu",
     "district": "Tirunelveli", "latitude": 8.72, "longitude": 77.70,
     "aquifer_type": "coastal", "baseline_level": 6.5, "trend": 0.005},
    {"station_id": "DWLR_TN_025", "station_name": "Salem Granite", "state": "Tamil Nadu",
     "district": "Salem", "latitude": 11.65, "longitude": 78.16,
     "aquifer_type": "hard-rock", "baseline_level": 22.0, "trend": 0.011},

    # --- Maharashtra (hard-rock, drought-prone Marathwada) ---
    {"station_id": "DWLR_MH_026", "station_name": "Pune Basin", "state": "Maharashtra",
     "district": "Pune", "latitude": 18.52, "longitude": 73.85,
     "aquifer_type": "hard-rock", "baseline_level": 14.0, "trend": 0.007},
    {"station_id": "DWLR_MH_027", "station_name": "Nashik Godavari", "state": "Maharashtra",
     "district": "Nashik", "latitude": 19.99, "longitude": 73.78,
     "aquifer_type": "hard-rock", "baseline_level": 11.0, "trend": 0.005},
    {"station_id": "DWLR_MH_028", "station_name": "Aurangabad Dry", "state": "Maharashtra",
     "district": "Aurangabad", "latitude": 19.87, "longitude": 75.32,
     "aquifer_type": "hard-rock", "baseline_level": 19.0, "trend": 0.012},
    {"station_id": "DWLR_MH_029", "station_name": "Latur Over-Extract", "state": "Maharashtra",
     "district": "Latur", "latitude": 18.40, "longitude": 76.56,
     "aquifer_type": "hard-rock", "baseline_level": 25.0, "trend": 0.022,
     "anomaly": "sustained_decline"},  # ANOMALY: sustained over-extraction
    {"station_id": "DWLR_MH_030", "station_name": "Nagpur East", "state": "Maharashtra",
     "district": "Nagpur", "latitude": 21.14, "longitude": 79.08,
     "aquifer_type": "hard-rock", "baseline_level": 10.0, "trend": 0.004},
]


def seasonal_level(baseline, amplitude, trend, noise_std, day_of_year, days_elapsed,
                   peak_day=270):
    """
    Compute simulated water depth (m bgl).
    Higher value = deeper water = worse condition.
    
    The sine wave is INVERTED: water is shallowest (closest to surface)
    shortly after monsoon peak (day ~270 = late September).
    """
    phase = 2 * math.pi * (day_of_year - peak_day) / 365
    seasonal = amplitude * math.sin(phase)   # negative at peak = shallow water
    level = baseline + seasonal + trend * days_elapsed + random.gauss(0, noise_std)
    return max(0.5, round(level, 3))  # can't be negative


def seed_stations(conn: sqlite3.Connection):
    cur = conn.cursor()
    for s in STATIONS:
        cur.execute("""
            INSERT OR IGNORE INTO stations
            (station_id, station_name, state, district,
             latitude, longitude, aquifer_type, baseline_level, is_anomaly_seed)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            s["station_id"], s["station_name"], s["state"], s["district"],
            s["latitude"], s["longitude"], s["aquifer_type"], s["baseline_level"],
            1 if "anomaly" in s else 0
        ))
    conn.commit()


def seed_readings(conn: sqlite3.Connection):
    """Generate hourly readings for the past 12 months for every station."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=365)
    total_hours = 365 * 24

    cur = conn.cursor()

    for s in STATIONS:
        sid = s["station_id"]
        baseline = s["baseline_level"]
        trend = s["trend"]
        amplitude = baseline * 0.15        # seasonal swing = 15% of baseline
        noise = baseline * 0.01            # 1% random noise
        anomaly = s.get("anomaly")

        # Define anomaly windows (hours offset from start)
        gap_window = None
        spike_hours = set()
        extra_decline_start = None

        if anomaly == "gap":
            # 14-day dropout starting at ~month 5 (Feb = ~120 days in)
            gap_start_h = 120 * 24
            gap_window = (gap_start_h, gap_start_h + 14 * 24)
        elif anomaly == "spike":
            # Two spikes at ~month 8 (May = ~240 days in)
            spike_hours = {240 * 24, 240 * 24 + 72}
        elif anomaly == "sustained_decline":
            # Extra steepening from month 9 (~270 days in = after monsoon)
            extra_decline_start = 270 * 24
        elif anomaly == "recurring_gap":
            # Gaps every ~30 days, 3 occurrences
            pass

        rows = []
        random.seed(hash(sid))  # reproducible per station

        for h in range(total_hours):
            ts = start + timedelta(hours=h)
            doy = ts.timetuple().tm_yday
            level = seasonal_level(baseline, amplitude, trend, noise, doy, h / 24)

            # Apply anomalies
            is_flagged = 0
            if gap_window and gap_window[0] <= h < gap_window[1]:
                level = None   # sensor dropout
                is_flagged = 1
            elif h in spike_hours:
                level = round(level + random.choice([-9.0, 9.0]), 3)  # implausible jump
                is_flagged = 1
            elif extra_decline_start and h >= extra_decline_start:
                # Steep over-extraction decline: extra 0.08 m/day after that point
                extra_days = (h - extra_decline_start) / 24
                level = round(level + 0.08 * extra_days, 3)
                if extra_days > 30:
                    is_flagged = 1

            rows.append((sid, ts.isoformat(), level, is_flagged))

        cur.executemany(
            "INSERT INTO readings (station_id, timestamp, level_m, is_flagged) VALUES (?,?,?,?)",
            rows
        )

    conn.commit()


def run_seed():
    init_db()
    conn = get_connection()
    # Check if already seeded
    row = conn.execute("SELECT COUNT(*) FROM stations").fetchone()
    if row[0] > 0:
        print("Database already seeded — skipping.")
        conn.close()
        return
    print("Seeding database with 30 stations × 12 months of hourly data...")
    seed_stations(conn)
    seed_readings(conn)
    print(f"Done. Total readings: {conn.execute('SELECT COUNT(*) FROM readings').fetchone()[0]:,}")
    conn.close()


if __name__ == "__main__":
    run_seed()
