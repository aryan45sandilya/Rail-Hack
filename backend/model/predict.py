import os
import pickle
import datetime
import numpy as np

# Load trained XGBoost model from pickle
MODEL_PATH = os.path.join(os.path.dirname(__file__), "railhack_model.pkl")

def get_fallback_prediction(
    train_number: str,
    quota: str,
    coach_class: str,
    initial_wl: int,
    days_to_departure: int,
    is_festival: bool,
    avg_confirm_rate: float,
    distance_km: float
) -> dict:
    """
    High-fidelity mathematical predictor fallback if XGBoost model pickle is missing.
    Matches the statistical factors used during seeding and training exactly.
    """
    # Base probability
    prob = avg_confirm_rate
    
    # Quota modifiers
    quota_mods = {"GN": 0.0, "TQ": -0.15, "LD": 0.02, "SS": 0.05}
    prob += quota_mods.get(quota, 0.0)
    
    # Class modifiers
    class_mods = {"SL": -0.05, "3A": 0.08, "2A": 0.12, "1A": 0.18}
    prob += class_mods.get(coach_class, 0.0)
    
    # Waitlist size scaling
    wl_scale_factor = 80.0
    if coach_class == "SL":
        wl_scale_factor = 120.0
    elif coach_class == "1A":
        wl_scale_factor = 40.0
        
    prob_scale = max(0.05, 1.0 - (initial_wl / wl_scale_factor))
    prob *= prob_scale
    
    # Festival season
    if is_festival:
        prob -= 0.15
        
    # Days to departure modifier (minor boost if booked early and plenty of days left)
    if days_to_departure > 30:
        prob += 0.05
    elif days_to_departure < 3:
        prob -= 0.08
        
    # Cap between 2.0% and 98.0%
    prob = max(0.02, min(0.98, prob))
    prob_percent = round(prob * 100.0, 1)
    
    # Verdict selection
    if prob_percent >= 65.0:
        verdict = "likely"
        confidence = "high" if prob_percent > 80.0 else "medium"
    elif prob_percent >= 40.0:
        verdict = "borderline"
        confidence = "medium"
    else:
        verdict = "unlikely"
        confidence = "high" if prob_percent < 20.0 else "medium"
        
    # Determine top driving factors
    top_factors = []
    if is_festival:
        top_factors.append({
            "factor": "Festival Season",
            "impact": "negative",
            "description": "High travel volume and festival rush significantly reduce waitlist movement."
        })
    else:
        top_factors.append({
            "factor": "Non-Festival Window",
            "impact": "positive",
            "description": "Travel dates fall in standard period, normal cancellation frequencies expected."
        })
        
    # WL size factor
    if initial_wl > 60:
        top_factors.append({
            "factor": f"High Waitlist Position (WL-{initial_wl})",
            "impact": "negative",
            "description": "Large queue ahead makes clearance statistically challenging."
        })
    elif initial_wl <= 20:
        top_factors.append({
            "factor": f"Low Waitlist Position (WL-{initial_wl})",
            "impact": "positive",
            "description": "Close proximity to RAC/Confirmed zone increases chances of clearance."
        })
    else:
        top_factors.append({
            "factor": f"Moderate Waitlist Position (WL-{initial_wl})",
            "impact": "neutral",
            "description": "Moderate queue depth, relies heavily on bulk coach allocations."
        })
        
    # Quota factors
    if quota == "TQ":
        top_factors.append({
            "factor": "Tatkal (TQ) Quota",
            "impact": "negative",
            "description": "Tatkal waitlists experience very low cancellations (~4-7%)."
        })
    elif quota == "GN":
        top_factors.append({
            "factor": "General (GN) Quota",
            "impact": "positive",
            "description": "General quota ticket pools are larger and experience highest cancellation volume."
        })
        
    # Class factor
    if coach_class in ["3A", "2A", "1A"]:
        top_factors.append({
            "factor": f"AC Coach Class ({coach_class})",
            "impact": "positive",
            "description": "AC classes have higher seat volumes per coach allocation and stable clearance trends."
        })
    else:
        top_factors.append({
            "factor": "Sleeper Class (SL)",
            "impact": "negative",
            "description": "Sleeper coaches are heavily booked with historically low voluntary cancellation rates."
        })
        
    return {
        "confirmation_probability": prob_percent,
        "verdict": verdict,
        "confidence": confidence,
        "top_factors": top_factors,
        "method": "statistical_fallback"
    }

