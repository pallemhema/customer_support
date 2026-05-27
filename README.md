# GenAI Assessment

A small GenAI evaluation and RAG pipeline used for demonstration and testing.

## Summary

This repository implements a retrieval-augmented generation (RAG) pipeline, a set of agents and tools for intent/order/tracking/escalation flows, and evaluation/test harnesses. It includes a Streamlit UI and a FastAPI endpoint for running the system locally.

## Quick Start

Prerequisites

- Python 3.10+ (use a virtual environment)
- (Optional) Local MongoDB instance if you want to persist sessions/history

Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Seed data (optional)

```bash
python seed/seed.py
```

Run the API

```bash
uvicorn ui.api:app --reload --port 8000
```

Run the UI

```bash
streamlit run ui/app.py
```

Run tests

```bash
pytest -q
```

## Project Layout

- agents/: Agent implementations and orchestration (intent, order, escalation, tracking, followup, retrieval, etc.)
- rag/: RAG pipeline and retriever, local FAISS vector store under `rag/vector_store/index.faiss`
- ui/: FastAPI + Streamlit frontends (`ui/api.py`, `ui/app.py`)
- tools/: Helper tools used by agents and workflows
- workflows/: High-level conversation/workflow implementations
- data/pdfs/: Example PDFs used for retrieval
- database/: Database helper (Mongo connector)
- tests/: Unit, integration and performance tests
- evaluation/: Evaluation scripts (RAGAS evaluation)
- seed/: Scripts to populate initial data

## Notable Files

- [requirements.txt](requirements.txt)
- [ui/api.py](ui/api.py)
- [ui/app.py](ui/app.py)
- [seed/seed.py](seed/seed.py)
- [rag/retriever.py](rag/retriever.py)

## Data & Indexes

FAISS indexes are stored under `rag/vector_store` and `workflows/ticket_vectordb`. If you add new documents you can re-run the retriever/index building logic in `rag/retriever.py`.

## Running Locally (development tips)

- Keep your virtualenv active while developing
- Run unit tests frequently: `pytest tests/unit`
- Integration tests require services (DB, vectorstore) to be available

## Contributing

Contributions are welcome. Open issues or PRs for enhancements, bug fixes, or test improvements.

## License

This project is provided for assessment and learning. No license specified.
