"""
main.py — AquaPulse Flask backend (Python 3.14 compatible)

REST API Endpoints:
  GET  /                                 — health check + active data source info
  GET  /stations                         — list all stations with latest status + aggregate summary
  GET  /stations/<id>                    — single station metadata
  GET  /stations/<id>/readings           — time series (query: start, end, limit, aggregate)
  GET  /stations/<id>/status             — stress classification + rolling averages
  GET  /stations/<id>/forecast           — 30-day water level projection
  GET  /stations/<id>/export/csv         — download historical + forecast as CSV
  GET  /alerts                           — active alerts, newest first
  PUT  /alerts/<id>/resolve              — mark alert as resolved
  POST /simulate/tick                    — advance telemetry by one hour for all stations
  GET  /data-source                      — show active adapter + swap instructions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import csv
import io
import json
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, abort, Response, send_file
from flask_cors import CORS

from database import get_connection, init_db
from seed import run_seed
from evaluation import get_station_status, get_all_station_statuses
from anomaly import run_detection_all
from forecasting import forecast_station
from simulator import tick
from data_source import get_data_source, _ADAPTERS

app = Flask(__name__)
CORS(app)

# Active data source (set DATA_SOURCE env var to switch)
_data_source = get_data_source()

# ── Startup: seed + anomaly detection on first run ─────────────────────────────
with app.app_context():
    init_db()
    run_seed()
    run_detection_all()


# ── Helpers ────────────────────────────────────────────────────────────────────

def success(data):
    return jsonify(data)


def error(msg, code=400):
    return jsonify({"error": msg}), code


def get_station_or_404(station_id, conn):
    row = conn.execute(
        "SELECT * FROM stations WHERE station_id=?", (station_id,)
    ).fetchone()
    if not row:
        abort(404, description=f"Station '{station_id}' not found")
    return dict(row)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    active = os.environ.get("DATA_SOURCE", "simulated")
    return success({
        "status": "ok",
        "service": "AquaPulse API",
        "version": "1.0.0",
        "data_source": active,
        "available_adapters": list(_ADAPTERS.keys()),
    })


@app.get("/stations")
def list_stations():
    """List all DWLR stations with latest status, stress level, and aggregate summary."""
    conn = get_connection()
    try:
        stations = [dict(r) for r in conn.execute("SELECT * FROM stations").fetchall()]
        statuses = {s["station_id"]: s for s in get_all_station_statuses(conn)}

        for st in stations:
            sid = st["station_id"]
            status = statuses.get(sid, {})
            st["latest_level"]           = status.get("latest_level")
            st["latest_timestamp"]       = status.get("latest_timestamp")
            st["stress_level"]           = status.get("stress_level", "unknown")
            st["avg_30d"]                = status.get("avg_30d")
            st["avg_365d"]               = status.get("avg_365d")
            st["decline_rate_m_per_day"] = status.get("decline_rate_m_per_day")

        total = len(stations)
        counts = {}
        for st in stations:
            lvl = st.get("stress_level", "unknown")
            counts[lvl] = counts.get(lvl, 0) + 1

        total_alerts = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE resolved=0"
        ).fetchone()[0]

        return success({
            "stations": stations,
            "summary": {
                "total_stations": total,
                "stress_counts": counts,
                "active_alerts": total_alerts,
            }
        })
    finally:
        conn.close()


@app.get("/stations/<station_id>")
def get_station(station_id):
    conn = get_connection()
    try:
        return success(get_station_or_404(station_id, conn))
    finally:
        conn.close()


@app.get("/stations/<station_id>/readings")
def get_readings(station_id):
    """
    Time-series readings for a station.
    Query params: start (ISO), end (ISO), limit (int), aggregate (hourly|daily|weekly)
    """
    conn = get_connection()
    try:
        get_station_or_404(station_id, conn)

        start     = request.args.get("start",
                      (datetime.now(timezone.utc) - timedelta(days=90)).isoformat())
        end       = request.args.get("end",
                      datetime.now(timezone.utc).isoformat())
        limit     = min(int(request.args.get("limit", 2000)), 50000)
        aggregate = request.args.get("aggregate", "daily")

        rows = conn.execute("""
            SELECT timestamp, level_m, is_flagged
            FROM readings
            WHERE station_id=? AND timestamp BETWEEN ? AND ?
              AND level_m IS NOT NULL
            ORDER BY timestamp
            LIMIT ?
        """, (station_id, start, end, limit * 24)).fetchall()

        data = [{"timestamp": r["timestamp"], "level_m": r["level_m"],
                 "is_flagged": bool(r["is_flagged"])} for r in rows]

        if aggregate in ("daily", "weekly"):
            days_per = 1 if aggregate == "daily" else 7
            buckets = {}
            for d in data:
                dt = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
                since = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).days
                bk = str(since // days_per * days_per)
                buckets.setdefault(bk, []).append(d["level_m"])
            aggregated = []
            for bk in sorted(buckets, key=lambda x: int(x)):
                vals = buckets[bk]
                dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(days=int(bk) * days_per)
                aggregated.append({
                    "timestamp": dt.isoformat(),
                    "level_m": round(sum(vals) / len(vals), 3),
                    "is_flagged": False,
                })
            data = aggregated[:limit]
        else:
            data = data[:limit]

        return success({"station_id": station_id, "count": len(data), "readings": data})
    finally:
        conn.close()


@app.get("/stations/<station_id>/status")
def get_status(station_id):
    conn = get_connection()
    try:
        get_station_or_404(station_id, conn)
        return success(get_station_status(station_id, conn))
    finally:
        conn.close()


@app.get("/stations/<station_id>/forecast")
def get_forecast(station_id):
    conn = get_connection()
    try:
        get_station_or_404(station_id, conn)
        return success(forecast_station(station_id, conn))
    finally:
        conn.close()


@app.get("/alerts")
def get_alerts():
    conn = get_connection()
    try:
        resolved   = request.args.get("resolved", "false").lower() == "true"
        station_id = request.args.get("station_id")
        limit      = min(int(request.args.get("limit", 100)), 500)

        query = """
            SELECT a.*, s.station_name, s.state, s.district
            FROM alerts a
            JOIN stations s ON a.station_id = s.station_id
            WHERE a.resolved = ?
        """
        params = [int(resolved)]
        if station_id:
            query += " AND a.station_id = ?"
            params.append(station_id)
        query += " ORDER BY a.timestamp DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        alerts = [dict(r) for r in rows]

        total_active = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE resolved=0"
        ).fetchone()[0]

        return success({"total_active": total_active, "count": len(alerts), "alerts": alerts})
    finally:
        conn.close()


@app.put("/alerts/<int:alert_id>/resolve")
def resolve_alert(alert_id):
    conn = get_connection()
    try:
        conn.execute("UPDATE alerts SET resolved=1 WHERE id=?", (alert_id,))
        conn.commit()
        return success({"status": "resolved", "alert_id": alert_id})
    finally:
        conn.close()


@app.post("/alerts/<int:alert_id>/dispatch")
def dispatch_alert(alert_id):
    """
    Simulate automated multi-channel dispatch (SMS + Email) to district/state nodal officers.
    Logs realistic notification messages to server logs and returns dispatch confirmation.
    """
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT a.*, s.station_name, s.state, s.district, s.aquifer_type
            FROM alerts a
            JOIN stations s ON a.station_id = s.station_id
            WHERE a.id = ?
        """, (alert_id,)).fetchone()

        if not row:
            abort(404, description=f"Alert #{alert_id} not found")

        alert = dict(row)
        now_str = datetime.now(timezone.utc).isoformat()
        state_clean = alert["state"].lower().replace(" ", "")
        dist_clean = alert["district"].lower().replace(" ", "")

        # Target contacts
        sms_phone = "+91 94140 " + str(10000 + (alert["id"] * 73) % 90000)
        sms_officer = f"District Nodal Hydrologist ({alert['district']})"
        sms_text = (
            f"[CGWB-AQUAPULSE] {alert['severity']} ALERT for {alert['station_name']} "
            f"({alert['district']}, {alert['state']}): {alert['alert_type']} detected. "
            f"Level: {alert['reason'][:90]}... Immediate verification required."
        )

        email_to = f"cgwb.{state_clean}@nic.in, dm.{dist_clean}@nic.in"
        email_subject = f"[{alert['severity']} ALERT] CGWB Telemetry: {alert['station_name']} ({alert['alert_type']})"
        email_body = (
            f"Respected Authorities,\n\n"
            f"An automated groundwater telemetry alert has been generated by the AquaPulse CGWB Monitoring System.\n\n"
            f"STATION DETAILS:\n"
            f"* Station: {alert['station_name']} ({alert['station_id']})\n"
            f"* State/District: {alert['state']} / {alert['district']}\n"
            f"* Aquifer: {alert['aquifer_type']}\n"
            f"* Alert Type: {alert['alert_type']}\n"
            f"* Severity: {alert['severity']}\n"
            f"* Triggered At: {alert['timestamp']}\n\n"
            f"REASON:\n{alert['reason']}\n\n"
            f"RECOMMENDED ACTION:\n"
            f"Deploy block-level inspection team to verify piezometer sensor calibration and investigate localized extraction spikes.\n\n"
            f"-- Central Ground Water Board (CGWB) Telemetry Directorate"
        )

        # Server-side console logging for demo visibility (ASCII safe for Windows console)
        print("\n=======================================================")
        print(f"[AQUAPULSE DISPATCH] Alert #{alert['id']} -> Multi-Channel Dispatch")
        print(f"[SMS] -> {sms_phone} ({sms_officer})")
        print(f"      Message: {sms_text}")
        print(f"[EMAIL] -> {email_to}")
        print(f"        Subject: {email_subject}")
        print("=======================================================\n")

        return success({
            "status": "dispatched",
            "alert_id": alert["id"],
            "station_id": alert["station_id"],
            "station_name": alert["station_name"],
            "dispatched_at": now_str,
            "channels": ["SMS (Govt. SMS Gateway)", "Email (NIC Portal)"],
            "sms": {
                "recipient": f"{sms_officer} [{sms_phone}]",
                "message": sms_text,
            },
            "email": {
                "to": email_to,
                "subject": email_subject,
                "body_preview": email_body[:180] + "...",
            }
        })
    finally:
        conn.close()



