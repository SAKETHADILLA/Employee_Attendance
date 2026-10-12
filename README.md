# Employee Attendance & Analytics API

A high-performance FastAPI and MongoDB service built for employee attendance tracking, manual corrections with audit logging, and reporting analytics powered by native MongoDB aggregation pipelines.

---

## Features
- **Attendance Punch Lifecycle:** State-validated punch-in and punch-out handling with strict double punch-in prevention (enforced via database unique compound indexes) and overnight shift resolution (R1).
- **Automated Rule Evaluations:** Real-time computation of late arrivals with grace periods (R2), overtime calculations with thresholds (R3), half-up rounded working hours (R4), and half-day classifications (R5).
- **Manual Regularization & Audit Trail:** Manual attendance adjustments with append-only history tracking recording authors, timestamps, justifications, and before/after field changes.
- **Aggregations & Analytics:** Non-blocking MongoDB aggregation pipelines calculating monthly employee metrics, department-wide summaries with zero-log headcount retention (R9), late-comer leaderboards with Standard Competition Ranking, and daily department trends with 7-day moving averages.
- **Query Optimization & Explain:** Mandatory compound indexes initialized idempotently at startup to guarantee index scans (`IXSCAN`) across all operations.

---

## Local Setup

### 1. Prerequisites
- Python 3.11+
- MongoDB 6.0+ (Local instance, Docker, or MongoDB Atlas URI)

### 2. Environment Setup
```bash
# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Configure the database connection via environment variables:
```bash
# On Linux/macOS:
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="attendance_db"

# On Windows PowerShell:
$env:MONGO_URI="mongodb://localhost:27017"
$env:MONGO_DB="attendance_db"
```
*(A local `.env` file can also be used; real environment variables always take precedence).*

### 4. Seed Sample Data (Optional)
```bash
python sample_seed.py
```

### 5. Run the Application
```bash
uvicorn app.main:app --port 8000 --reload
```

---

## Interactive API Documentation
Once running, explore and test the endpoints via the built-in Swagger UI:
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Readiness Probe:** `GET http://localhost:8000/health`

---

## Testing
Run the test suite using `pytest`:
```bash
pytest -v
```

---

## Deliverables Summary
- `app/main.py`: Complete production implementation matching OpenAPI 3.0.3 specification.
- `requirements.txt`: Clean dependencies list.
- `REVIEW.md`: Detailed audit identifying all defects in the starter code with root-cause fixes.
- `DECISIONS.md`: Architectural decisions regarding indexing, concurrency handling, tie-breaking, and scalability.
- `README.md`: Setup instructions and runtime guidelines.
