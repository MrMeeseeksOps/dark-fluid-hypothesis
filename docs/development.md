# Development guide

## Architecture

`src/darkfluid/` contains reusable library code. It must not import experiment
scripts or notebooks, start simulations during import, or write output on import.
Experiment-specific initial conditions, parameter sweeps, and plots belong in
`experiments/` when those experiments are developed.

Euler and classical RK4 expose `euler_step(f, t, y, dt)` and
`rk4_step(f, t, y, dt)` from `darkfluid.integrators`. Both operate on finite real
state sequences and return tuples; callers own the simulation loop and storage.

The planned mechanics, fluids, relativity, and cosmology packages will be added
when their interfaces and validation cases are defined. Empty solver modules
do not constitute an implemented API.

## Local workflow

Install the development extra as described in the root README. Use
`python -m ruff format .` to format maintained Python code. Ruff excludes
experiments and notebooks; CI does not run them.

Tests use the standard-library `unittest` runner. CI checks Python 3.11 through
3.14, builds a source distribution and wheel, and checks imports after installing
the wheel in a separate environment. Run the same checks locally before a PR.

Packaging follows the [setuptools pyproject configuration guide](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).
CI uses [GitHub's Python workflow guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).

## Research artifacts and reproducibility

Place generated runs under `outputs/<experiment-id>/<run-id>/`; this directory
is ignored by Git. Commit small, curated summaries and links to retained artifacts
in the experiment record. Ignored outputs need separate durable storage before
they can serve as reproducible evidence.

For each future run, record:

- Git revision and whether the working tree had uncommitted changes.
- Exact invocation, configuration, initial conditions, and random seeds.
- Python version, dependency versions (`python -m pip freeze`), and relevant platform details.
- Units, coordinate and tensor conventions, numerical method, and resolution.
- Validation results, error estimates, and artifact locations or checksums.

Dependency ranges support development; they do not freeze a research environment.
Keep the resolved environment with each retained run.

## Documentation responsibilities

Keep the research plan as the roadmap. Use the experiment log for actual status
and the templates for future records. Mark missing evidence explicitly rather
than filling result sections with expected outcomes.
