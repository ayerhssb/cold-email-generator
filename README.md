# Cold Email Generator

>A small Python utility to generate personalized cold emails and perform mail-merge style deliveries. This repository contains helper chains, mail-merge tooling, resume editing utilities, and a minimal runner.

## Contents / Quick overview

- `app/` - main application modules
  - `main.py` - entrypoint for the app (simple runner/wrapper)
  - `mailmerge.py` - mail-merge logic (reads CSVs and sends personalized emails)
  - `chains.py`, `utils.py`, `logger.py` - supporting helpers and logging
  - `ResumeEditor.py` - tools to edit/generate resume content
  - `credentials-mail-merge.json` - (local) mail credentials used by mailmerge (sensitive; not committed)
  - `test-mailmerge.csv` - example CSV used for mail-merge testing
  - `token.json` / `token*` - tokens or API keys used by some flows (sensitive)
- `data/` - generated or static data (e.g., `resume.json`)
- `resource/portfolio.csv` - supplemental CSVs (portfolio data)
- `pdfs/` - generated PDF artifacts (if any)
- `vectorstore/` - local vector DB artifacts (Chroma) used by retrieval components
- `portfolio.csv` - root-level data copy
- `requirements.txt` / `pyproject.toml` - dependency metadata

Files intentionally ignored in this README generation: `generate_logs.py` and `run_evaluation_suite.py` (per request).

## Features

- Generate personalized cold emails using templates and data from CSV files.
- Mail-merge capability to send emails (uses credentials in `app/credentials-mail-merge.json`).
- Resume editing utilities to shape resume content programmatically.
- Small vectorstore-based retrieval (Chroma) for content/context reuse.

## Minimal contract

- Inputs: CSV rows (contacts + context), optional resume JSON and portfolio CSV.
- Outputs: personalized email text, optional sent emails (SMTP), saved PDFs or logs.
- Error modes: missing credentials, invalid CSV rows, or missing tokens will fail gracefully and log an error.

## Setup (local)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

Prefer using `uv` (this project includes `uv.lock`) to run commands inside the pinned environment. Example — install dependencies by running pip inside the `uv` environment:

```bash
uv sync
```

3. Prepare credentials and tokens:

- Add your mail credentials to `app/credentials-mail-merge.json` (example keys: smtp server, smtp port, username, password). Keep this file out of version control.
- If the app uses API tokens (e.g., `token.json`, or `app/token.json`) place them in the expected location and protect them.

4. Check or initialize the vectorstore if you rely on retrieval features. The vector DB lives under `vectorstore/`.

## Usage

- Run the main app using Streamlit through `uv`. The command for starting the app is:

```bash
export PYTHONPATH=.
uv run streamlit run app/main.py
```
Notes:
- The repository contains `app/test-mailmerge.csv` as an example. Inspect it to match expected CSV column names before running a real mail-merge.
- Sending emails requires valid OAuth credentials and network access.

## Configuration

- `app/credentials-mail-merge.json`: Gmail API settings (sensitive). Example structure:
- `token.json` or `app/token.json`: API tokens (e.g., for third-party services). Keep private.

## Developer notes

- Code style and tests: There are no formal tests included by default. Add unit tests for `mailmerge` and `ResumeEditor` when modifying behavior.
- When editing code that touches the vectorstore, back up `vectorstore/chroma.sqlite3` before destructive operations.

## Troubleshooting

- SMTP/auth errors: confirm credentials in `app/credentials-mail-merge.json` and that the SMTP server allows external connections.
- Missing dependencies: re-run `uv sync` in an activated venv.
- Permission errors when writing outputs: ensure the process has write permission to `pdfs/`, `logs/`, and `vectorstore/`.

## Security and secrets

Never commit credentials, tokens, or secrets. Use environment variables or a local, gitignored JSON for credentials as shown above.

## Contributing

If you'd like to contribute:

1. Fork the repo.
2. Create a feature branch.
3. Add tests for new behavior.
4. Open a pull request describing your changes.
