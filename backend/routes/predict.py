import os
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import redis

# Try importing database connection if available
try:
    from db.models import Base
except ImportError:
    # Handle relative pathing
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from db.models import Base

from model.predict import predict_ticket

router = APIRouter()

# Redis initialization (optional/graceful fallback)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
    # Ping to test connection
    redis_client.ping()
    print("Connected to Redis successfully.")
except Exception:
    print("Redis not available. Caching disabled.")
    redis_client = None

class PredictionRequest(BaseModel):
    train_number: str = Field(..., description="5-digit Train number", example="12951")
    source: str = Field(..., description="Source station code", example="NDLS")
    destination: str = Field(..., description="Destination station code", example="MMCT")
    quota: str = Field(..., description="Quota (GN, TQ, LD, SS)", example="GN")
    coach_class: str = Field(..., description="Coach Class (SL, 3A, 2A, 1A)", example="3A")
    initial_wl: int = Field(..., description="Initial waitlist number", ge=1, example=45)
    journey_date: str = Field(..., description="Journey date (YYYY-MM-DD)", example="2026-07-15")
    booked_at: str = Field(..., description="Booking date and time", example="2026-06-15T10:00:00")

class PredictionFactor(BaseModel):
    factor: str
    impact: str  # positive, negative, neutral
    description: str

class PredictionResponse(BaseModel):
    confirmation_probability: float
    verdict: str  # likely, borderline, unlikely
    confidence: str  # high, medium, low
    top_factors: list[PredictionFactor]
    cached: bool = False

@router.post("/predict", response_model=PredictionResponse)
def get_prediction(request: PredictionRequest):
    # Try fetching from cache first
    cache_key = f"predict:{request.train_number}:{request.source}:{request.destination}:{request.quota}:{request.coach_class}:{request.initial_wl}:{request.journey_date}"
    
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                response_dict = json.loads(cached_data)
                response_dict["cached"] = True
                return response_dict
        except Exception as e:
            print(f"Redis cache read error: {e}")
            
    # Calculate prediction
    try:
        input_data = request.model_dump()
        prediction = predict_ticket(input_data)
        
        # Save to Redis for 1 hour (3600 seconds)
        if redis_client:
            try:
                redis_client.setex(cache_key, 3600, json.dumps(prediction))
            except Exception as e:
                print(f"Redis cache write error: {e}")
                
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
