# Contributing to eavt-helper

Thanks for your interest in contributing! This is a small, focused project — please keep PRs small and focused as well.

## Development setup

```bash
git clone https://github.com/vmjulio/eavt-helper.git
cd eavt-helper
pip install --editable ".[dev]"
```

## Running the checks locally

Before opening a PR, make sure all of these pass:

```bash
make lint       # ruff check
make typecheck  # mypy strict
make test       # pytest
```

`make format` will auto-fix lint and formatting issues.

## Pull requests

- Branch from `main`.
- Keep each PR focused on one logical change.
- Add tests for new behavior or bug fixes — see existing tests in `tests/` for style.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `build:`, `ci:`.
- CI must be green before review.

## Reporting bugs

Open an issue with:
- What you ran (the exact CLI command)
- What you expected
- What actually happened (including any traceback)
- Your Python version and OS

A minimal reproducing CSV is enormously helpful.
