# Finance Data Modeling + RAG Agent Portfolio

## What this repo is
A compact portfolio project showing:
- Financial data modeling with medallion style layers and PII masking concepts
- A RAG and agent style workflow over curated finance data

## Local stack
- Database: DuckDB
- Transformations: dbt
- API: FastAPI
- UI: Streamlit
- Vector store: FAISS
- Embeddings: small open source model
- Orchestration: Python scripts (upgrade to Prefect later)

## Repo structure
- `data/` raw and curated local datasets (keep large files out of git)
- `dbt/` dbt project for bronze/silver/gold models
- `src/` python modules for ingestion, masking, embeddings, retrieval
- `notebooks/` exploration and experiments
- `app/` FastAPI and Streamlit apps
- `docs/` extra docs and diagrams

## Phase 0 deliverables
- Clean repo skeleton
- Basic README
