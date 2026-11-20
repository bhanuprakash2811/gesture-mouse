# Project documentation

Start with the root [README](../README.md) for features, installation, and running the application.

## Walkthrough

1. [Quick start](guides/QUICKSTART.md) — environment setup, dependencies, and running the app.
2. [Project summary](guides/PROJECT_SUMMARY.md) — modules, data flow, and gesture mappings.
3. [Evaluation documentation](evaluation/DOCUMENTATION_INDEX.md) — evaluation tools, reports, and result interpretation.

## Script entry points

Run these commands from the project root:

```bash
python -m scripts.training.collect_data
python -m scripts.training.train_model
python -m scripts.training.train_with_evaluation
python -m scripts.evaluation.quick_evaluation
python -m scripts.evaluation.compare_with_baseline
python -m scripts.evaluation.benchmark_speed
python -m scripts.evaluation.evaluate_model
python -m scripts.evaluation.test_gestures
python -m scripts.maintenance.verify_installation
```

The application itself is launched with `python src/main.py --mode hand` or `--mode glove`.

## Top-level folders

- `src/` — application code.
- `scripts/` — training, evaluation, and maintenance commands.
- `tests/` — automated unit tests.
- `docs/` — user guides and evaluation references.
- `data/`, `models/`, and `results/` — datasets, trained models, and generated outputs.
- `cpp/` — optional C++ extension location; it is empty in this workspace.
- Large ZIP archives and local/generated data are intentionally excluded from the public repository.

All commands above expect the working directory to be the project root.
