# Robot Data Analysis V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first importable version of the offline robot data analysis library.

**Architecture:** Move reusable logic from scripts into a `robot_data_analysis` package and keep executable workflows in `scripts`. The first implementation keeps ROS2 dependencies lazy so CSV analysis works in the `data_analysis` conda environment.

**Tech Stack:** Python 3.12, pandas, numpy, matplotlib-ready package layout, pytest, argparse.

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, pytest configuration, CLI entry point.
- Create `README.md`: quick start and project layout.
- Create `robot_data_analysis/core/schema.py`: sensor type and standard column constants.
- Create `robot_data_analysis/core/time.py`: timestamp normalization and sampling helpers.
- Create `robot_data_analysis/core/errors.py`: typed library exceptions.
- Create `robot_data_analysis/analysis/quality.py`: DataFrame quality summary.
- Create `robot_data_analysis/io/csv.py`: CSV read/write helpers.
- Create `robot_data_analysis/io/dataset.py`: experiment directory scanner and loader.
- Create `robot_data_analysis/ros/flatten.py`: ROS-like message flattening.
- Create `robot_data_analysis/ros/bag_exporter.py`: ROS2 bag to CSV exporter with lazy ROS imports.
- Create `robot_data_analysis/sensors/gnss/novatel.py`: NovAtel `bestgnsspos` parser.
- Create placeholder packages for `imu`, `ins`, and `visualization` so future modules have stable locations.
- Create `robot_data_analysis/cli/main.py`: `summary`, `parse-bestgnsspos`, and `export-bag` commands.
- Use `scripts/run_export_bag.py` for IDE-oriented bag export.
- Create tests under `tests/`.

## Tasks

### Task 1: Project Metadata and Documentation

- [ ] Add `.gitignore`, `pyproject.toml`, and `README.md`.
- [ ] Verify package metadata can be parsed with `python -m pip install -e . --dry-run` or a targeted import after implementation.
- [ ] Commit documentation and metadata when stable.

### Task 2: Test-First Core Utilities

- [ ] Write failing tests for ROS message flattening, timestamp conversion, and quality summaries.
- [ ] Run `pytest` and confirm failures are due to missing package modules.
- [ ] Implement core modules and rerun targeted tests until green.

### Task 3: Test-First GNSS Parser and Dataset Loader

- [ ] Write failing tests for `parse_bestgnsspos_csv` and experiment directory scanning.
- [ ] Run `pytest` and confirm failures are due to missing parser/loader behavior.
- [ ] Implement parser and loader.
- [ ] Rerun targeted tests until green.

### Task 4: CLI and Compatibility Wrappers

- [ ] Write tests or smoke commands for importable CLI functions.
- [ ] Implement `robot_data_analysis.cli.main`.
- [ ] Replace existing scripts with thin wrappers that call the package.
- [ ] Verify existing command style remains available.

### Task 5: Final Verification and Commit

- [ ] Run `pytest`.
- [ ] Run `python -m robot_data_analysis.cli.main --help`.
- [ ] Run `python -m robot_data_analysis.cli.main summary .`.
- [ ] Check `git status --short`.
- [ ] Commit the first version with a concise message.
