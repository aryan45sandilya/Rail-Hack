import os
import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    print("Training XGBoost prediction model on seeded dataset...")
    
    # Establish connection to sqlite database
    # Database path — resolve relative to this file's location
    import pathlib
    _HERE = pathlib.Path(__file__).parent  # model/
    _DB_PATH = _HERE.parent / "db" / "railhack.db"
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DB_PATH}")
            
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    # 1. Fetch data
    tickets_query = """
    SELECT 
        t.id as ticket_id,
        t.quota,
        t.coach_class,
        t.initial_wl,
        t.journey_date,
        t.booked_at,
        t.confirmed,
        r.distance_km,
        r.avg_confirm_rate as route_avg_confirm_rate,
        tr.train_number
    FROM tickets t
    JOIN routes r ON t.route_id = r.id
    JOIN trains tr ON t.train_id = tr.id
    """
    
    tickets_df = pd.read_sql(tickets_query, engine)
    
    if len(tickets_df) == 0:
        raise ValueError("No historical tickets found in database. Run seed.py first.")
        
    snapshots_query = """
    SELECT ticket_id, wl_number, hours_to_departure
    FROM wl_snapshots
    WHERE hours_to_departure = 24
    """
    snapshots_df = pd.read_sql(snapshots_query, engine)
    
    # Merge snapshot at 24 hours
    df = pd.merge(tickets_df, snapshots_df, on="ticket_id", how="left")
    
    # 2. Feature Engineering
    # Encode Quota: GN=0, TQ=1, LD=2, SS=3
    quota_map = {"GN": 0, "TQ": 1, "LD": 2, "SS": 3}
    df["quota_encoded"] = df["quota"].map(lambda x: quota_map.get(x, 0))
    
    # Encode Class: SL=0, 3A=1, 2A=2, 1A=3
    class_map = {"SL": 0, "3A": 1, "2A": 2, "1A": 3}
    df["class_encoded"] = df["coach_class"].map(lambda x: class_map.get(x, 0))
    
    # Dates conversion
    df["journey_date"] = pd.to_datetime(df["journey_date"])
    df["booked_at"] = pd.to_datetime(df["booked_at"])
    
    # days_to_departure
    df["days_to_departure"] = (df["journey_date"] - df["booked_at"]).dt.days
    
    # is_festival_season (Oct/Nov/Dec)
    df["is_festival_season"] = df["journey_date"].dt.month.isin([10, 11, 12]).astype(int)
    
    # wl_movement_rate (initial_wl - wl_24hr_before)
    # If 24hr snapshot is missing, fill with estimated snapshot decay
    df["wl_number_24h"] = df["wl_number"].fillna(df["initial_wl"] * 0.7)
    df["wl_movement_rate"] = df["initial_wl"] - df["wl_number_24h"]
    
    # train_cancellation_rate (deterministically hashed from train_number)
    df["train_cancellation_rate"] = df["train_number"].apply(lambda x: (int(x) % 15) / 500.0) # between 0.0% and 3.0%
    
    # Journey distance
    df["journey_distance_km"] = df["distance_km"]
    
    # day_of_week & month
    df["day_of_week"] = df["journey_date"].dt.dayofweek
    df["month"] = df["journey_date"].dt.month
    
    # Target
    df["target"] = df["confirmed"].astype(int)
    
    # Select features
    feature_cols = [
        "initial_wl",
        "quota_encoded",
        "class_encoded",
        "days_to_departure",
        "is_festival_season",
        "wl_movement_rate",
        "route_avg_confirm_rate",
        "train_cancellation_rate",
        "journey_distance_km",
        "day_of_week",
        "month"
    ]
    
    X = df[feature_cols]
    y = df["target"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric="logloss"
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model accuracy on test set: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, preds))
    
    # Package model and metadata
    payload = {
        "model": model,
        "features": feature_cols,
        "quota_map": quota_map,
        "class_map": class_map,
        "accuracy": acc
    }
    
    # Save model to the same directory as this script
    model_path = os.path.join(os.path.dirname(__file__), "railhack_model.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(payload, f)
        
    print("Saved railhack_model.pkl successfully!")

if __name__ == "__main__":
    train_model()
