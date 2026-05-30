# Contributing to Lumidoc

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Run `bash scripts/bootstrap.sh` for first-time setup
4. Create a feature branch: `git checkout -b feature/your-feature`

## Development Workflow

1. Make your changes
2. Write/update tests
3. Run linting and tests locally
4. Commit with conventional commit messages
5. Push and create a Pull Request

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user authentication
fix: resolve login redirect issue
docs: update API documentation
chore: update dependencies
refactor: simplify auth middleware
test: add unit tests for auth service
```

## Code Style

### Frontend (TypeScript/React)
- ESLint + Prettier for formatting
- Follow existing component patterns
- Use TypeScript strict mode

### Backend (Python)
- Ruff for linting and formatting
- Type hints required for all functions
- Follow existing service patterns

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure CI passes
4. Request review from code owners
5. Squash merge when approved

## Reporting Issues

Use GitHub Issues with the appropriate template:
- Bug Report: for bugs and errors
- Feature Request: for new features
