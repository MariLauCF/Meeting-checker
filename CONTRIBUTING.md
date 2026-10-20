# Contributing to Meeting Checker

Thanks for helping improve the project!

## Workflow

1. Fork the repository and create a branch: `git checkout -b feature/my-change`
2. Make your change. Keep commits small and use clear messages (`feat:`, `fix:`, `docs:`).
3. Run the checks locally:
   ```bash
   pip install -r app/requirements.txt
   python -m unittest discover -s tests -v
   kubectl kustomize k8s/ > /dev/null
   ```
4. Open a Pull Request describing *what* and *why*. CI must pass before merge.

## Guidelines

- **Code**: Python 3.12, type hints where useful, docstrings for public functions, business logic stays in `app/checker.py` (pure and unit-testable).
- **Metrics**: use `snake_case`, a unit suffix where relevant (`_seconds`, `_total`), and document new metrics in the README.
- **Alerts**: every alert needs `severity`, `summary` and `description`.
- **Secrets**: never commit real webhook URLs, passwords or tokens.

## Reporting issues

Open a GitHub issue with steps to reproduce, expected vs. actual behaviour, and relevant logs.

By contributing you agree your work is released under the [MIT License](LICENSE.md).
