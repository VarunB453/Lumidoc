# Architecture Overview

## System Architecture

Lumidoc is a full-stack application built with:
- **Frontend**: React + Vite + TypeScript + TailwindCSS
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **Vector Store**: FAISS
- **Reverse Proxy**: Nginx

## High-Level Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    Nginx    │────▶│   FastAPI   │
│  (React)    │     │  (Reverse   │     │  (Backend)  │
└─────────────┘     │   Proxy)    │     └──────┬──────┘
                    └─────────────┘            │
                                               ├──▶ PostgreSQL
                                               ├──▶ Redis
                                               ├──▶ FAISS
                                               └──▶ Celery Workers
```

## Key Design Decisions
See the `decisions/` directory for Architecture Decision Records (ADRs).

## Diagrams
See the `diagrams/` directory for detailed system diagrams.
