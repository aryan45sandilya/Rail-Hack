import os
import random
import hashlib
import datetime
import pathlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, text

router = APIRouter()

_HERE = pathlib.Path(__file__).parent
_DB_PATH = _HERE.parent / "db" / "railhack.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DB_PATH}")

COACH_PREFIXES = {
    "SL": "S", "3A": "B", "2A": "A", "1A": "H"
}

QUOTA_LABELS = {
    "GN": "General Quota", "TQ": "Tatkal Quota",
    "LD": "Ladies Quota",  "SS": "Senior Citizen Quota"
}

class PassengerStatus(BaseModel):
    passenger_number: int
    coach: str
    berth: Optional[int]
    current_status: str       # WL#12, RAC 4, CNF, etc.
    booking_status: str       # original status at booking
    confirmation_probability: float
    verdict: str              # likely / borderline / unlikely

class PNRResponse(BaseModel):
    pnr: str
    train_number: str
    train_name: str
    source: str
    destination: str
    journey_date: str
    coach_class: str
    quota: str
    distance_km: float
    chart_status: str         # "Chart Prepared" / "Chart Not Prepared"
    passengers: List[PassengerStatus]
    overall_probability: float
    verdict: str
    confidence: str

def _deterministic(pnr: str, salt: str, mod: int) -> int:
    h = hashlib.md5(f"{pnr}{salt}".encode()).hexdigest()
    return int(h[:8], 16) % mod

def _verdict(prob: float):
    if prob >= 65: return "likely", "high" if prob >= 80 else "medium"
    if prob >= 40: return "borderline", "medium"
    return "unlikely", "high" if prob < 20 else "medium"

