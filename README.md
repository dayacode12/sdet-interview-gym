# SDET Interview Gym — Charles Schwab Cybersecurity QA Preparation

A personal, self-hosted practice platform for an SDET / Cyber Security QA interview.
It runs fully offline and honestly: **Java code is really compiled and executed,
SQL really runs against a sandboxed database, and nothing is ever faked.**

> ⚠️ **Honesty statement.** Every question, scenario and "expected interview question"
> in this gym is a *prediction* of likely topics based on the public role description
> and general SDET interview knowledge. Nothing here is a leaked or actual Charles
> Schwab question bank. Free-text scoring is a transparent rule-based rubric
> (keyword coverage + structure signals) unless you configure an optional LLM key —
> it is a practice aid, not a human judge.

---

## What's inside

| Area | Content |
|---|---|
| **Java Lab** | 33 questions (core Java + automation-focused) with a real run-button, stdin/stdout test harness, hints and solutions |
| **Automation Lab** | 12 Selenium / Playwright / REST Assured coding exercises + framework architecture Q&A |
| **SQL Playground** | 26 challenges on a seeded IAM dataset (users, roles, access requests, certifications, provisioning logs) with realistic defects planted; free-query sandbox |
| **IAM Lab** | 5 modules (IAM fundamentals, IGA/Saviynt, PAM/CyberArk, auth protocols, DLP) with concepts, architecture, interview Q&A, test cases and server-graded quizzes |
| **Scenario Simulator** | 30 enterprise security QA scenarios, scored against a 5-dimension rubric with full model answers |
| **Mock Interview** | 60-minute timed interview, 6 sections, 22 questions, weighted rubric (technical 30% / practical 25% / problem-solving 20% / communication 15% / security 10%) |
| **Resume Deep Dive** | 15 questions with STAR scaffolds; candidate-specific gaps are flagged, never invented |
| **Flashcards** | 100 cards across 17 topics with confidence tracking |
| **Analytics** | Progress, weak Java categories, mock history, time-on-topic |
| **Cheat Sheet** | 12 sections + HTTP status reference |

All progress persists in a local database (SQLite by default).

## Quick start (local development)

**Requirements:** Python 3.12+, Node 20+, and a JDK (`javac` + `java`) if you want
the run button to actually run Java.

```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows (use source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
copy ..\.env.example .env          # optional — defaults work offline
python -m uvicorn app.main:app --port 8000 --reload

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev                        # http://localhost:3000
```

The backend API docs (Swagger) live at http://localhost:8000/docs.

### Java execution modes

The backend detects what is available at startup and **tells the truth in the UI**:

- `docker` — candidate code runs in a throwaway container: `--network none`,
  `--memory 512m`, `--cpus 1`, read-only root FS, tmpfs workspace.
- `local` — code runs as a short-lived `javac`/`java` subprocess in an isolated
  temp directory (the usual mode on a dev machine without the Docker CLI).
- `disabled` — no execution; the editor, hints, solutions and test cases all still
  work, and every run request returns an honest error instead of a fake pass.

Force a mode with `JAVA_EXECUTION_MODE=docker|local|disabled` (default `auto`).

To build the sandboxed executor image:

```bash
docker build -t sdet-gym-java:latest docker/java-executor
```

### SQL playground safety

- Every query runs against a **fresh, in-memory SQLite database** seeded with the
  IAM dataset — never the application database, and no credentials ever reach the browser.
- Only `SELECT` / `WITH` statements are accepted; write keywords (`DROP`, `INSERT`,
  `UPDATE`, `DELETE`, `ATTACH`, `PRAGMA`, …) are blocked, with string literals
  stripped first so data containing keywords doesn't false-positive.
- `PRAGMA query_only = 1` is set after seeding as a second layer.
- Challenge grading compares **result rows** (order-insensitive), not SQL strings.

### Optional LLM evaluation

Free-text answers are scored by a transparent rule-based rubric by default. To use
an OpenAI-compatible LLM instead, set `LLM_API_KEY` (and optionally `LLM_BASE_URL`,
`LLM_MODEL`) in `backend/.env`. If the LLM call fails, scoring falls back to
rule-based and says so — it never silently fakes an LLM verdict.

## Docker Compose

```bash
# backend + frontend (SQLite)
docker compose up --build

# with PostgreSQL instead of SQLite
DATABASE_URL=postgresql+psycopg2://gym:gym@postgres:5432/sdet_gym \
docker compose --profile postgres up --build
```

