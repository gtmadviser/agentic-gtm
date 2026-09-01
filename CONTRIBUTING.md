# Contributing

Contributions are welcome. Open an issue before a large change. Keep Agent Skills thin, put deterministic behavior and provider details in the CLI, and add synthetic adapter-contract tests for each API change.

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest
uv run python scripts/scan_public_release.py .
```

Never submit real contact data, customer names, credentials, campaign copy, or provider response recordings. Fixtures must be wholly fictional.
