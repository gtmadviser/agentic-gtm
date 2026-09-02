# Contributing

Contributions are welcome. Open an issue before a large change.

## Skills

Every skill under `skills/<name>/` has:

- `SKILL.md` with frontmatter (`name`, `description` with "use for / do not use for"), then: purpose, when to use, inputs, numbered procedure, hard rules with numbers, checklist, output contract, failure modes, references. 90-250 lines.
- `references/` with 2-7 focused files (templates, thresholds, worked examples on fictional companies).
- `agents/openai.yaml` with `display_name` and `short_description`.

Rules for skill text: imperative, numeric, testable. No em dashes. Fictional examples only, on `.example` domains. No real company, person, domain, phone number, campaign ID or customer figure. Never attribute a number to an identifiable engagement.

## Code

Keep deterministic behavior and provider details in the CLI, not in skills. Add a synthetic adapter-contract test for each API change and a provider note under `docs/providers/` for each gotcha.

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest
uv run python scripts/validate_release.py
uv run python scripts/scan_public_release.py .
```

Maintainers additionally run the scan with a private deny list of client terms before every release.

Never submit real contact data, customer names, credentials, campaign copy, or provider response recordings. Fixtures must be wholly fictional.