Note for **Windows / macOS Docker Desktop**: the backend container cannot spawn
sibling containers without docker-in-docker. Either run the backend natively with
`JAVA_EXECUTION_MODE=local` (recommended) or keep `docker` mode with the host
Docker socket mounted (Linux hosts).

## Deploying (backend on Render, UI on GitHub Pages)

The repo ships deployment wiring for both free tiers:

| Piece | How | Files |
|---|---|---|
| **Backend API** | Render blueprint: Docker service + managed PostgreSQL | `render.yaml`, `backend/Dockerfile` |
| **UI** | GitHub Actions workflow: static export of the Next.js app | `.github/workflows/deploy-ui.yml`, `frontend/next.config.ts` |

The Render image bakes in a JDK 21, so candidate Java code still really compiles
and runs there (`JAVA_EXECUTION_MODE=local` subprocess mode — Docker-in-Docker is
not available on Render). Progress persists in managed PostgreSQL
(`DATABASE_URL` is wired automatically by the blueprint).

### 1. Push the repo to GitHub

The repo is a normal git checkout — `main` is the deploy branch for both hosts.

### 2. Deploy the backend on Render

1. Render Dashboard → **New → Blueprint** → pick this repository.
2. Render reads `render.yaml` and creates the web service plus the Postgres
   database. When prompted for `CORS_ORIGINS`, set it to your GitHub Pages URL
   plus local development, comma-separated, e.g.
   `https://<user>.github.io,http://localhost:3000`.
3. Wait for the build; the health check is `/api/health`. Your API is then at
   `https://<service-name>.onrender.com` (free services sleep after inactivity —
   the first request after a nap takes ~30s to wake).

> Note: free-tier Render Postgres **expires after 30 days**. Before it expires,
> back up your progress (or redeploy a fresh database and export/import what
> you need). Locally nothing changes — SQLite is still the default.

### 3. Publish the UI on GitHub Pages

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. The `Deploy UI to GitHub Pages` workflow runs on every push to `main`. It
   builds the frontend as a static export (`NEXT_OUTPUT=export`, base path
   `/<repo>`) and publishes it. Your UI lands at
   `https://<user>.github.io/<repo>/`.
3. The workflow bakes in the backend URL from the Actions **variable**
   `NEXT_PUBLIC_API_URL` (Settings → Secrets and variables → Actions →
   Variables). If the variable is absent it defaults to
   `https://sdet-interview-gym-api.onrender.com`, matching the blueprint's
   service name — so with default names, no variable is needed.

### 4. Point the UI at your backend (one of two ways)

- **Baked in**: set the `NEXT_PUBLIC_API_URL` Actions variable to your Render
  URL before the workflow runs.
- **Per browser**: open the hosted dashboard once — the "Backend not
  reachable" box has a URL field; paste your Render URL and press Save. It is
  stored in that browser's localStorage and takes effect immediately.

Local development is unaffected by all of this: with no `NEXT_OUTPUT` /
`NEXT_PUBLIC_BASE_PATH` env vars set, `npm run dev` / `npm run build` behave
exactly as before.

## Tests

```bash
# Backend: content integrity, SQL sandbox security, rubric logic, API smoke
# (the API suite performs real Java compilation/execution and real SQL grading)
cd backend
python -m pytest

# E2E (requires backend on :8000 and frontend dev server on :3000)
cd frontend/e2e
npm install
npx playwright install chromium
npx playwright test
```

## Project layout

```
backend/
  app/
    config.py            settings + Java mode detection
    database.py          engine/session (SQLite default, Postgres via DATABASE_URL)
    models.py            progress models (attempts, scenarios, mocks, flashcards…)
    schemas.py           request schemas
    main.py              FastAPI app, CORS, routers
    content/             all question banks (pure Python data)
    services/
      java_executor.py   docker/local/disabled execution — never fakes
      sql_runner.py       read-only in-memory SQL sandbox
      evaluation.py       rule-based rubric + optional LLM
    routers/             java, sql, scenarios, mock, flashcards, iam,
                         automation, resume, roadmap, analytics, settings
  tests/                 pytest suite
frontend/                Next.js app (App Router, TypeScript, Tailwind, Monaco, Recharts)
docker/
  java-executor/         sandboxed JDK image for candidate code
```

## Candidate profile note

The resume deep-dive and mock interview content reference the real candidate
profile (2+ years at TCS, Admiral Group IAM work, Saviynt/CyberArk/JML/CIAM,
300+ automated cases, Selenium→Playwright migration). Questions that need
details only you can supply are flagged `needs_candidate_detail` — fill those in
yourself; the platform deliberately does not invent them.