def predict_ticket(data: dict) -> dict:
    """
    Main prediction router: tries XGBoost, falls back to high-fidelity statistical heuristic if model is not trained yet.
    """
    # 1. Parse fields
    train_number = str(data.get("train_number", "12951"))
    quota = str(data.get("quota", "GN")).upper()
    coach_class = str(data.get("coach_class", "3A")).upper()
    initial_wl = int(data.get("initial_wl", 10))
    
    # Dates
    journey_date_str = data.get("journey_date", "2026-07-15")
    booked_at_str = data.get("booked_at", "2026-06-15")
    
    try:
        if isinstance(journey_date_str, datetime.date):
            journey_date = journey_date_str
        else:
            journey_date = datetime.datetime.strptime(journey_date_str.split("T")[0], "%Y-%m-%d").date()
    except Exception:
        journey_date = datetime.date.today() + datetime.timedelta(days=15)
        
    try:
        if isinstance(booked_at_str, datetime.datetime):
            booked_at = booked_at_str
        else:
            # Parse datetime or date
            clean_book = booked_at_str.split(".")[0].replace("Z", "")
            if "T" in clean_book:
                booked_at = datetime.datetime.strptime(clean_book, "%Y-%m-%dT%H:%M:%S")
            else:
                booked_at = datetime.datetime.strptime(clean_book, "%Y-%m-%d")
    except Exception:
        booked_at = datetime.datetime.combine(journey_date - datetime.timedelta(days=20), datetime.time(10, 0))
        
    days_to_departure = (journey_date - booked_at.date()).days
    is_festival = journey_date.month in [10, 11, 12]
    
    # 2. Derive Route averages
    # We can use hardcoded routes metadata or query database (done in fastapi endpoints, but let's have defaults here)
    avg_confirm_rate = 0.74
    distance_km = 1000.0
    
    # Hardcoded lookups for popular routes based on source/dest if database session is not passed in
    source = str(data.get("source", "NDLS")).upper()
    destination = str(data.get("destination", "MMCT")).upper()
    
    # Attempt lookup
    route_stats = {
        ("NDLS", "MMCT"): (1386.0, 0.78),
        ("NDLS", "HWH"): (1447.0, 0.72),
        ("NDLS", "MAS"): (2182.0, 0.65),
        ("SBC", "HYB"): (610.0, 0.82),
        ("CSMT", "SBC"): (1013.0, 0.74),
        ("HWH", "CSMT"): (1968.0, 0.68),
        ("HWH", "MAS"): (1661.0, 0.70),
        ("NDLS", "SBC"): (2365.0, 0.60),
        ("NDLS", "PNBE"): (998.0, 0.55),
        ("ADI", "MMCT"): (491.0, 0.88),
        ("GKP", "NDLS"): (730.0, 0.50),
        ("CSMT", "PNBE"): (1700.0, 0.45),
        ("SBC", "MAS"): (357.0, 0.85),
        ("LKO", "NDLS"): (512.0, 0.80),
        ("SC", "HWH"): (1545.0, 0.72),
        ("PUNE", "CSMT"): (192.0, 0.92),
        ("CNB", "NDLS"): (440.0, 0.83),
        ("NDLS", "JAT"): (577.0, 0.78),
        ("GHY", "HWH"): (980.0, 0.65),
        ("CSMT", "MAS"): (1279.0, 0.70)
    }
    
    pair = (source, destination)
    if pair in route_stats:
        distance_km, avg_confirm_rate = route_stats[pair]
        
    # Try load XGBoost pickle
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                payload = pickle.load(f)
                
            model = payload["model"]
            features = payload["features"]
            quota_map = payload["quota_map"]
            class_map = payload["class_map"]
            
            # Map input to feature columns
            quota_encoded = quota_map.get(quota, 0)
            class_encoded = class_map.get(coach_class, 0)
            
            # wl_movement_rate is calculated as initial_wl minus expected 24h decay if no snapshot exists
            # Typically waitlist reduces by ~25% 24 hours before
            wl_number_24h = initial_wl * 0.75
            wl_movement_rate = initial_wl - wl_number_24h
            
            # train_cancellation_rate hashed from train_number
            train_cancellation_rate = (int(train_number) % 15) / 500.0 if train_number.isdigit() else 0.01
            
            day_of_week = journey_date.weekday()
            month = journey_date.month
            
            # Form feature vector in identical order
            # "initial_wl", "quota_encoded", "class_encoded", "days_to_departure", "is_festival_season", 
            # "wl_movement_rate", "route_avg_confirm_rate", "train_cancellation_rate", "journey_distance_km", "day_of_week", "month"
            feats = [
                initial_wl,
                quota_encoded,
                class_encoded,
                days_to_departure,
                int(is_festival),
                wl_movement_rate,
                avg_confirm_rate,
                train_cancellation_rate,
                distance_km,
                day_of_week,
                month
            ]
            
            # Convert to numpy array of correct shape
            feats_arr = np.array([feats])
            
            # Predict probability
            prob_arr = model.predict_proba(feats_arr)[0]
            prob_val = float(prob_arr[1]) # probability of class 1 (confirmed)
            prob_percent = round(prob_val * 100.0, 1)
            
            # Get verdict and confidence
            if prob_percent >= 65.0:
                verdict = "likely"
                confidence = "high" if prob_percent > 80.0 else "medium"
            elif prob_percent >= 40.0:
                verdict = "borderline"
                confidence = "medium"
            else:
                verdict = "unlikely"
                confidence = "high" if prob_percent < 20.0 else "medium"
                
            # Drive factors list
            base_factors = get_fallback_prediction(
                train_number, quota, coach_class, initial_wl, 
                days_to_departure, is_festival, avg_confirm_rate, distance_km
            )["top_factors"]
            
            return {
                "confirmation_probability": prob_percent,
                "verdict": verdict,
                "confidence": confidence,
                "top_factors": base_factors,
                "method": "XGBoost"
            }
        except Exception as e:
            # Fallback on any error during loading/running XGBoost
            print(f"XGBoost load error: {e}. Falling back to statistical predictor...")
            
    # Return statistical fallback predictor
    return get_fallback_prediction(
        train_number, quota, coach_class, initial_wl, 
        days_to_departure, is_festival, avg_confirm_rate, distance_km
    )
