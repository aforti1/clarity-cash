# Clarity Cash

Clarity Cash is a data-driven budgeting app that connects to your bank accounts, pulls transaction data, and turns your spending into clear, actionable insights. It was originally started for Technica Hackathon 2025 at UMD, and may be expanded for completion in the future.

## Overview

Clarity Cash focuses on answering one core question:

> Given how I actually spend, what is truly “unavoidable” versus what I can control or change?

To do this, the backend ingests bank transactions, maps them into a custom category system, and computes metrics and scores that summarize the health of a user’s spending over a selected time period.

## Features

- Connect bank accounts using Plaid
- Fetch and store transactions for each user
- Categorize spending into structural/unavoidable vs flexible/controllable buckets
- Flag risky or harmful patterns (fees, cash advances, etc.)
- Compute summary metrics and an overall “clarity” score for a period
- Provide a simple API for a web or mobile frontend to consume

## Project Structure

The repository is organized as a monorepo:

- `backend/` – FastAPI backend and scoring logic
- `frontend/` – TypeScript/React frontend (consumer of the backend API)
- Root configuration:
  - `requirements.txt` – Python dependencies for the backend
  - `package.json` – Node/TypeScript dependencies for the frontend tooling
  - Firebase and helper scripts for local development

## Tech Stack

- Backend: Python, FastAPI
- Banking: Plaid API
- Database / Storage: Firestore / Firebase
- Frontend: TypeScript + React
- Hosting: Firebase (for frontend) plus any compatible backend host

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/aforti1/clarity-cash.git
cd clarity-cash
```

### 2. Backend setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r ../requirements.txt
```

Create a `.env` file in `backend/` with your configuration values:

```env
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox   # or development
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
FIREBASE_PROJECT_ID=your_firebase_project_id
BACKEND_PORT=5173
```

Run the backend:

```bash
uvicorn main:app --reload --port 5173
```

By default, the API will be available at:

- `http://localhost:5173`


### 3. Frontend setup

In a separate terminal:

```bash
cd clarity-cash/frontend

npm install
npm run dev
```

Then open the URL printed in the terminal (typically something like `http://localhost:5173`) and ensure the backend is running at `http://localhost:5173`.

## API (High-Level)

Typical backend responsibilities include:

- Creating a Plaid Link token  
  `POST /plaid/link/token`

- Exchanging a Plaid public token for an access token  
  `POST /plaid/exchange`

- Fetching transactions and computing scores for a user  
  `GET /plaid/transactions/{uid}`

- Health check  
  `GET /health`

Exact endpoint names and payloads may evolve as the project grows; refer to the FastAPI routes in `backend/` for the current API surface.

## Scoring Logic

At a high level, the scoring flow is:

1. Pull transactions from Plaid for a given user and time range.
2. Map transactions into custom categories:
   - Structural / unavoidable (e.g., rent, utilities, core groceries)
   - Flexible / controllable (e.g., discretionary, non-essential recurring)
   - Harmful / risky (e.g., fees, cash advances)
3. Compute metrics such as:
   - Effective income
   - Share of unavoidable vs flexible spending
   - Fees and cash-advance ratios
4. Aggregate these into a summary “clarity” score for the period.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.



