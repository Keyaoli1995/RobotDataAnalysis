"""Plotting helpers for IMU analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from robot_data_analysis.core.errors import MissingColumnsError
from robot_data_analysis.core.schema import TIMESTAMP_COLUMN

DEFAULT_IMU_AXES = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]


def build_time_tick_labels(
    comparison: pd.DataFrame,
    max_ticks: int = 8,
    line_break: str = "\n",
) -> tuple[list[float], list[str]]:
    """Build elapsed-time/readable-time tick labels for comparison plots."""

    if comparison.empty:
        return [], []

    tick_rows = comparison.iloc[_tick_indices(len(comparison), max_ticks)]
    tick_values = [float(value) for value in tick_rows["time_seconds"]]
    readable_times = pd.to_datetime(tick_rows["readable_time"])
    tick_labels = [
        f"{elapsed:.3f} s{line_break}{readable.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}"
        for elapsed, readable in zip(tick_values, readable_times)
    ]
    return tick_values, tick_labels


def resolve_imu_axes(axes: list[str] | tuple[str, ...] | None = None) -> list[str]:
    """Return configured IMU axes or the default six-axis output list."""

    return list(axes) if axes else DEFAULT_IMU_AXES.copy()


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

    tick_values, tick_labels = build_time_tick_labels(comparison, line_break="\n")
    axes[1].set_xticks(tick_values)
    axes[1].set_xticklabels(tick_labels, rotation=0, ha="center")
    axes[1].set_xlabel("elapsed time / readable timestamp")

    fig.suptitle("IMU acceleration norm comparison")
    fig.savefig(destination, dpi=150)
    plt.close(fig)

    return destination


def plot_interactive_accel_norm_comparison(
    comparison: pd.DataFrame,
    output_path: str | Path,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
) -> Path:
    """Write an interactive HTML acceleration norm comparison plot."""

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    time_col = "time_seconds"
    left_norm_col = f"{left_label}_accel_norm"
    right_norm_col = f"{right_label}_accel_norm"
    readable_text = pd.to_datetime(comparison["readable_time"]).dt.strftime("%Y-%m-%d %H:%M:%S.%f").str[:-3]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Acceleration norm", "Acceleration norm delta"),
    )

    customdata = pd.DataFrame({"readable_time": readable_text})
    hovertemplate = "elapsed=%{x:.6f} s<br>time=%{customdata[0]}<br>value=%{y:.6f}<extra></extra>"
    fig.add_trace(
        go.Scatter(
            x=comparison[time_col],
            y=comparison[left_norm_col],
            customdata=customdata,
            mode="lines",
            name=left_label,
            hovertemplate=hovertemplate,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=comparison[time_col],
            y=comparison[right_norm_col],
            customdata=customdata,
            mode="lines",
            name=right_label,
            hovertemplate=hovertemplate,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=comparison[time_col],
            y=comparison["accel_norm_delta"],
            customdata=customdata,
            mode="lines",
            name=f"{left_label} - {right_label}",
            hovertemplate=hovertemplate,
        ),
        row=2,
        col=1,
    )

    tick_values, tick_labels = build_time_tick_labels(comparison, line_break="<br>")
    fig.update_xaxes(
        title_text="elapsed time / readable timestamp",
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_labels,
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="accel norm", row=1, col=1)
    fig.update_yaxes(title_text=f"{left_label} - {right_label}", row=2, col=1)
    fig.update_layout(
        title="IMU acceleration norm comparison",
        hovermode="x unified",
        height=760,
    )
    fig.write_html(destination, include_plotlyjs=True)
    return destination


def plot_imu_axes_outputs(
    imu_data: pd.DataFrame,
    output_path: str | Path,
    axes: list[str] | tuple[str, ...] | None = None,
    title: str = "IMU outputs",
) -> Path:
    """Write an interactive multi-axis IMU output plot."""

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    axis_columns = resolve_imu_axes(axes)
    _require_imu_plot_columns(imu_data, axis_columns)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    plot_data = imu_data.copy()
    plot_data["time_seconds"] = (
        pd.to_numeric(plot_data[TIMESTAMP_COLUMN], errors="coerce") - plot_data[TIMESTAMP_COLUMN].iloc[0]
    ) / 1_000_000_000
    readable_text = pd.to_datetime(plot_data["readable_time"]).dt.strftime("%Y-%m-%d %H:%M:%S.%f").str[:-3]
    customdata = pd.DataFrame({"readable_time": readable_text})

    fig = make_subplots(
        rows=len(axis_columns),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=min(0.04, 0.2 / max(len(axis_columns), 1)),
        subplot_titles=axis_columns,
    )
    hovertemplate = "elapsed=%{x:.6f} s<br>time=%{customdata[0]}<br>value=%{y:.6f}<extra></extra>"

    for row_index, axis_column in enumerate(axis_columns, start=1):
        fig.add_trace(
            go.Scatter(
                x=plot_data["time_seconds"],
                y=plot_data[axis_column],
                customdata=customdata,
                mode="lines",
                name=axis_column,
                hovertemplate=hovertemplate,
            ),
            row=row_index,
            col=1,
        )
        fig.update_yaxes(title_text=axis_column, row=row_index, col=1)

    tick_values, tick_labels = build_time_tick_labels(plot_data, line_break="<br>")
    fig.update_xaxes(
        title_text="elapsed time / readable timestamp",
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_labels,
        row=len(axis_columns),
        col=1,
    )
    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=max(360, 180 * len(axis_columns)),
        showlegend=False,
    )
    fig.write_html(destination, include_plotlyjs=True)
    return destination


def build_time_interval_series(imu_data: pd.DataFrame, label: str) -> pd.DataFrame:
    """Build consecutive timestamp interval rows for plotting."""

    _require_time_plot_columns(imu_data)
    sorted_data = imu_data.sort_values(TIMESTAMP_COLUMN).reset_index(drop=True)
    timestamps = pd.to_numeric(sorted_data[TIMESTAMP_COLUMN], errors="coerce")
    intervals = timestamps.diff()
    interval_rows = sorted_data.loc[intervals.notna(), [TIMESTAMP_COLUMN, "readable_time"]].copy()
    interval_rows["time_seconds"] = (
        pd.to_numeric(interval_rows[TIMESTAMP_COLUMN], errors="coerce") - timestamps.iloc[0]
    ) / 1_000_000_000
    interval_rows["interval_seconds"] = intervals.dropna().to_numpy() / 1_000_000_000
    interval_rows["source"] = label
    return interval_rows[["time_seconds", "readable_time", "interval_seconds", "source"]].reset_index(drop=True)


def plot_interactive_time_intervals(
    left_imu: pd.DataFrame,
    right_imu: pd.DataFrame,
    output_path: str | Path,
    left_label: str = "rawimusx",
    right_label: str = "tcp_raw_imu",
) -> Path:
    """Write an interactive HTML plot comparing two IMU timestamp intervals."""

    import plotly.graph_objects as go

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    left_intervals = build_time_interval_series(left_imu, left_label)
    right_intervals = build_time_interval_series(right_imu, right_label)

    fig = go.Figure()
    for label, intervals in ((left_label, left_intervals), (right_label, right_intervals)):
        readable_text = pd.to_datetime(intervals["readable_time"]).dt.strftime("%Y-%m-%d %H:%M:%S.%f").str[:-3]
        customdata = pd.DataFrame({"readable_time": readable_text})
        fig.add_trace(
            go.Scatter(
                x=intervals["time_seconds"],
                y=intervals["interval_seconds"],
                customdata=customdata,
                mode="lines+markers",
                marker={"size": 4},
                name=label,
                hovertemplate=(
                    "elapsed=%{x:.6f} s<br>"
                    "time=%{customdata[0]}<br>"
                    "interval=%{y:.9f} s<extra></extra>"
                ),
            )
        )

    combined = pd.concat([left_intervals, right_intervals], ignore_index=True)
    tick_values, tick_labels = build_time_tick_labels(combined, line_break="<br>")
    fig.update_xaxes(
        title_text="elapsed time / readable timestamp",
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_labels,
    )
    fig.update_yaxes(title_text="interval (s)")
    fig.update_layout(
        title="IMU timestamp intervals",
        hovermode="x unified",
        height=620,
    )
    fig.write_html(destination, include_plotlyjs=True)
    return destination


def _tick_indices(row_count: int, max_ticks: int) -> list[int]:
    if row_count <= 0:
        return []
    if row_count <= max_ticks:
        return list(range(row_count))

    step = (row_count - 1) / (max_ticks - 1)
    indices = [round(index * step) for index in range(max_ticks)]
    return sorted(set(indices))


def _require_imu_plot_columns(imu_data: pd.DataFrame, axes: list[str]) -> None:
    required_columns = [TIMESTAMP_COLUMN, "readable_time", *axes]
    missing_columns = [column for column in required_columns if column not in imu_data.columns]
    if missing_columns:
        raise MissingColumnsError(missing_columns)


def _require_time_plot_columns(imu_data: pd.DataFrame) -> None:
    missing_columns = [column for column in [TIMESTAMP_COLUMN, "readable_time"] if column not in imu_data.columns]
    if missing_columns:
        raise MissingColumnsError(missing_columns)
