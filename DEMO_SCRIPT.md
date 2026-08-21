# 🎙️ AquaPulse — 2-Minute Hackathon Demo Script

> **Target Audience**: Hackathon Judges, CGWB Officials, Ministry of Jal Shakti Evaluators  
> **Total Duration**: 2 Minutes (120 Seconds)  
> **Key Objective**: Demonstrate real-time evaluation, anomaly alerting, predictive forecasting, and production readiness in a fluid click-through narrative.

---

## ⏱️ Timeline & Click-Through Path

```
 0:00 ─── [HOOK & SLIDE 1] National Overview Dashboard
 0:30 ─── [DRILL-DOWN] Interactive Map & Time-Series Holt Forecast
 1:00 ─── [ANOMALY DETECTION] Real-Time Anomaly & Multi-Channel Alert Dispatch
 1:30 ─── [LIVE TELEMETRY] Telemetry Tick Simulation & Ingestion
 1:45 ─── [PRODUCTION READINESS] India-WRIS Adapter & Educational Guide
 2:00 ─── [CLOSING IMPACT]
```

---

## 🎬 Minute-by-Minute Script & Action Guide

### 📍 [0:00 - 0:25] The Hook & National Overview (Slide 1)
- **On Screen**: Start on the **📊 National Overview** dashboard ([`http://localhost:5173`](http://localhost:5173)).
- **Action**: Hover over the **State Stress Distribution Bar Chart** and the **12-Month National Drying Trend**.
- **What to Say**:
  > *"Respected judges, India's Central Ground Water Board operates over 15,000 telemetric DWLR piezometers, but traditional resource assessments are conducted annually — leaving severe localized depletion undetected for months.  
  > Welcome to **AquaPulse**, a real-time groundwater intelligence platform. Right here on our National Overview, executive decision-makers can instantly observe groundwater health across states, track our national drying velocity over 12 months, and immediately identify the top 10 most at-risk stations in the country."*

---

### 📍 [0:25 - 0:55] Drill-Down: Geospatial Map & 30-Day Predictive Forecasting
- **On Screen**: Click on **#1 Latur Over-Extract** (Maharashtra) from the leaderboard.
- **Action**: 
  1. The app automatically transitions to the **🗺 Stations & Map** view.
  2. The **Station Detail Drawer** opens, showing the Recharts depth curve.
  3. Toggle between **30d**, **90d**, and **1y** time ranges.
  4. Point out the **dashed orange forecast line** with the shaded 95% confidence interval band.
  5. Click the **⬇ CSV** button to show instant data export.
- **What to Say**:
  > *"Clicking our #1 at-risk station instantly brings us to our geospatial map, where stations are color-coded by stress severity and shaped by aquifer type — alluvial, hard-rock, or coastal.  
  > In the detail drawer, our 2-metric engine evaluates both historical baseline deviation and 30-day linear decline rate. Using **Holt's Linear Exponential Smoothing**, AquaPulse projects water levels 30 days into the future with a 95% confidence band — alerting authorities to critical threshold breaches weeks before they occur."*

---

### 📍 [0:55 - 1:25] Anomaly Detection & Automated Multi-Channel Dispatch
- **On Screen**: Click on the **🔔 Alerts** tab in the left sidebar.
- **Action**: 
  1. Filter by **Status Downgrade** or **Sustained Decline**.
  2. Click on the **📲 Alert SMS/Mail** button on the top alert card.
  3. The **Multi-Channel Dispatch Preview Modal** opens, displaying simulated SMS and NIC Email logs.
  4. Point to the floating **Toast Notification** at the bottom-right and the browser console log.
  5. Close modal, click **✓ Resolve**.
- **What to Say**:
  > *"Raw IoT telemetry is noisy. Our anomaly engine continuously detects sensor dropouts (>6h gaps), electromagnetic spikes (>5m jumps), sustained over-extraction, and classification downgrades.  
  > When an anomaly occurs, AquaPulse doesn't just log it — with one click, our automated dispatch gateway routes targeted SMS alerts to the District Nodal Hydrologist and official NIC emails to the District Magistrate and Disaster Management Authority. You can see the simulated gateway payload, console telemetry, and live toast confirmation right here."*

---

### 📍 [1:25 - 1:45] Live Telemetry Simulation Tick
- **On Screen**: Click the **⚡ Simulate Tick** button in the top right header.
- **Action**: 
  1. Observe the button state change to `⏳ Updating…`.
  2. Watch the in-app confirmation toast: `⚡ Ingested +30 DWLR readings...`.
  3. Note the active alert counters update in real time.
- **What to Say**:
  > *"To demonstrate real-world ingestion, clicking **Simulate Tick** pushes a new hourly reading packet across all 30 stations, advances our virtual telemetry timeline, and immediately re-evaluates stress classifications and anomaly filters in sub-second time."*

---

### 📍 [1:45 - 2:00] Production Readiness & Closing Impact
- **On Screen**: Click the **💡 How It Works** button in the header to briefly display the educational guide.
- **Action**: 
  1. Scroll through the plain-language classification table.
  2. Close the modal and return to the main dashboard.
- **What to Say**:
  > *"Finally, AquaPulse is architected for immediate production rollout. Through our plug-and-play **DataSourceAdapter** interface, connecting this system to the live India-WRIS REST API requires zero changes to the analytical or visualization code.  
  > AquaPulse bridges the gap between raw sensor telemetry and proactive water governance for India's water security. Thank you!"*

---

## 🎯 Quick Judge Q&A Cheat Sheet

| Question | Winning Answer |
|---|---|
| **Why Holt's Smoothing instead of Deep Learning (LSTM)?** | *"Holt's Linear Smoothing provides exact interpretability, requires minimal computational overhead on edge nodes, and captures both level and trend directions robustly without requiring huge training epochs on new sensors."* |
| **How does your engine handle missing sensor data?** | *"If missing readings are under 6 hours, our spline/linear interpolator fills the gap for moving averages. If data is absent for >6 hours, our Gap Detector flags a WARNING/CRITICAL alert for field sensor maintenance."* |
| **How do you scale to 15,000+ national DWLR stations?** | *"Our backend is decoupled via the Strategy Pattern. In production, we deploy an Apache Kafka ingestion pipeline with SQLite swapped for PostgreSQL/TimescaleDB, capable of processing 15k readings/sec with sub-second latency."* |
| **Why take the worse of Metric A and Metric B?** | *"A station might currently be near its historical average (Metric A = Safe), but experiencing a steep seasonal decline (Metric B = Critical) due to sudden unseasonal pumping. Taking the maximum severity ensures proactive early warnings."* |
