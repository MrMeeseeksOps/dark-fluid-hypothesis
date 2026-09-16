# Contributing

Follow the setup in [README.md](README.md) and the workflow in
[docs/development.md](docs/development.md).

## Scope changes clearly

- Separate repository infrastructure, reusable numerical code, and experiments.
- Add dependencies only when implemented functionality needs them.
- Describe the problem, assumptions, resulting behavior, and validation in each PR.
- Keep generated datasets and large output files out of Git.
- Record unsuccessful and inconclusive research outcomes alongside positive ones.

## Before submitting

```sh
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
python -m build
```

Update documentation when behavior changes. For numerical work, describe units,
state conventions, validity limits, and quantitative error tolerances. Passing
software checks alone does not establish physical validity.
