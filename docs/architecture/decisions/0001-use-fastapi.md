# ADR 0001: Use FastAPI for Backend

## Status
Accepted

## Context
We needed to choose a Python web framework for the backend API. The main candidates were:
- FastAPI
- Django REST Framework
- Flask

## Decision
We chose **FastAPI** as the backend framework.

## Rationale
- **Performance**: FastAPI is one of the fastest Python frameworks, built on Starlette and Pydantic
- **Type Safety**: Native support for Python type hints with automatic validation
- **Auto Documentation**: Automatic OpenAPI/Swagger documentation generation
- **Async Support**: First-class async/await support for I/O-bound operations
- **Modern Python**: Leverages modern Python features (3.8+)
- **WebSocket Support**: Built-in WebSocket support for real-time features

## Consequences
- Team needs familiarity with async Python patterns
- Pydantic v2 is used for data validation
- ASGI server (uvicorn) required instead of WSGI
