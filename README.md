# Architecture Evolution Analyzer

Architecture Evolution Analyzer is a FastAPI web application that samples a public GitHub repository's history and reports code growth, structural complexity, dependency changes, architecture drift, and evolving hotspots.

The application uses server-rendered [Jinja2](https://jinja.palletsprojects.com/) templates for the dashboard and a small JSON API for submitting and polling analyses. The analyzer itself remains independent from HTTP and UI concerns.

<<<<<<< Updated upstream
`Python` · `GitPython` · `AST Analysis` · `Hugging Face` · `Gradio`

https://architecture-evolution-analyzer.onrender.com/
=======
## Architecture

```text
Browser
  ├─ Jinja2 dashboard and static CSS/JavaScript
  └─ POST /api/analyses, GET /api/analyses/{id}
       └─ AnalysisJobService (background worker)
            └─ RepositoryService (validation, temporary clone, cleanup)
                 └─ Analyzer (Git history, AST metrics, dependencies, evolution)
```

Key directories:

- `app/api/` — HTML routes and JSON request/response models.
- `app/services/` — cloning and background-job lifecycle.
- `app/analyzers/` — language parsing, dependency graph construction, and drift rules.
- `app/templates/` — Jinja2 layouts and reusable UI partials.
- `app/static/` — CSS and browser JavaScript.
- `tests/` — unit and route tests.

## Run locally

Python 3.11+ and Git are required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 7860
```

Open `http://localhost:7860` and submit a public URL in the form `https://github.com/owner/repository`.

Set `HF_TOKEN` in `.env` to enable the optional Hugging Face architectural explanation. The default `HF_PROVIDER=hf-inference` avoids automatic third-party routing; set `HF_PROVIDER=auto` only if you intentionally want Hugging Face to select a provider. Transient provider failures are retried, and a deterministic architectural summary is shown if the provider remains unavailable.

## API

Start an analysis:

```bash
curl -X POST http://localhost:7860/api/analyses \
  -H 'content-type: application/json' \
  -d '{"repository_url":"https://github.com/owner/repository","snapshot_count":15}'
```

Poll the `id` returned from the request:

```bash
curl http://localhost:7860/api/analyses/<analysis-id>
```

Jobs are intentionally stored in memory. They are appropriate for a single-process deployment; use Redis or a database-backed worker queue before deploying across multiple application instances.

## Quality checks

```bash
ruff check .
ruff format --check .
mypy app
pytest --cov=app
```

## Docker

```bash
docker build -t architecture-evolution-analyzer .
docker run --rm -p 7860:7860 --env-file .env architecture-evolution-analyzer
```

## Current scope and limitations

- Only public HTTPS GitHub repositories are accepted.
- Analysis clones the complete history; set operational limits before exposing it publicly.
- AST metrics support Python, JavaScript, TypeScript/TSX, Java, and Kotlin.
- Dependency detection recognizes local imports heuristically; it is not a full language-aware resolver.
>>>>>>> Stashed changes
