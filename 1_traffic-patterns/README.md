# Project 1 — Bus Passenger Load Along Singapore's NEL Corridor

**APIs · Geospatial Analysis · EDA · Data Storytelling**

---

## Research Question

> *How does bus passenger load vary on weekdays in the north-eastern corridor of Singapore, specifically at the Kovan–Serangoon–Woodleigh region, and what does the concentration of that load suggest about bus-rail integration as stated in LTMP 2040?*

---

## Overview

This project uses real-time public transport data from Singapore's LTA DataMall API to analyse weekday bus passenger volumes at 63 bus stops in the NEL corridor during May 2026. The analysis is framed against Singapore's [Land Transport Master Plan 2040](https://www.lta.gov.sg/content/ltagov/en/who_we_are/our_work/land_transport_master_plan_2040.html) Walk-Cycle-Ride goals, identifying potential bus-rail integration gaps through peak-period demand patterns.

---

## Key Findings

- Identified the top-5 highest-volume bus stops in the corridor and characterised their peak-hour load profiles
- Directional flow analysis (tap-in vs tap-out) revealed asymmetric demand patterns consistent with commuter rail-feeder behaviour
- Boxplot analysis across all 63 corridor stops surfaced three high-volume outliers, all at Serangoon (Stn Exit C/Blk 201, Stn Exit E and Serangoon Interchange), with comparatively little load at Kovan or Woodleigh
- The lowest-volume stops sit 240–840m from Serangoon MRT while the top 5 are at station exits, suggesting load concentration is driven by direct rail-transfer function rather than proximity alone

---

## Methods & Tools

| Step | Approach |
|---|---|
| Data acquisition | LTA DataMall Bus Stops API (paginated via `$skip`, 5,205 rows) + Passenger Volume API (S3 download, May 2026) |
| Geospatial filtering | OneMap API for NEL station coordinates; rectilinear bounding box → 1,278 rows, 63 unique bus stops |
| Analysis | Weekday-only filter; merged on `BusStopCode`/`PT_CODE`; EDA with four distinct Matplotlib/Seaborn plots |
| Mapping | Folium interactive map of the top-5 and bottom-5 stops plus the three MRT stations (CartoDB Voyager, CircleMarkers, HeatMap layer), shown side by side with Plot 1 |

**Libraries:** `pandas`, `requests`, `folium`, `matplotlib`, `seaborn`, `python-dotenv`

---

## Data

Data is sourced live from the LTA DataMall API. To replicate:

1. Register for a free API key at [datamall.lta.gov.sg](https://datamall.lta.gov.sg)
2. Register for a free OneMap account at [www.onemap.gov.sg](https://www.onemap.gov.sg) (the notebook requests an access token with your account email and password)
3. Create a `.env` file in this directory:
   ```
   LTA_ACCOUNT_KEY=your_key_here
   ONEMAP_EMAIL=your_email_here
   ONEMAP_PASSWORD=your_password_here
   ```

> ⚠️ Never commit your API keys or passwords. `.env` files are listed in `.gitignore`.

---

## Notebook

`Project 1 - Traffic Patterns.ipynb` — Run top-to-bottom after setting up API keys. All plots render inline.

A published HTML version of this notebook is available at [mikeee.co](https://www.mikeee.co).
