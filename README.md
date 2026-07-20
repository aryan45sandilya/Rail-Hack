<div align="center">

# 🚂 RailHack

### Indian Railways Waitlist Confirmation Predictor

[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML_Model-FF6600?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PC9zdmc+&logoColor=white)](https://xgboost.readthedocs.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)

[![GitHub](https://img.shields.io/badge/GitHub-aryan45sandilya-181717?style=for-the-badge&logo=github)](https://github.com/aryan45sandilya/Rail-Hack)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](https://github.com/aryan45sandilya/Rail-Hack/pulls)

<br/>

> **Enter your IRCTC waitlist ticket details → Get instant confirmation probability powered by XGBoost ML**

<br/>

![RailHack Demo](https://img.shields.io/badge/Status-Live-27ae60?style=flat-square&logo=railway) &nbsp;
![Model Accuracy](https://img.shields.io/badge/Model_Accuracy-99%25-f5a623?style=flat-square) &nbsp;
![Routes](https://img.shields.io/badge/Routes-60%2B-blue?style=flat-square) &nbsp;
![Trains](https://img.shields.io/badge/Trains-200%2B-purple?style=flat-square)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎰 **Split-Flap Animation** | Mechanical departure board digit animation for probability display |
| 🎫 **Ticket Card UI** | Physical Indian railway ticket aesthetic with perforated design |
| 📊 **Route Explorer** | Historical WL clearance rates by route, class, quota & month |
| 🔢 **PNR Status** | Simulated PNR lookup with passenger-wise WL/RAC/CNF status |
| 🤖 **XGBoost ML** | Trained on 8,000+ historical ticket records across 60+ routes |
| ⚡ **Redis Caching** | 1-hour prediction cache for repeated queries |
| 🗄️ **PostgreSQL** | Full relational DB with trains, routes, tickets & WL snapshots |

---

## 🏗️ Architecture

```
┌──────────────┐     HTTP/Proxy      ┌─────────────────┐
│   React +    │ ─────────────────►  │  FastAPI        │
│   Vite       │                     │  (Port 8000)    │
│  (Port 3001) │                     └────────┬────────┘
└──────────────┘                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                               ┌────▼────┐        ┌─────▼───┐
                               │ SQLite  │        │  Redis  │
                               │  / PG   │        │  Cache  │
                               └─────────┘        └─────────┘
                                    │
                               ┌────▼────────────┐
                               │  XGBoost Model  │
                               │  railhack.pkl   │
                               └─────────────────┘
```

---

## 🧠 ML Model — Features Used

```python
features = [
    "initial_wl",            # Waitlist number at booking
    "quota_encoded",         # GN=0, TQ=1, LD=2, SS=3
    "class_encoded",         # SL=0, 3A=1, 2A=2, 1A=3
    "days_to_departure",     # Days between booking & journey
    "is_festival_season",    # Oct/Nov/Dec = 1
    "wl_movement_rate",      # initial_wl - wl_24hr_before
    "route_avg_confirm_rate",# Historical avg for this route
    "train_cancellation_rate",
    "journey_distance_km",
    "day_of_week",
    "month"
]
# Target: confirmed (1) / not confirmed (0)
```

---

## 📁 Project Structure

```
Rail-Hack/
├── 📂 backend/
│   ├── main.py                 # FastAPI app + CORS + routers
│   ├── Dockerfile              # Backend container
│   ├── entrypoint.sh           # Auto seed + train on startup
│   ├── requirements.txt
│   ├── 📂 db/
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── seed.py             # 60+ routes, 200+ trains, 8000 tickets
│   ├── 📂 model/
│   │   ├── train.py            # XGBoost training script
│   │   └── predict.py          # Prediction engine + fallback
│   └── 📂 routes/
│       ├── predict.py          # POST /api/predict
│       ├── stats.py            # GET /api/routes & /trains
│       └── pnr.py              # GET /api/pnr/:pnr
├── 📂 src/
│   ├── App.tsx                 # Router + nav + loading state
│   ├── 📂 pages/
│   │   ├── Home.tsx            # Input form
│   │   ├── Result.tsx          # Split-flap + verdict + factors
│   │   ├── Explorer.tsx        # Route stats + bar chart
│   │   └── PNRStatus.tsx       # PNR passenger status
│   └── 📂 components/
│       ├── SplitFlapNumber.tsx # Mechanical digit animation
│       ├── TicketCard.tsx      # Physical ticket UI
│       └── VerdictBadge.tsx    # Likely/Borderline/Unlikely pill
├── Dockerfile                  # Frontend container
├── docker-compose.yml          # Full stack local setup
├── server.ts                   # Express dev server + API fallback
└── vite.config.ts              # Vite + Tailwind + API proxy
```

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)
```bash
git clone https://github.com/aryan45sandilya/Rail-Hack.git
cd Rail-Hack
docker-compose up --build
```
Opens at `http://localhost:3000`

### Option 2 — Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

cd db && python seed.py        # Seed 60+ routes + 8000 tickets
cd ../model && python train.py # Train XGBoost model
cd ..
uvicorn main:app --port 8000 --reload
```

**Frontend:**
```bash
# In project root
npm install
npm run dev                    # http://localhost:3001
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Get WL confirmation probability |
| `GET` | `/api/routes/{src}/{dst}/stats` | Route historical stats |
| `GET` | `/api/routes/{src}/{dst}/trains` | Top trains for route |
| `GET` | `/api/trains/{number}/stats` | Train-level stats |
| `GET` | `/api/pnr/{pnr}` | Simulated PNR status |
| `GET` | `/api/health` | Health check |

### Sample Request
```json
POST /api/predict
{
  "train_number": "12951",
  "source": "NDLS",
  "destination": "MMCT",
  "quota": "GN",
  "coach_class": "3A",
  "initial_wl": 45,
  "journey_date": "2026-08-15",
  "booked_at": "2026-07-01T10:00:00"
}
```

### Sample Response
```json
{
  "confirmation_probability": 73.4,
  "verdict": "likely",
  "confidence": "high",
  "top_factors": [
    { "factor": "Low Waitlist Position (WL-45)", "impact": "positive" },
    { "factor": "General (GN) Quota", "impact": "positive" },
    { "factor": "AC Coach Class (3A)", "impact": "positive" }
  ]
}
```

---

## 🗄️ Database Schema

```sql
trains      → id, train_number, train_name, train_type
routes      → id, source_station, dest_station, distance_km, avg_confirm_rate
tickets     → id, train_id, route_id, quota, coach_class, initial_wl, confirmed, journey_date
wl_snapshots→ id, ticket_id, wl_number, hours_to_departure, recorded_at
predictions → id, ticket_id, probability, model_version, predicted_at
```

---

## 🚢 Deployment

| Service | Platform |
|---------|----------|
| Frontend | [Vercel](https://vercel.com) |
| Backend | [Railway](https://railway.app) |
| Database | Railway PostgreSQL |
| Cache | Railway Redis |

---

## ⚠️ Disclaimer

> This project uses **synthetic training data** generated from realistic statistical models. Predictions are for **educational/demonstration purposes only** and do not reflect official IRCTC data. Always check [irctc.co.in](https://irctc.co.in) for actual PNR status.

---

<div align="center">

Made with ❤️ for Indian Railways enthusiasts

[![GitHub stars](https://img.shields.io/github/stars/aryan45sandilya/Rail-Hack?style=social)](https://github.com/aryan45sandilya/Rail-Hack/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/aryan45sandilya/Rail-Hack?style=social)](https://github.com/aryan45sandilya/Rail-Hack/network/members)

</div>
