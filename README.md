# Relativistic Dark-Fluid Hypothesis

A computational research repository asking whether nonlinear stretching and
vorticity in a relativistic fluid can contribute to accelerated cosmological
expansion. The hypothesis is unverified; the research plan prioritizes attempts
to falsify it.

**Status:** Euler and classical RK4 integrators and the harmonic oscillator
experiment are implemented and analytically checked. The first experiment includes
CSV/JSON output, diagnostic figures, and measured convergence results. See the
[experiment record](experiments/001_harmonic_oscillator/record.md).

## Getting started

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell.
The import name is `darkfluid`; the distribution name is
`dark-fluid-hypothesis`. The core library has no runtime dependencies. Install `.[plots]` to run the
oscillator experiment and generate figures.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`src/darkfluid/`](src/darkfluid/) | Reusable library, including Euler and RK4 steps |
| [`tests/`](tests/) | Package checks and future library validation |
| [`docs/research-plan.md`](docs/research-plan.md) | Long-term scientific roadmap |
| [`docs/hypothesis.md`](docs/hypothesis.md) | Scope and evidence requirements |
| [`docs/experiment-log.md`](docs/experiment-log.md) | Research status and future result index |
| [`docs/development.md`](docs/development.md) | Architecture, checks, and artifact conventions |
| [`docs/templates/`](docs/templates/) | Research record templates |
| [`docs/math-notes/`](docs/math-notes/) | Mathematics study guide |
| [`docs/derivations/`](docs/derivations/) | Derivation conventions |
| [`experiments/`](experiments/) | Experiment runners and research records |
| [`notebooks/`](notebooks/) | Future exploratory analysis |

The architecture in the research plan is a target, not a list of implemented
capabilities. Physics subpackages will be introduced with validated code.
See [CONTRIBUTING.md](CONTRIBUTING.md) before making changes.
