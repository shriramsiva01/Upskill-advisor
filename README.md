Career Path Recommender (RAG Project)
Overview:
This project is an AI-powered course recommender system. It helps students bridge the gap between their current skills and job requirements by
* Comparing student skills vs. job descriptions
* Identifying gaps
* Suggesting courses (from Pinecone vector DB)
* Generating an optimized course path using an LLM (Ollama + LangChain)
* Providing a visual radar chart and a PDF report


Setup Instructions:
1. Backend (FastAPI + MySQL + Pinecone)

cd backend
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
——
Configure .env (if using one):
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/rag
PINECONE_API_KEY=your-pinecone-key
——
Initialize DB:
python ingest.py
——
Run backend:
uvicorn main:app --reload

Backend runs at  http://127.0.0.1:8000

2. Frontend (React + Vite + Tailwind):
cd frontend
npm install
npm run dev

Frontend runs at  http://127.0.0.1:5173


How to Use:
1. Open the frontend in your browser.
2. Enter Student ID and Job ID (e.g., 1 and 1).
3. Click Get Plan.
    * You’ll see:
        * A Radar chart (student vs job skills)
        * Recommended courses from Pinecone
        * LLM reasoning explanation
4. Click Download PDF Report → generates a formatted report.


Metrics & Evaluation:
The system tracks key KPIs:
* Latency: total time taken for advice method
* Cost: estimated cost per LLM + Pinecone query
* Top-k Skill Coverage: % of job-required skills covered in recommended courses


Key Design Decisions
1. Hybrid Data Sources
    * MySQL stores structured data (students, jobs, skills).
    * Pinecone stores vector embeddings of course descriptions for semantic search.
2. LLM Integration
    * Used LangChain + Ollama (LLaMA3) for reasoning over course selections.
    * Tradeoff: more accurate reasoning, but slower & costlier than simple heuristics.
3. Course Ranking
    * Scoring function = level_gain / (duration * cost)
    * Balances efficiency (time & cost) with skill improvement.
4. Frontend Tech
    * React + Vite for fast builds.
    * TailwindCSS for styling.
    * Recharts for radar chart visualization.


Tradeoffs
* Why SQL for skills, Pinecone for courses? Skills are small, structured, easy to query → SQL. Courses are large, text-rich, better suited for semantic search → Pinecone.
* Why Ollama (local LLM) instead of OpenAI API? Local → free, private, offline. Tradeoff: slightly slower & requires machine resources.
* Why PDF Reports with ReportLab? Chose ReportLab for lightweight, dependency-free PDF generation. Tradeoff: less design flexibility vs HTML → PDF converters.

