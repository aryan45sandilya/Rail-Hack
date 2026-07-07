from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import routes
from routes.predict import router as predict_router
from routes.stats import router as stats_router
from routes.pnr import router as pnr_router

app = FastAPI(
    title="RailHack API",
    description="Indian Railways waitlist confirmation predictor backend",
    version="1.0.0"
)

# Set up CORS middleware to allow cross-origin requests from frontend (Vercel, AI Studio preview, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Vercel and AI Studio origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base healthcheck route
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "RailHack Waitlist Prediction Engine"}

# Include routers
app.include_router(predict_router, prefix="/api", tags=["Prediction"])
app.include_router(stats_router, prefix="/api", tags=["Statistics"])
app.include_router(pnr_router, prefix="/api", tags=["PNR"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