@app.post("/simulate/tick")
def simulate_tick():
    conn = get_connection()
    try:
        return success(tick(conn))
    finally:
        conn.close()


@app.get("/stations/<station_id>/export/csv")
def export_csv(station_id):
    """
    Download historical readings + 30-day forecast as a single CSV file.

    Columns:
      date, type, level_m_bgl, lower_bound, upper_bound, is_flagged

    type = 'observed' for historical data, 'forecast' for projected values.
    """
    conn = get_connection()
    try:
        station = get_station_or_404(station_id, conn)

        # Historical daily aggregates — last 365 days
        start = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
        end   = datetime.now(timezone.utc).isoformat()

        rows = conn.execute("""
            SELECT timestamp, level_m, is_flagged
            FROM readings
            WHERE station_id=? AND timestamp BETWEEN ? AND ?
              AND level_m IS NOT NULL
            ORDER BY timestamp
        """, (station_id, start, end)).fetchall()

        # Daily aggregate
        buckets = {}
        for r in rows:
            day = r["timestamp"][:10]
            buckets.setdefault(day, []).append(r["level_m"])
        historical = [
            {"date": day, "level_m": round(sum(v)/len(v), 3), "is_flagged": False}
            for day, v in sorted(buckets.items())
        ]

        # 30-day forecast
        fc_data = forecast_station(station_id, conn)
        forecast = fc_data.get("forecast", [])

        # Build CSV in-memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Header block with metadata
        writer.writerow(["# AquaPulse CSV Export"])
        writer.writerow(["# Station", station["station_name"]])
        writer.writerow(["# Station ID", station_id])
        writer.writerow(["# State", station["state"]])
        writer.writerow(["# District", station["district"]])
        writer.writerow(["# Aquifer Type", station["aquifer_type"]])
        writer.writerow(["# Latitude", station["latitude"]])
        writer.writerow(["# Longitude", station["longitude"]])
        writer.writerow(["# Exported", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")])
        writer.writerow(["# Forecasting method: Holt Linear Exponential Smoothing (alpha=0.3, beta=0.1)"])
        writer.writerow([])

        # Data header
        writer.writerow(["date", "type", "level_m_bgl", "lower_bound", "upper_bound", "is_flagged"])

        # Historical rows
        for h in historical:
            writer.writerow([
                h["date"], "observed", h["level_m"], "", "", int(h["is_flagged"])
            ])

        # Forecast rows
        for f in forecast:
            writer.writerow([
                f["date"], "forecast",
                f["predicted_level"], f["lower_bound"], f["upper_bound"], ""
            ])

        csv_bytes = output.getvalue().encode("utf-8")
        filename = f"aquapulse_{station_id}_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            csv_bytes,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    finally:
        conn.close()


@app.get("/data-source")
def data_source_info():
    """
    Returns the active data source adapter and instructions for swapping to live data.
    """
    active = os.environ.get("DATA_SOURCE", "simulated")
    return success({
        "active_adapter": active,
        "available_adapters": list(_ADAPTERS.keys()),
        "how_to_switch": (
            "Set the DATA_SOURCE environment variable before starting the server. "
            "Example: DATA_SOURCE=india_wris python backend/main.py"
        ),
        "india_wris_requirements": {
            "env_vars": ["WRIS_BASE_URL", "WRIS_CLIENT_ID", "WRIS_CLIENT_SECRET"],
            "stub_file": "backend/data_source.py — IndiaWRISAdapter class",
            "api_docs": "https://indiawris.gov.in/wris/#/DataAnalysis",
        },
    })


@app.get("/dashboard/summary")
def dashboard_summary():
    """
    Aggregate data for the national summary dashboard.

    Returns:
      state_stress   — per-state counts of each stress level
      national_trend — daily average water level across all stations (last 365 days)
      at_risk        — top 10 most-at-risk stations this week (scored composite)

    AT-RISK SCORING (higher = more urgent):
      +8  stress_level == 'over-exploited'
      +4  stress_level == 'critical'
      +1  stress_level == 'semi-critical'
      +5  per active CRITICAL alert in the last 7 days
      +2  per active WARNING alert in the last 7 days
      +3  if 7-day decline rate > 0.05 m/day
      +1  if 7-day decline rate > 0.03 m/day
    """
    conn = get_connection()
    try:
        # ── 1. State stress distribution ──────────────────────────────────────
        stations = [dict(r) for r in conn.execute("SELECT * FROM stations").fetchall()]
        statuses = {s["station_id"]: s for s in get_all_station_statuses(conn)}

        # Merge stress onto stations
        for st in stations:
            status = statuses.get(st["station_id"], {})
            st["stress_level"] = status.get("stress_level", "unknown")
            st["decline_rate"] = status.get("decline_rate_m_per_day", 0) or 0
            st["latest_level"] = status.get("latest_level")
            st["avg_365d"]     = status.get("avg_365d")

        stress_levels = ["safe", "semi-critical", "critical", "over-exploited"]
        state_stress: dict[str, dict] = {}
        for st in stations:
            s = st["state"]
            if s not in state_stress:
                state_stress[s] = {lvl: 0 for lvl in stress_levels}
            lvl = st["stress_level"]
            if lvl in stress_levels:
                state_stress[s][lvl] += 1

        state_stress_list = [
            {"state": state, **counts}
            for state, counts in sorted(state_stress.items())
        ]

        # ── 2. National daily trend (365 days) ───────────────────────────────
        cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
        rows = conn.execute("""
            SELECT substr(timestamp, 1, 10) as day,
                   AVG(level_m) as avg_level,
                   COUNT(*) as n
            FROM readings
            WHERE timestamp >= ? AND level_m IS NOT NULL
            GROUP BY day
            ORDER BY day
        """, (cutoff,)).fetchall()

        national_trend = [
            {"date": r["day"], "avg_level_m": round(r["avg_level"], 3)}
            for r in rows
        ]

        # ── 3. At-risk leaderboard (this week) ───────────────────────────────
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

        # Count alerts per station in last 7 days
        alert_rows = conn.execute("""
            SELECT station_id, severity, COUNT(*) as cnt
            FROM alerts
            WHERE timestamp >= ? AND resolved = 0
            GROUP BY station_id, severity
        """, (week_ago,)).fetchall()

        alert_counts: dict[str, dict] = {}
        for r in alert_rows:
            sid = r["station_id"]
            if sid not in alert_counts:
                alert_counts[sid] = {"CRITICAL": 0, "WARNING": 0}
            alert_counts[sid][r["severity"]] = alert_counts[sid].get(r["severity"], 0) + r["cnt"]

        # Score each station
        scored = []
        stress_pts = {
            "over-exploited": 8, "critical": 4, "semi-critical": 1, "safe": 0, "unknown": 0
        }
        for st in stations:
            sid = st["station_id"]
            score = stress_pts.get(st["stress_level"], 0)

            alerts = alert_counts.get(sid, {})
            score += alerts.get("CRITICAL", 0) * 5
            score += alerts.get("WARNING", 0) * 2

            rate = st["decline_rate"]
            if rate > 0.05:
                score += 3
            elif rate > 0.03:
                score += 1

            scored.append({
                "station_id":    sid,
                "station_name":  st["station_name"],
                "state":         st["state"],
                "district":      st["district"],
                "aquifer_type":  st["aquifer_type"],
                "stress_level":  st["stress_level"],
                "latest_level":  st["latest_level"],
                "decline_rate":  round(rate, 5),
                "alerts_critical": alerts.get("CRITICAL", 0),
                "alerts_warning":  alerts.get("WARNING", 0),
                "risk_score":    score,
            })

        at_risk = sorted(scored, key=lambda x: x["risk_score"], reverse=True)[:10]

        return success({
            "state_stress":    state_stress_list,
            "national_trend":  national_trend,
            "at_risk":         at_risk,
            "generated_at":    datetime.now(timezone.utc).isoformat(),
        })
    finally:
        conn.close()


@app.get("/download/pdf")
def download_pdf():
    """
    Direct HTTP endpoint to download the AquaPulse Dossier & Pitch Script PDF.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pdf_path = os.path.join(base_dir, "AquaPulse_Submission_Dossier_and_Pitch.pdf")
    if not os.path.exists(pdf_path):
        abort(404, description="PDF dossier not found. Run generate_pdf.py first.")
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AquaPulse_Submission_Dossier_and_Pitch.pdf"
    )


# ── Error handlers ─────────────────────────────────────────────────────────────


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
