# Tests

Run `python -m unittest discover -s tests -v` after installing the package.
Checks cover distribution metadata, package imports, and Euler/RK4 integration:
analytical reference cases, convergence order, state preservation, and invalid
inputs. These unit checks do not constitute a completed research experiment.

Future library tests should cover analytical reference cases, convergence,
invariants, and invalid inputs as appropriate. Keep tests deterministic and
small enough for CI. Long parameter sweeps belong in experiments.
