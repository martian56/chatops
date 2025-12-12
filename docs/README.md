# Documentation

This directory contains the MkDocs documentation for ChatOps.

## Building Locally

### Prerequisites

- Python 3.12+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Serve documentation locally
mkdocs serve
```

The documentation will be available at `http://localhost:8000`

### Build Static Site

```bash
mkdocs build
```

The static site will be generated in the `site/` directory.

## Documentation Structure

- `index.md` - Homepage
- `getting-started/` - Getting started guides
- `architecture/` - System architecture
- `api/` - API documentation
- `agent/` - Agent documentation
- `frontend/` - Frontend documentation
- `technologies/` - Technology stack
- `deployment/` - Deployment guides
- `contributing/` - Contribution guidelines

## Deployment

Documentation is automatically deployed to Cloudflare Pages on push to `main` branch.

See `.github/workflows/docs-deploy.yml` for deployment configuration.

## Contributing

When adding or updating documentation:

1. Edit the relevant `.md` file
2. Test locally with `mkdocs serve`
3. Commit and push
4. Documentation will be automatically deployed

