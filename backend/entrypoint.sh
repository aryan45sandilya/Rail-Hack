#!/bin/bash
set -e

echo "=== RailHack Backend Startup ==="

# Run DB seed if no data exists yet
echo "Checking database..."
cd /app/db
python seed.py
cd /app

# Train model if pkl not present
if [ ! -f /app/model/railhack_model.pkl ]; then
    echo "Training XGBoost model..."
    cd /app/model
    python train.py
    cd /app
else
    echo "Model already trained, skipping..."
fi

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
