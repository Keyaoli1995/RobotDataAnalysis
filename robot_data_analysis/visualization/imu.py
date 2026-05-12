"""Plotting helpers for IMU analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def plot_accel_norm_comparison(
    comparison: pd.DataFrame,
    output_path: str | Path,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
) -> Path:
    """Plot two acceleration norm series and their difference."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    time_col = "time_seconds"
    left_norm_col = f"{left_label}_accel_norm"
    right_norm_col = f"{right_label}_accel_norm"

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, constrained_layout=True)

    axes[0].plot(comparison[time_col], comparison[left_norm_col], label=left_label, linewidth=1.2)
    axes[0].plot(comparison[time_col], comparison[right_norm_col], label=right_label, linewidth=1.2)
    axes[0].set_ylabel("accel norm")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(comparison[time_col], comparison["accel_norm_delta"], color="tab:red", linewidth=1.0)
    axes[1].axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    axes[1].set_xlabel("time from start (s)")
    axes[1].set_ylabel(f"{left_label} - {right_label}")
    axes[1].grid(True, alpha=0.3)

    fig.suptitle("IMU acceleration norm comparison")
    fig.savefig(destination, dpi=150)
    plt.close(fig)

    return destination
