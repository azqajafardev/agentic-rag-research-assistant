# EvidenceRAG Frontend

React + Vite + Tailwind CSS interface for EvidenceRAG, consuming the FastAPI backend in `../backend`.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # adjust VITE_API_URL if the backend isn't on 127.0.0.1:8000
npm run dev
```

Frontend: http://localhost:5173 — requires the backend running (see `../backend/README` equivalent run instructions).