@router.get("/pnr/{pnr}", response_model=PNRResponse)
def check_pnr(pnr: str):
    if len(pnr) != 10 or not pnr.isdigit():
        raise HTTPException(status_code=400, detail="PNR must be exactly 10 digits.")

    # Try to pull a real ticket from DB for realistic data
    train_number = None
    train_name   = None
    source = dest = None
    distance_km  = 1000.0
    coach_class  = None
    quota        = None
    journey_date_str = None
    route_avg    = 0.70

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            idx = _deterministic(pnr, "ticket_idx", 3000) + 1
            row = conn.execute(text("""
                SELECT tr.train_number, tr.train_name,
                       r.source_station, r.dest_station, r.distance_km, r.avg_confirm_rate,
                       t.coach_class, t.quota, t.journey_date, t.initial_wl
                FROM tickets t
                JOIN trains tr ON t.train_id = tr.id
                JOIN routes r  ON t.route_id = r.id
                WHERE t.id = :idx
                LIMIT 1
            """), {"idx": idx}).fetchone()
            if row:
                train_number, train_name, source, dest, distance_km, route_avg, \
                    coach_class, quota, journey_date_str, _ = row
    except Exception:
        pass

    # Fallbacks if DB not available
    FALLBACK_TRAINS = [
        ("12951", "Mumbai Rajdhani Express",   "NDLS", "MMCT", 1386.0, 0.78),
        ("12301", "Howrah Rajdhani Express",   "NDLS", "HWH",  1447.0, 0.72),
        ("12615", "Grand Trunk Express",       "NDLS", "MAS",  2182.0, 0.65),
        ("12007", "Shatabdi Express",          "SBC",  "MAS",   357.0, 0.85),
        ("12951", "Mumbai Rajdhani Express",   "KOTA", "MMCT",  897.0, 0.74),
        ("12391", "Shramjeevi Express",        "PNBE", "NDLS",  998.0, 0.55),
        ("12555", "Gorakhdham Express",        "GKP",  "NDLS",  730.0, 0.50),
        ("12015", "Ajmer Shatabdi Express",    "NDLS", "JP",    303.0, 0.85),
        ("12559", "Shiv Ganga Express",        "BSB",  "NDLS",  789.0, 0.62),
        ("13049", "Amritsar Express",          "CPR",  "NDLS",  986.0, 0.48),
    ]
    fi = _deterministic(pnr, "fallback", len(FALLBACK_TRAINS))
    if not train_number:
        train_number, train_name, source, dest, distance_km, route_avg = FALLBACK_TRAINS[fi]

    CLASSES = ["SL", "3A", "2A", "1A"]
    QUOTAS  = ["GN", "TQ", "LD", "SS"]
    if not coach_class:
        coach_class = CLASSES[_deterministic(pnr, "class", 4)]
    if not quota:
        quota = QUOTAS[_deterministic(pnr, "quota", 4)]

    # Journey date — 5 to 25 days from today
    if not journey_date_str:
        days_ahead = 5 + _deterministic(pnr, "days", 20)
        jd = datetime.date.today() + datetime.timedelta(days=days_ahead)
        journey_date_str = jd.strftime("%d-%b-%Y")
    else:
        try:
            jd = datetime.date.fromisoformat(str(journey_date_str))
            journey_date_str = jd.strftime("%d-%b-%Y")
        except Exception:
            jd = datetime.date.today() + datetime.timedelta(days=10)
            journey_date_str = jd.strftime("%d-%b-%Y")

    # Chart prepared if journey within 4 hours
    try:
        days_left = (jd - datetime.date.today()).days
    except Exception:
        days_left = 10
    chart_status = "Chart Prepared" if days_left <= 0 else "Chart Not Prepared"

    # Number of passengers: 1–4
    num_pax = 1 + _deterministic(pnr, "pax", 4)
    prefix  = COACH_PREFIXES.get(coach_class, "S")
    coach_num = 1 + _deterministic(pnr, "coach_num", 12)
    coach_label = f"{prefix}{coach_num}"

    passengers = []
    total_prob  = 0.0

    for i in range(num_pax):
        init_wl = 5 + _deterministic(pnr, f"wl{i}", 80)

        # WL movement — simulate decay
        wl_mult = {"SL": 1.5, "3A": 1.0, "2A": 0.7, "1A": 0.4}.get(coach_class, 1.0)
        prob = route_avg
        prob += {"GN": 0.0, "TQ": -0.15, "LD": 0.02, "SS": 0.05}.get(quota, 0)
        prob += {"SL": -0.05, "3A": 0.08, "2A": 0.12, "1A": 0.18}.get(coach_class, 0)
        prob *= max(0.1, 1.0 - (init_wl / (80.0 * wl_mult)))
        if days_left < 3: prob -= 0.08
        prob = max(0.05, min(0.95, prob))
        prob_pct = round(prob * 100, 1)
        total_prob += prob_pct

        # Current WL status
        decay = 0.6 if days_left > 5 else 0.3 if days_left > 1 else 0.0
        current_wl = max(0, int(init_wl * decay))

        if current_wl == 0:
            berth = 10 + _deterministic(pnr, f"berth{i}", 60)
            current_status  = f"CNF/{coach_label}/{berth}"
            booking_status  = f"WL# {init_wl}"
        elif current_wl <= 4:
            current_status  = f"RAC {current_wl}"
            booking_status  = f"WL# {init_wl}"
            berth = None
        else:
            current_status  = f"WL# {current_wl}"
            booking_status  = f"WL# {init_wl}"
            berth = None

        verd, _ = _verdict(prob_pct)
        passengers.append(PassengerStatus(
            passenger_number=i + 1,
            coach=coach_label,
            berth=berth,
            current_status=current_status,
            booking_status=booking_status,
            confirmation_probability=prob_pct,
            verdict=verd,
        ))

    overall_prob = round(total_prob / num_pax, 1)
    verdict, confidence = _verdict(overall_prob)

    return PNRResponse(
        pnr=pnr,
        train_number=train_number,
        train_name=train_name,
        source=source,
        destination=dest,
        journey_date=journey_date_str,
        coach_class=coach_class,
        quota=QUOTA_LABELS.get(quota, quota),
        distance_km=distance_km,
        chart_status=chart_status,
        passengers=passengers,
        overall_probability=overall_prob,
        verdict=verdict,
        confidence=confidence,
    )
