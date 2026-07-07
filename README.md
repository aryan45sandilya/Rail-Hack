# RailHack — Indian Railways Waitlist Confirmation Predictor

RailHack is a Waitlist Confirmation Predictor designed with a physical railway station board aesthetic. It leverages a trained XGBoost classifier and historical IRCTC booking patterns to deliver high-fidelity waitlist clearance probability estimates.

## Tech Stack
- **Frontend**: React + Vite + Tailwind CSS + Framer Motion
- **Backend**: Python + FastAPI
- **ML**: XGBoost, scikit-learn, pandas, numpy
- **Database**: PostgreSQL (main storage) + Redis (1-hour caching layer)
- **Styling**: Indian Railways departure board & physical ticket themed design tokens.

---

## Design System

The application centers around a custom theme reflecting the visual cues of physical tickets and mechanical split-flap station departure boards:
- **Station-Board Theme**: Deep charcoals, aged parchment/cream texts, and glowing mechanical amber highlights (`#f5a623`).
- **Split-Flap Animation**: Probability percentages flip like actual departure signage digits.
- **Ticket Aesthetics**: Perforated ticket cards, large monospace station identifiers (NDLS, MMCT), and ticket tears.

---

## Folder Structure

```text
railhack/
├── backend/
│   ├── main.py                 # FastAPI application setup
│   ├── model/
│   │   ├── train.py            # Model training workflow
│   │   ├── predict.py          # Prediction route calculations
│   │   └── railhack_model.pkl  # Trained serialized classifier
│   ├── routes/
│   │   ├── predict.py          # /predict POST endpoints
│   │   └── stats.py            # /routes and /trains statistics
│   ├── db/
│   │   ├── models.py           # SQLAlchemy declarative schema
│   │   └── seed.py             # Route & 500 ticket records seeder
│   └── requirements.txt
├── src/
│   ├── components/             # Customized styled ticket modules
│   ├── pages/                  # Home, Results, and Route Explorer
│   └── App.tsx                 # Client controller
├── docker-compose.yml          # Local container configuration
└── README.md
```

---

## Local Development & Installation

### Option 1: Run via Docker Compose
Ensure Docker is installed, then run from the root:
```bash
docker-compose up --build
```
This automatically boots PostgreSQL, Redis, the FastAPI backend, and the React client.

### Option 2: Manual Backend Setup
1. Enter the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the local SQLite database and seed initial values:
   ```bash
   python db/seed.py
   ```
4. Train the ML model:
   ```bash
   python model/train.py
   ```
5. Spin up the FastAPI server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```

### Option 3: Client Setup
1. Install client dependencies at the root directory:
   ```bash
   npm install
   ```
2. Start the Vite client dev server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` to inspect.
