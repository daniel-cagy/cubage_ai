#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import FuncFormatter

ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "tests" / "results"

IMAGE_PROCESSING_MODES = ["original", "resized", "quantized"]
DIMENSION_MEASURES = ["comprimento", "largura", "altura"]
MEASURES = [*DIMENSION_MEASURES, "peso"]
WEIGHT_THRESHOLDS_GRAMS = [25, 50, 100]
MODE_COLORS = {
    "original": "#4B5563",
    "resized": "#00A868",
    "quantized": "#2563EB",
}
IMAGE_COUNT_BASE = 1
IMAGE_COUNT_COMPARISON = 2

MODEL_PRICES_PER_1M = {
    "gpt-5.5": {"input": 5.00, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

SUMMARY_FIELDS = [
    "group",
    "runs",
    "successes",
    "failures",
    "success_rate",
    "mean_duration_seconds",
    "mean_image_preprocessing_seconds",
    "mean_all_interval_hit_rate",
    "mean_dimension_interval_hit_rate",
    "mean_abs_percent_error_all",
    "mean_abs_percent_error_dimensions",
    "mean_max_abs_percent_error_all",
    "mean_input_tokens",
    "mean_output_tokens",
    "mean_total_tokens",
    "mean_estimated_cost",
    "mean_calculated_cost_usd",
    "total_input_tokens",
    "total_output_tokens",
    "total_tokens",
    "total_input_cost_usd",
    "total_output_cost_usd",
    "total_calculated_cost_usd",
    "cost_benefit_score",
    "cost_benefit_score_dimensions",
    "cost_benefit_score_all",
    "weight_mean_absolute_error_g",
    "weight_median_absolute_error_g",
    "weight_within_25g_rate",
    "weight_within_50g_rate",
    "weight_within_100g_rate",
    "weight_within_20_percent_rate",
    "mean_original_bytes",
    "mean_final_bytes",
    "mean_byte_reduction_percent",
    "mean_final_megapixels",
]

MEASURE_SUMMARY_FIELDS = [
    "group",
    "measure",
    "runs",
    "valid_error_count",
    "mean_percent_error",
    "median_percent_error",
    "mean_absolute_error",
    "median_absolute_error",
    "mean_signed_error",
    "mean_expected",
    "mean_estimate",
    "interval_hits",
    "interval_hit_rate",
    "mean_absolute_error_grams",
    "median_absolute_error_grams",
    "within_25g_rate",
    "within_50g_rate",
    "within_100g_rate",
    "within_20_percent_rate",
]

IMAGE_COUNT_DELTA_FIELDS = [
    "group",
    "model",
    "image_processing_mode",
    "runs_1_image",
    "runs_2_images",
    "success_rate_1_image",
    "success_rate_2_images",
    "delta_success_rate",
    "error_dimensions_1_image",
    "error_dimensions_2_images",
    "delta_error_dimensions",
    "relative_change_error_dimensions_percent",
    "error_all_1_image",
    "error_all_2_images",
    "delta_error_all",
    "relative_change_error_all_percent",
    "interval_dimensions_1_image",
    "interval_dimensions_2_images",
    "delta_interval_dimensions",
    "interval_all_1_image",
    "interval_all_2_images",
    "delta_interval_all",
    "height_error_1_image",
    "height_error_2_images",
    "delta_height_error",
    "relative_change_height_error_percent",
    "weight_error_g_1_image",
    "weight_error_g_2_images",
    "delta_weight_error_g",
    "tokens_1_image",
    "tokens_2_images",
    "delta_tokens",
    "relative_change_tokens_percent",
    "cost_1_image",
    "cost_2_images",
    "delta_cost",
    "relative_change_cost_percent",
]

MEASURE_IMAGE_COUNT_DELTA_FIELDS = [
    "group",
    "model",
    "image_processing_mode",
    "measure",
    "mean_percent_error_1_image",
    "mean_percent_error_2_images",
    "delta_mean_percent_error",
    "relative_change_mean_percent_error_percent",
    "interval_hit_rate_1_image",
    "interval_hit_rate_2_images",
    "delta_interval_hit_rate",
]

MEAN_SOURCE_COLUMNS = {
    "mean_duration_seconds": "duration_seconds",
    "mean_image_preprocessing_seconds": "image_preprocessing_seconds",
    "mean_all_interval_hit_rate": "all_interval_hit_rate",
    "mean_dimension_interval_hit_rate": "dimension_interval_hit_rate",
    "mean_abs_percent_error_all": "mean_abs_percent_error_all",
    "mean_abs_percent_error_dimensions": "mean_abs_percent_error_dimensions",
    "mean_max_abs_percent_error_all": "max_abs_percent_error_all",
    "mean_input_tokens": "input_tokens",
    "mean_output_tokens": "output_tokens",
    "mean_total_tokens": "total_tokens",
    "mean_estimated_cost": "estimated_cost",
    "mean_calculated_cost_usd": "calculated_cost_usd",
    "mean_original_bytes": "original_bytes",
    "mean_final_bytes": "final_bytes",
    "mean_byte_reduction_percent": "byte_reduction_percent",
    "mean_final_megapixels": "final_megapixels",
}

TOTAL_SOURCE_COLUMNS = {
    "total_input_tokens": "input_tokens",
    "total_output_tokens": "output_tokens",
    "total_tokens": "total_tokens",
    "total_input_cost_usd": "input_cost_usd",
    "total_output_cost_usd": "output_cost_usd",
    "total_calculated_cost_usd": "calculated_cost_usd",
}

MEASURE_NUMERIC_COLUMNS = [
    f"{measure}_{suffix}"
    for measure in MEASURES
    for suffix in ("expected", "estimate", "signed_error", "absolute_error", "percent_error")
]
MEASURE_INTERVAL_COLUMNS = [f"{measure}_interval_hit" for measure in MEASURES]
NUMERIC_COLUMNS = sorted(
    set(MEAN_SOURCE_COLUMNS.values())
    | set(TOTAL_SOURCE_COLUMNS.values())
    | set(MEASURE_NUMERIC_COLUMNS)
    | {"peso_absolute_error_grams", "image_count"}
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera tabelas e gráficos a partir de um CSV de avaliação."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=None,
        help="CSV de avaliação. Se omitido, usa o evaluation_*.csv mais recente em tests/results.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Diretório de saída. Se omitido, cria tests/results/analysis_<nome_do_csv>.",
    )
    return parser.parse_args()


def latest_evaluation_csv() -> Path:
    candidates = sorted(RESULTS_DIR.glob("evaluation_*.csv"), key=lambda path: path.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError("Nenhum CSV evaluation_*.csv encontrado em tests/results.")
    return candidates[-1]


def load_results(input_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    if "image_count" not in df.columns:
        df["image_count"] = IMAGE_COUNT_BASE

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
        else:
            df[column] = pd.Series(pd.NA, index=df.index, dtype="Float64")

    for column in MEASURE_INTERVAL_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype(str).str.lower().eq("true")
        else:
            df[column] = False

    if "success" not in df.columns:
        df["success"] = False

    df["image_count"] = pd.to_numeric(df["image_count"], errors="coerce").fillna(IMAGE_COUNT_BASE).astype(int)
    df["success_bool"] = df["success"].astype(str).str.lower().eq("true")
    add_weight_error_columns(df)
    add_cost_columns(df)
    return df


def add_weight_error_columns(df: pd.DataFrame) -> None:
    df["peso_absolute_error_grams"] = df["peso_absolute_error_grams"].fillna(
        df["peso_absolute_error"] * 1000
    )

    for threshold in WEIGHT_THRESHOLDS_GRAMS:
        df[f"peso_error_within_{threshold}g"] = df["peso_absolute_error_grams"].le(threshold).fillna(False)

    df["peso_error_within_20_percent"] = df["peso_percent_error"].le(20).fillna(False)


def add_cost_columns(df: pd.DataFrame) -> None:
    df["input_price_per_1m"] = df["model"].map(
        lambda model: MODEL_PRICES_PER_1M.get(str(model), {}).get("input")
    )
    df["output_price_per_1m"] = df["model"].map(
        lambda model: MODEL_PRICES_PER_1M.get(str(model), {}).get("output")
    )
    df["input_cost_usd"] = df["input_tokens"] / 1_000_000 * df["input_price_per_1m"]
    df["output_cost_usd"] = df["output_tokens"] / 1_000_000 * df["output_price_per_1m"]
    df["calculated_cost_usd"] = df["input_cost_usd"] + df["output_cost_usd"]


def numeric_sum(series: pd.Series) -> float | Any:
    if series.notna().any():
        return series.sum()
    return pd.NA


def boolean_rate(series: pd.Series) -> float | Any:
    if len(series):
        return series.astype(bool).mean()
    return pd.NA


def iter_groups(df: pd.DataFrame, group_columns: list[str]):
    if not group_columns:
        yield ("all",), df
        return

    for key, group in df.groupby(group_columns, dropna=False, sort=True):
        if not isinstance(key, tuple):
            key = (key,)
        yield key, group


def build_summary(df: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    rows = []

    for key, group in iter_groups(df, group_columns):
        successful = group[group["success_bool"]]
        runs = len(group)
        successes = int(group["success_bool"].sum())
        row: dict[str, Any] = {
            "group": " | ".join(str(value) for value in key),
            "runs": runs,
            "successes": successes,
            "failures": runs - successes,
            "success_rate": successes / runs if runs else 0,
        }

        for output_column, source_column in MEAN_SOURCE_COLUMNS.items():
            row[output_column] = successful[source_column].mean() if not successful.empty else pd.NA

        for output_column, source_column in TOTAL_SOURCE_COLUMNS.items():
            row[output_column] = numeric_sum(successful[source_column]) if not successful.empty else pd.NA

        weight_error_grams = successful["peso_absolute_error_grams"].dropna() if not successful.empty else pd.Series(dtype="float64")
        row["weight_mean_absolute_error_g"] = weight_error_grams.mean() if not weight_error_grams.empty else pd.NA
        row["weight_median_absolute_error_g"] = weight_error_grams.median() if not weight_error_grams.empty else pd.NA
        for threshold in WEIGHT_THRESHOLDS_GRAMS:
            row[f"weight_within_{threshold}g_rate"] = (
                boolean_rate(successful[f"peso_error_within_{threshold}g"]) if not successful.empty else pd.NA
            )
        row["weight_within_20_percent_rate"] = (
            boolean_rate(successful["peso_error_within_20_percent"]) if not successful.empty else pd.NA
        )

        hit_rate_all = row.get("mean_all_interval_hit_rate")
        hit_rate_dimensions = row.get("mean_dimension_interval_hit_rate")
        mean_cost = row.get("mean_calculated_cost_usd")
        if pd.notna(mean_cost) and mean_cost > 0:
            row["cost_benefit_score_all"] = (
                hit_rate_all / mean_cost if pd.notna(hit_rate_all) else pd.NA
            )
            row["cost_benefit_score_dimensions"] = (
                hit_rate_dimensions / mean_cost if pd.notna(hit_rate_dimensions) else pd.NA
            )
            row["cost_benefit_score"] = row["cost_benefit_score_dimensions"]
        else:
            row["cost_benefit_score"] = pd.NA
            row["cost_benefit_score_dimensions"] = pd.NA
            row["cost_benefit_score_all"] = pd.NA

        rows.append(row)

    return pd.DataFrame(rows, columns=SUMMARY_FIELDS)


def build_measure_summary(df: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    rows = []
    successful_df = df[df["success_bool"]]

    for key, group in iter_groups(successful_df, group_columns):
        group_name = " | ".join(str(value) for value in key)

        for measure in MEASURES:
            percent_error = group[f"{measure}_percent_error"].dropna()
            absolute_error = group[f"{measure}_absolute_error"].dropna()
            signed_error = group[f"{measure}_signed_error"].dropna()
            expected = group[f"{measure}_expected"].dropna()
            estimate = group[f"{measure}_estimate"].dropna()
            interval_hit = group[f"{measure}_interval_hit"]

            row = {
                "group": group_name,
                "measure": measure,
                "runs": len(group),
                "valid_error_count": int(percent_error.count()),
                "mean_percent_error": percent_error.mean() if not percent_error.empty else pd.NA,
                "median_percent_error": percent_error.median() if not percent_error.empty else pd.NA,
                "mean_absolute_error": absolute_error.mean() if not absolute_error.empty else pd.NA,
                "median_absolute_error": absolute_error.median() if not absolute_error.empty else pd.NA,
                "mean_signed_error": signed_error.mean() if not signed_error.empty else pd.NA,
                "mean_expected": expected.mean() if not expected.empty else pd.NA,
                "mean_estimate": estimate.mean() if not estimate.empty else pd.NA,
                "interval_hits": int(interval_hit.sum()) if len(interval_hit) else 0,
                "interval_hit_rate": interval_hit.mean() if len(interval_hit) else pd.NA,
                "mean_absolute_error_grams": pd.NA,
                "median_absolute_error_grams": pd.NA,
                "within_25g_rate": pd.NA,
                "within_50g_rate": pd.NA,
                "within_100g_rate": pd.NA,
                "within_20_percent_rate": pd.NA,
            }

            if measure == "peso":
                absolute_error_grams = group["peso_absolute_error_grams"].dropna()
                row["mean_absolute_error_grams"] = (
                    absolute_error_grams.mean() if not absolute_error_grams.empty else pd.NA
                )
                row["median_absolute_error_grams"] = (
                    absolute_error_grams.median() if not absolute_error_grams.empty else pd.NA
                )
                for threshold in WEIGHT_THRESHOLDS_GRAMS:
                    row[f"within_{threshold}g_rate"] = boolean_rate(group[f"peso_error_within_{threshold}g"])
                row["within_20_percent_rate"] = boolean_rate(group["peso_error_within_20_percent"])

            rows.append(row)

    return pd.DataFrame(rows, columns=MEASURE_SUMMARY_FIELDS)

def save_summary(path: Path, summary: pd.DataFrame) -> None:
    summary.to_csv(path, index=False)


def split_model_mode(summary: pd.DataFrame, metric: str) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()

    parts = summary["group"].str.split(" | ", regex=False, expand=True)
    if parts.shape[1] < 2:
        return pd.DataFrame()

    chart_data = pd.DataFrame({
        "model": parts[0],
        "mode": parts[1],
        metric: pd.to_numeric(summary[metric], errors="coerce"),
    })
    return chart_data.pivot(index="model", columns="mode", values=metric)


def split_measure_model_mode(summary: pd.DataFrame, measure: str, metric: str) -> pd.DataFrame:
    measure_summary = summary[summary["measure"] == measure]
    return split_model_mode(measure_summary, metric)


def image_count_label(value: Any) -> str:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{count} imagem" if count == 1 else f"{count} imagens"


def parse_model_mode_image_count_summary(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty or "group" not in summary.columns:
        return pd.DataFrame()

    parts = summary["group"].str.split(" | ", regex=False, expand=True)
    if parts.shape[1] < 3:
        return pd.DataFrame()

    data = summary.copy()
    data["model"] = parts[0]
    data["image_processing_mode"] = parts[1]
    data["image_count"] = pd.to_numeric(parts[2], errors="coerce")
    data = data.dropna(subset=["image_count"])
    data["image_count"] = data["image_count"].astype(int)
    data["group"] = data["model"] + " | " + data["image_processing_mode"]
    return data


def split_model_mode_image_count(summary: pd.DataFrame, metric: str) -> pd.DataFrame:
    data = parse_model_mode_image_count_summary(summary)
    if data.empty or metric not in data.columns:
        return pd.DataFrame()

    data[metric] = pd.to_numeric(data[metric], errors="coerce")
    data["image_count_label"] = data["image_count"].map(image_count_label)
    pivot = data.pivot_table(index="group", columns="image_count_label", values=metric, aggfunc="mean")
    ordered_labels = [
        image_count_label(count)
        for count in sorted(data["image_count"].dropna().unique())
        if image_count_label(count) in pivot.columns
    ]
    return pivot[ordered_labels]


def get_metric_for_image_count(group: pd.DataFrame, image_count: int, metric: str) -> Any:
    matching = group[group["image_count"] == image_count]
    if matching.empty or metric not in matching.columns:
        return pd.NA
    value = matching.iloc[0][metric]
    return value if pd.notna(value) else pd.NA


def calculate_delta(before: Any, after: Any) -> Any:
    if pd.isna(before) or pd.isna(after):
        return pd.NA
    return float(after) - float(before)


def calculate_relative_change_percent(before: Any, after: Any) -> Any:
    if pd.isna(before) or pd.isna(after) or float(before) == 0:
        return pd.NA
    return ((float(after) - float(before)) / abs(float(before))) * 100


def build_image_count_delta_summary(
    summary: pd.DataFrame,
    measure_summary: pd.DataFrame,
) -> pd.DataFrame:
    data = parse_model_mode_image_count_summary(summary)
    measure_data = parse_model_mode_image_count_summary(measure_summary)
    if data.empty:
        return pd.DataFrame(columns=IMAGE_COUNT_DELTA_FIELDS)

    height_data = measure_data[measure_data.get("measure", "") == "altura"] if not measure_data.empty else pd.DataFrame()
    rows = []

    for (model, mode), group in data.groupby(["model", "image_processing_mode"], sort=True):
        if IMAGE_COUNT_BASE not in set(group["image_count"]) or IMAGE_COUNT_COMPARISON not in set(group["image_count"]):
            continue

        height_group = pd.DataFrame()
        if not height_data.empty:
            height_group = height_data[
                (height_data["model"] == model)
                & (height_data["image_processing_mode"] == mode)
            ]

        error_dimensions_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_abs_percent_error_dimensions")
        error_dimensions_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_abs_percent_error_dimensions")
        error_all_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_abs_percent_error_all")
        error_all_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_abs_percent_error_all")
        interval_dimensions_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_dimension_interval_hit_rate")
        interval_dimensions_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_dimension_interval_hit_rate")
        interval_all_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_all_interval_hit_rate")
        interval_all_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_all_interval_hit_rate")
        height_error_1 = get_metric_for_image_count(height_group, IMAGE_COUNT_BASE, "mean_percent_error")
        height_error_2 = get_metric_for_image_count(height_group, IMAGE_COUNT_COMPARISON, "mean_percent_error")
        weight_error_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "weight_mean_absolute_error_g")
        weight_error_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "weight_mean_absolute_error_g")
        tokens_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_total_tokens")
        tokens_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_total_tokens")
        cost_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_calculated_cost_usd")
        cost_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_calculated_cost_usd")

        rows.append({
            "group": f"{model} | {mode}",
            "model": model,
            "image_processing_mode": mode,
            "runs_1_image": get_metric_for_image_count(group, IMAGE_COUNT_BASE, "runs"),
            "runs_2_images": get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "runs"),
            "success_rate_1_image": get_metric_for_image_count(group, IMAGE_COUNT_BASE, "success_rate"),
            "success_rate_2_images": get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "success_rate"),
            "delta_success_rate": calculate_delta(
                get_metric_for_image_count(group, IMAGE_COUNT_BASE, "success_rate"),
                get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "success_rate"),
            ),
            "error_dimensions_1_image": error_dimensions_1,
            "error_dimensions_2_images": error_dimensions_2,
            "delta_error_dimensions": calculate_delta(error_dimensions_1, error_dimensions_2),
            "relative_change_error_dimensions_percent": calculate_relative_change_percent(error_dimensions_1, error_dimensions_2),
            "error_all_1_image": error_all_1,
            "error_all_2_images": error_all_2,
            "delta_error_all": calculate_delta(error_all_1, error_all_2),
            "relative_change_error_all_percent": calculate_relative_change_percent(error_all_1, error_all_2),
            "interval_dimensions_1_image": interval_dimensions_1,
            "interval_dimensions_2_images": interval_dimensions_2,
            "delta_interval_dimensions": calculate_delta(interval_dimensions_1, interval_dimensions_2),
            "interval_all_1_image": interval_all_1,
            "interval_all_2_images": interval_all_2,
            "delta_interval_all": calculate_delta(interval_all_1, interval_all_2),
            "height_error_1_image": height_error_1,
            "height_error_2_images": height_error_2,
            "delta_height_error": calculate_delta(height_error_1, height_error_2),
            "relative_change_height_error_percent": calculate_relative_change_percent(height_error_1, height_error_2),
            "weight_error_g_1_image": weight_error_1,
            "weight_error_g_2_images": weight_error_2,
            "delta_weight_error_g": calculate_delta(weight_error_1, weight_error_2),
            "tokens_1_image": tokens_1,
            "tokens_2_images": tokens_2,
            "delta_tokens": calculate_delta(tokens_1, tokens_2),
            "relative_change_tokens_percent": calculate_relative_change_percent(tokens_1, tokens_2),
            "cost_1_image": cost_1,
            "cost_2_images": cost_2,
            "delta_cost": calculate_delta(cost_1, cost_2),
            "relative_change_cost_percent": calculate_relative_change_percent(cost_1, cost_2),
        })

    return pd.DataFrame(rows, columns=IMAGE_COUNT_DELTA_FIELDS)


def build_measure_image_count_delta_summary(measure_summary: pd.DataFrame) -> pd.DataFrame:
    data = parse_model_mode_image_count_summary(measure_summary)
    if data.empty:
        return pd.DataFrame(columns=MEASURE_IMAGE_COUNT_DELTA_FIELDS)

    rows = []
    for (model, mode, measure), group in data.groupby(["model", "image_processing_mode", "measure"], sort=True):
        if IMAGE_COUNT_BASE not in set(group["image_count"]) or IMAGE_COUNT_COMPARISON not in set(group["image_count"]):
            continue

        error_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "mean_percent_error")
        error_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "mean_percent_error")
        hit_1 = get_metric_for_image_count(group, IMAGE_COUNT_BASE, "interval_hit_rate")
        hit_2 = get_metric_for_image_count(group, IMAGE_COUNT_COMPARISON, "interval_hit_rate")

        rows.append({
            "group": f"{model} | {mode}",
            "model": model,
            "image_processing_mode": mode,
            "measure": measure,
            "mean_percent_error_1_image": error_1,
            "mean_percent_error_2_images": error_2,
            "delta_mean_percent_error": calculate_delta(error_1, error_2),
            "relative_change_mean_percent_error_percent": calculate_relative_change_percent(error_1, error_2),
            "interval_hit_rate_1_image": hit_1,
            "interval_hit_rate_2_images": hit_2,
            "delta_interval_hit_rate": calculate_delta(hit_1, hit_2),
        })

    return pd.DataFrame(rows, columns=MEASURE_IMAGE_COUNT_DELTA_FIELDS)


def get_heatmap_norm(matrix, center_zero: bool):
    if not center_zero:
        return None

    finite_values = matrix[pd.notna(matrix)]
    if not len(finite_values):
        return None

    min_value = float(finite_values.min())
    max_value = float(finite_values.max())
    if min_value < 0 < max_value:
        return TwoSlopeNorm(vmin=min_value, vcenter=0, vmax=max_value)

    return None


def save_grouped_bar_chart(
    path: Path,
    data: pd.DataFrame,
    title: str,
    y_label: str,
    y_percent: bool = False,
    y_currency: bool = False,
) -> None:
    if data.empty:
        return

    ordered_columns = [mode for mode in IMAGE_PROCESSING_MODES if mode in data.columns]
    data = data[ordered_columns]

    colors = [MODE_COLORS.get(mode, "#6B7280") for mode in data.columns]
    ax = data.plot(kind="bar", figsize=(12, 6), width=0.78, color=colors)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Modelo")
    ax.set_ylabel(y_label)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Imagem")
    ax.tick_params(axis="x", rotation=35)

    if y_percent:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    if y_currency:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.4f}"))

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_simple_bar_chart(
    path: Path,
    data: pd.DataFrame,
    title: str,
    y_label: str,
    color: str = "#00A868",
    y_currency: bool = False,
) -> None:
    if data.empty:
        return

    ax = data.plot(kind="bar", x="group", y="value", figsize=(8, 5), legend=False, color=color)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel(y_label)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=20)

    if y_currency:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.4f}"))

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_heatmap(
    path: Path,
    data: pd.DataFrame,
    title: str,
    colorbar_label: str,
    cmap: str,
    value_format: str,
    colorbar_percent: bool = False,
    center_zero: bool = False,
) -> None:
    if data.empty or data.dropna(how="all").empty:
        return

    data = data[[measure for measure in MEASURES if measure in data.columns]]
    data = data.apply(pd.to_numeric, errors="coerce")
    matrix = data.to_numpy(dtype=float, na_value=float("nan"))

    height = max(5, 0.38 * len(data.index) + 2)
    width = max(8, 1.35 * len(data.columns) + 5)
    fig, ax = plt.subplots(figsize=(width, height))
    image = ax.imshow(matrix, aspect="auto", cmap=cmap, norm=get_heatmap_norm(matrix, center_zero))

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)

    for row_index, row_label in enumerate(data.index):
        for col_index, column in enumerate(data.columns):
            value = matrix[row_index, col_index]
            if pd.notna(value):
                ax.text(col_index, row_index, value_format.format(float(value)), ha="center", va="center", fontsize=8)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label(colorbar_label)
    if colorbar_percent:
        colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_measure_heatmaps(path_prefix: Path, summary: pd.DataFrame) -> None:
    if summary.empty:
        return

    error_data = summary.pivot(index="group", columns="measure", values="mean_percent_error")
    save_heatmap(
        path_prefix / "mean_percent_error_by_measure_heatmap.svg",
        error_data,
        "Erro percentual médio por medida",
        "Erro médio (%)",
        "YlOrRd",
        "{:.1f}",
    )

    interval_data = summary.pivot(index="group", columns="measure", values="interval_hit_rate")
    save_heatmap(
        path_prefix / "interval_hit_rate_by_measure_heatmap.svg",
        interval_data,
        "Taxa de acerto de intervalo por medida",
        "Taxa de acerto",
        "YlGn",
        "{:.0%}",
        colorbar_percent=True,
    )


def save_model_mode_heatmap(
    path: Path,
    summary: pd.DataFrame,
    metric: str,
    title: str,
    colorbar_label: str,
    cmap: str,
    value_format: str,
    colorbar_percent: bool = False,
    colorbar_currency: bool = False,
    center_zero: bool = False,
) -> None:
    data = split_model_mode(summary, metric)
    if data.empty or data.dropna(how="all").empty:
        return

    ordered_columns = [mode for mode in IMAGE_PROCESSING_MODES if mode in data.columns]
    data = data[ordered_columns]
    data = data.apply(pd.to_numeric, errors="coerce")
    matrix = data.to_numpy(dtype=float, na_value=float("nan"))

    height = max(4.5, 0.58 * len(data.index) + 2)
    width = max(7, 1.45 * len(data.columns) + 4.8)
    fig, ax = plt.subplots(figsize=(width, height))
    image = ax.imshow(matrix, aspect="auto", cmap=cmap, norm=get_heatmap_norm(matrix, center_zero))

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)

    for row_index, row_label in enumerate(data.index):
        for col_index, column in enumerate(data.columns):
            value = matrix[row_index, col_index]
            if pd.notna(value):
                ax.text(
                    col_index,
                    row_index,
                    value_format.format(float(value)),
                    ha="center",
                    va="center",
                    fontsize=9,
                )

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label(colorbar_label)
    if colorbar_percent:
        colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    if colorbar_currency:
        colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.3f}"))

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_model_mode_heatmaps(path_prefix: Path, summary: pd.DataFrame) -> None:
    save_model_mode_heatmap(
        path_prefix / "heatmap_error_dimensions_by_model_mode.svg",
        summary,
        "mean_abs_percent_error_dimensions",
        "Erro médio dimensional por modelo e imagem",
        "Erro médio dimensional (%)",
        "YlOrRd",
        "{:.1f}",
    )
    save_model_mode_heatmap(
        path_prefix / "heatmap_error_including_weight_by_model_mode.svg",
        summary,
        "mean_abs_percent_error_all",
        "Erro médio incluindo peso por modelo e imagem",
        "Erro médio incluindo peso (%)",
        "YlOrRd",
        "{:.1f}",
    )
    save_model_mode_heatmap(
        path_prefix / "heatmap_interval_hit_dimensions_by_model_mode.svg",
        summary,
        "mean_dimension_interval_hit_rate",
        "Taxa de acerto dimensional por modelo e imagem",
        "Taxa de acerto dimensional",
        "YlGn",
        "{:.0%}",
        colorbar_percent=True,
    )
    save_model_mode_heatmap(
        path_prefix / "heatmap_interval_hit_including_weight_by_model_mode.svg",
        summary,
        "mean_all_interval_hit_rate",
        "Taxa de acerto incluindo peso por modelo e imagem",
        "Taxa de acerto incluindo peso",
        "YlGn",
        "{:.0%}",
        colorbar_percent=True,
    )
    save_model_mode_heatmap(
        path_prefix / "heatmap_total_cost_by_model_mode.svg",
        summary,
        "total_calculated_cost_usd",
        "Custo total por modelo e imagem",
        "Custo total (USD)",
        "Blues",
        "${:.3f}",
        colorbar_currency=True,
    )


def save_model_mode_image_count_heatmap(
    path: Path,
    summary: pd.DataFrame,
    metric: str,
    title: str,
    colorbar_label: str,
    cmap: str,
    value_format: str,
    colorbar_percent: bool = False,
    colorbar_currency: bool = False,
) -> None:
    data = split_model_mode_image_count(summary, metric)
    if data.empty or data.dropna(how="all").empty:
        return

    data = data.apply(pd.to_numeric, errors="coerce")
    matrix = data.to_numpy(dtype=float, na_value=float("nan"))

    height = max(4.5, 0.52 * len(data.index) + 2)
    width = max(7, 1.55 * len(data.columns) + 5)
    fig, ax = plt.subplots(figsize=(width, height))
    image = ax.imshow(matrix, aspect="auto", cmap=cmap)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)

    for row_index, row_label in enumerate(data.index):
        for col_index, column in enumerate(data.columns):
            value = matrix[row_index, col_index]
            if pd.notna(value):
                ax.text(
                    col_index,
                    row_index,
                    value_format.format(float(value)),
                    ha="center",
                    va="center",
                    fontsize=9,
                )

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label(colorbar_label)
    if colorbar_percent:
        colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    if colorbar_currency:
        colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.4f}"))

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_image_count_heatmaps(
    output_dir: Path,
    summary: pd.DataFrame,
    measure_summary: pd.DataFrame,
) -> None:
    save_model_mode_image_count_heatmap(
        output_dir / "heatmap_error_dimensions_by_model_mode_image_count.svg",
        summary,
        "mean_abs_percent_error_dimensions",
        "Erro dimensional por modelo, tratamento e quantidade de imagens",
        "Erro médio dimensional (%)",
        "YlOrRd",
        "{:.1f}",
    )
    save_model_mode_image_count_heatmap(
        output_dir / "heatmap_error_including_weight_by_model_mode_image_count.svg",
        summary,
        "mean_abs_percent_error_all",
        "Erro incluindo peso por modelo, tratamento e quantidade de imagens",
        "Erro médio incluindo peso (%)",
        "YlOrRd",
        "{:.1f}",
    )
    save_model_mode_image_count_heatmap(
        output_dir / "heatmap_interval_hit_dimensions_by_model_mode_image_count.svg",
        summary,
        "mean_dimension_interval_hit_rate",
        "Taxa de acerto dimensional por modelo, tratamento e quantidade de imagens",
        "Taxa de acerto dimensional",
        "YlGn",
        "{:.0%}",
        colorbar_percent=True,
    )
    save_model_mode_image_count_heatmap(
        output_dir / "heatmap_mean_tokens_by_model_mode_image_count.svg",
        summary,
        "mean_total_tokens",
        "Tokens médios por modelo, tratamento e quantidade de imagens",
        "Tokens médios",
        "Blues",
        "{:.0f}",
    )
    save_model_mode_image_count_heatmap(
        output_dir / "heatmap_mean_cost_by_model_mode_image_count.svg",
        summary,
        "mean_calculated_cost_usd",
        "Custo médio por modelo, tratamento e quantidade de imagens",
        "Custo médio (USD)",
        "Blues",
        "${:.5f}",
        colorbar_currency=True,
    )

    if not measure_summary.empty:
        height_summary = measure_summary[measure_summary["measure"] == "altura"]
        save_model_mode_image_count_heatmap(
            output_dir / "heatmap_height_error_by_model_mode_image_count.svg",
            height_summary,
            "mean_percent_error",
            "Erro de altura por modelo, tratamento e quantidade de imagens",
            "Erro médio de altura (%)",
            "YlOrRd",
            "{:.1f}",
        )


def save_image_count_delta_heatmaps(
    output_dir: Path,
    delta_summary: pd.DataFrame,
    measure_delta_summary: pd.DataFrame,
) -> None:
    if delta_summary.empty:
        return

    save_model_mode_heatmap(
        output_dir / "heatmap_delta_error_dimensions_2_vs_1_images.svg",
        delta_summary,
        "delta_error_dimensions",
        "Mudança no erro dimensional ao usar 2 imagens",
        "2 imagens - 1 imagem (p.p. de erro)",
        "RdYlGn_r",
        "{:+.1f}",
        center_zero=True,
    )
    save_model_mode_heatmap(
        output_dir / "heatmap_delta_height_error_2_vs_1_images.svg",
        delta_summary,
        "delta_height_error",
        "Mudança no erro de altura ao usar 2 imagens",
        "2 imagens - 1 imagem (p.p. de erro)",
        "RdYlGn_r",
        "{:+.1f}",
        center_zero=True,
    )
    save_model_mode_heatmap(
        output_dir / "heatmap_delta_interval_hit_dimensions_2_vs_1_images.svg",
        delta_summary,
        "delta_interval_dimensions",
        "Mudança na taxa de acerto dimensional ao usar 2 imagens",
        "2 imagens - 1 imagem",
        "RdYlGn",
        "{:+.0%}",
        colorbar_percent=True,
        center_zero=True,
    )
    save_model_mode_heatmap(
        output_dir / "heatmap_delta_tokens_2_vs_1_images.svg",
        delta_summary,
        "delta_tokens",
        "Mudança em tokens médios ao usar 2 imagens",
        "2 imagens - 1 imagem",
        "RdYlGn_r",
        "{:+.0f}",
        center_zero=True,
    )
    save_model_mode_heatmap(
        output_dir / "heatmap_delta_cost_2_vs_1_images.svg",
        delta_summary,
        "delta_cost",
        "Mudança no custo médio ao usar 2 imagens",
        "2 imagens - 1 imagem (USD)",
        "RdYlGn_r",
        "${:+.5f}",
        colorbar_currency=True,
        center_zero=True,
    )

    if measure_delta_summary.empty:
        return

    error_data = measure_delta_summary.pivot(index="group", columns="measure", values="delta_mean_percent_error")
    save_heatmap(
        output_dir / "heatmap_delta_error_by_measure_2_vs_1_images.svg",
        error_data,
        "Mudança no erro por medida ao usar 2 imagens",
        "2 imagens - 1 imagem (p.p. de erro)",
        "RdYlGn_r",
        "{:+.1f}",
        center_zero=True,
    )

    hit_data = measure_delta_summary.pivot(index="group", columns="measure", values="delta_interval_hit_rate")
    save_heatmap(
        output_dir / "heatmap_delta_interval_hit_by_measure_2_vs_1_images.svg",
        hit_data,
        "Mudança no acerto de intervalo por medida ao usar 2 imagens",
        "2 imagens - 1 imagem",
        "RdYlGn",
        "{:+.0%}",
        colorbar_percent=True,
        center_zero=True,
    )


def save_cost_benefit_scatter(path: Path, summary: pd.DataFrame) -> None:
    if summary.empty:
        return

    parts = summary["group"].str.split(" | ", regex=False, expand=True)
    if parts.shape[1] < 2:
        return

    data = summary.copy()
    data["model"] = parts[0]
    data["mode"] = parts[1]
    data["mean_calculated_cost_usd"] = pd.to_numeric(data["mean_calculated_cost_usd"], errors="coerce")
    data["mean_dimension_interval_hit_rate"] = pd.to_numeric(data["mean_dimension_interval_hit_rate"], errors="coerce")
    data = data.dropna(subset=["mean_calculated_cost_usd", "mean_dimension_interval_hit_rate"])
    if data.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    for mode in IMAGE_PROCESSING_MODES:
        mode_data = data[data["mode"] == mode]
        if mode_data.empty:
            continue
        ax.scatter(
            mode_data["mean_calculated_cost_usd"],
            mode_data["mean_dimension_interval_hit_rate"],
            label=mode,
            color=MODE_COLORS.get(mode, "#6B7280"),
            s=90,
            alpha=0.85,
        )
        for _, row in mode_data.iterrows():
            ax.annotate(
                str(row["model"]),
                (row["mean_calculated_cost_usd"], row["mean_dimension_interval_hit_rate"]),
                xytext=(5, 4),
                textcoords="offset points",
                fontsize=8,
            )

    ax.set_title("Custo-benefício dimensional por modelo e tratamento de imagem", fontsize=14, fontweight="bold")
    ax.set_xlabel("Custo médio por chamada (USD)")
    ax.set_ylabel("Taxa média de acerto dimensional")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.4f}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    ax.grid(alpha=0.25)
    ax.legend(title="Imagem")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def best_row(summary: pd.DataFrame, column: str, ascending: bool) -> pd.Series | None:
    valid = summary.dropna(subset=[column])
    if valid.empty:
        return None
    valid = valid.sort_values(column, ascending=ascending)
    return valid.iloc[0]


def format_percent(value: Any) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{float(value):.2%}"


def format_number(value: Any, suffix: str = "") -> str:
    if pd.isna(value):
        return "n/a"
    return f"{float(value):.2f}{suffix}"


def format_usd(value: Any) -> str:
    if pd.isna(value):
        return "n/a"
    return f"${float(value):.6f}"


def write_report(
    path: Path,
    input_csv: Path,
    df: pd.DataFrame,
    model_mode_summary: pd.DataFrame,
    measure_summary: pd.DataFrame,
    image_count_delta_summary: pd.DataFrame,
) -> None:
    successes = int(df["success_bool"].sum())
    failures = len(df) - successes

    best_error = best_row(model_mode_summary, "mean_abs_percent_error_dimensions", ascending=True)
    best_hit_rate = best_row(model_mode_summary, "mean_dimension_interval_hit_rate", ascending=False)
    lowest_tokens = best_row(model_mode_summary, "mean_total_tokens", ascending=True)
    lowest_cost = best_row(model_mode_summary, "mean_calculated_cost_usd", ascending=True)
    best_cost_benefit = best_row(model_mode_summary, "cost_benefit_score_dimensions", ascending=False)

    total_input_tokens = numeric_sum(df.loc[df["success_bool"], "input_tokens"])
    total_output_tokens = numeric_sum(df.loc[df["success_bool"], "output_tokens"])
    total_tokens = numeric_sum(df.loc[df["success_bool"], "total_tokens"])
    total_input_cost = numeric_sum(df.loc[df["success_bool"], "input_cost_usd"])
    total_output_cost = numeric_sum(df.loc[df["success_bool"], "output_cost_usd"])
    total_cost = numeric_sum(df.loc[df["success_bool"], "calculated_cost_usd"])

    lines = [
        "# Relatório de avaliação",
        "",
        f"Arquivo analisado: `{input_csv}`",
        f"Gerado em: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Visão geral",
        "",
        f"- Execuções: {len(df)}",
        f"- Sucessos: {successes}",
        f"- Falhas: {failures}",
        f"- Tokens de entrada usados: {format_number(total_input_tokens)}",
        f"- Tokens de saída usados: {format_number(total_output_tokens)}",
        f"- Tokens totais usados: {format_number(total_tokens)}",
        f"- Custo total de entrada: {format_usd(total_input_cost)}",
        f"- Custo total de saída: {format_usd(total_output_cost)}",
        f"- Gasto total estimado: {format_usd(total_cost)}",
    ]

    if best_error is not None:
        lines.append(
            f"- Menor erro médio dimensional: `{best_error['group']}` "
            f"({format_number(best_error['mean_abs_percent_error_dimensions'], '%')})"
        )
    if best_hit_rate is not None:
        lines.append(
            f"- Maior taxa média de acerto dimensional: `{best_hit_rate['group']}` "
            f"({format_percent(best_hit_rate['mean_dimension_interval_hit_rate'])})"
        )
    if lowest_tokens is not None:
        lines.append(
            f"- Menor média de tokens totais: `{lowest_tokens['group']}` "
            f"({format_number(lowest_tokens['mean_total_tokens'])})"
        )
    if lowest_cost is not None:
        lines.append(
            f"- Menor custo médio por chamada: `{lowest_cost['group']}` "
            f"({format_usd(lowest_cost['mean_calculated_cost_usd'])})"
        )
    if best_cost_benefit is not None:
        lines.append(
            f"- Melhor custo-benefício dimensional: `{best_cost_benefit['group']}` "
            f"({format_number(best_cost_benefit['cost_benefit_score_dimensions'])} acertos dimensionais por dólar médio)"
        )

    if not measure_summary.empty:
        lines.extend(["", "## Erro por medida", ""])
        for _, row in measure_summary.iterrows():
            line = (
                f"- `{row['measure']}`: erro médio {format_number(row['mean_percent_error'], '%')}; "
                f"mediana {format_number(row['median_percent_error'], '%')}; "
                f"acerto de intervalo {format_percent(row['interval_hit_rate'])}"
            )
            if row["measure"] == "peso":
                line += (
                    f"; erro absoluto médio {format_number(row['mean_absolute_error_grams'], 'g')}"
                    f"; <=25g {format_percent(row['within_25g_rate'])}"
                    f"; <=50g {format_percent(row['within_50g_rate'])}"
                    f"; <=100g {format_percent(row['within_100g_rate'])}"
                    f"; <=20% {format_percent(row['within_20_percent_rate'])}"
                )
            lines.append(line)

    if not image_count_delta_summary.empty:
        lines.extend([
            "",
            "## Uma imagem vs duas imagens",
            "",
            "Os deltas abaixo usam `2 imagens - 1 imagem`. Para erro, tokens e custo, valor negativo é melhor. Para taxa de acerto, valor positivo é melhor.",
            "",
        ])
        for _, row in image_count_delta_summary.iterrows():
            lines.append(
                f"- `{row['group']}`: "
                f"erro dimensional {format_number(row['error_dimensions_1_image'], '%')} -> "
                f"{format_number(row['error_dimensions_2_images'], '%')} "
                f"(delta {format_number(row['delta_error_dimensions'], ' p.p.')}); "
                f"altura delta {format_number(row['delta_height_error'], ' p.p.')}; "
                f"acerto dimensional delta {format_percent(row['delta_interval_dimensions'])}; "
                f"tokens delta {format_number(row['delta_tokens'])}; "
                f"custo delta {format_usd(row['delta_cost'])}"
            )

    failure_df = df[~df["success_bool"]]
    if not failure_df.empty and "error_type" in failure_df.columns:
        lines.extend(["", "## Falhas", ""])
        counts = failure_df["error_type"].fillna("erro_desconhecido").replace("", "erro_desconhecido").value_counts()
        for error_type, count in counts.items():
            lines.append(f"- {error_type}: {count}")

    lines.extend([
        "",
        "## Custos",
        "",
        "Os custos são recalculados na análise a partir de `input_tokens` e `output_tokens`, usando a tabela fixa de preço por 1 milhão de tokens definida em `tests/analyze_results.py`.",
        "O score principal de custo-benefício usa só dimensões: `mean_dimension_interval_hit_rate / mean_calculated_cost_usd`; maior é melhor, mas ele deve ser lido junto com erro médio, peso e taxa de sucesso.",
        "",
        "## Arquivos gerados",
        "",
        "- `summary_by_model_mode.csv`",
        "- `summary_by_model.csv`",
        "- `summary_by_processing_mode.csv`",
        "- `summary_by_sample_model_mode.csv`",
        "- `summary_by_model_mode_measure.csv`",
        "- `summary_by_measure.csv`",
        "- `summary_by_model_mode_weight.csv`",
        "- `summary_by_weight.csv`",
        "- `summary_by_model_mode_image_count.csv`",
        "- `summary_by_image_count.csv`",
        "- `summary_delta_2_vs_1_images_by_model_mode.csv`",
        "- `summary_delta_2_vs_1_images_by_model_mode_measure.csv`",
        "- gráficos `.svg` no mesmo diretório",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(input_csv: Path, output_dir: Path) -> None:
    df = load_results(input_csv)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_mode_summary = build_summary(df, ["model", "image_processing_mode"])
    model_summary = build_summary(df, ["model"])
    mode_summary = build_summary(df, ["image_processing_mode"])
    sample_model_mode_summary = build_summary(df, ["sample_id", "model", "image_processing_mode"])
    model_mode_measure_summary = build_measure_summary(df, ["model", "image_processing_mode"])
    measure_summary = build_measure_summary(df, [])
    model_mode_image_count_summary = build_summary(df, ["model", "image_processing_mode", "image_count"])
    image_count_summary = build_summary(df, ["image_count"])
    mode_image_count_summary = build_summary(df, ["image_processing_mode", "image_count"])
    sample_model_mode_image_count_summary = build_summary(
        df,
        ["sample_id", "model", "image_processing_mode", "image_count"],
    )
    model_mode_image_count_measure_summary = build_measure_summary(
        df,
        ["model", "image_processing_mode", "image_count"],
    )
    image_count_delta_summary = build_image_count_delta_summary(
        model_mode_image_count_summary,
        model_mode_image_count_measure_summary,
    )
    measure_image_count_delta_summary = build_measure_image_count_delta_summary(
        model_mode_image_count_measure_summary
    )
    model_mode_weight_summary = model_mode_measure_summary[
        model_mode_measure_summary["measure"] == "peso"
    ].copy()
    weight_summary = measure_summary[measure_summary["measure"] == "peso"].copy()

    save_summary(output_dir / "summary_by_model_mode.csv", model_mode_summary)
    save_summary(output_dir / "summary_by_model.csv", model_summary)
    save_summary(output_dir / "summary_by_processing_mode.csv", mode_summary)
    save_summary(output_dir / "summary_by_sample_model_mode.csv", sample_model_mode_summary)
    save_summary(output_dir / "summary_by_model_mode_measure.csv", model_mode_measure_summary)
    save_summary(output_dir / "summary_by_measure.csv", measure_summary)
    save_summary(output_dir / "summary_by_model_mode_weight.csv", model_mode_weight_summary)
    save_summary(output_dir / "summary_by_weight.csv", weight_summary)
    save_summary(output_dir / "summary_by_model_mode_image_count.csv", model_mode_image_count_summary)
    save_summary(output_dir / "summary_by_image_count.csv", image_count_summary)
    save_summary(output_dir / "summary_by_processing_mode_image_count.csv", mode_image_count_summary)
    save_summary(output_dir / "summary_by_sample_model_mode_image_count.csv", sample_model_mode_image_count_summary)
    save_summary(output_dir / "summary_by_model_mode_image_count_measure.csv", model_mode_image_count_measure_summary)
    save_summary(output_dir / "summary_delta_2_vs_1_images_by_model_mode.csv", image_count_delta_summary)
    save_summary(output_dir / "summary_delta_2_vs_1_images_by_model_mode_measure.csv", measure_image_count_delta_summary)

    save_grouped_bar_chart(
        output_dir / "mean_abs_percent_error_dimensions_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_abs_percent_error_dimensions"),
        "Erro percentual médio dimensional por modelo e imagem",
        "Erro médio dimensional (%)",
    )
    save_grouped_bar_chart(
        output_dir / "mean_abs_percent_error_all_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_abs_percent_error_all"),
        "Erro percentual médio por modelo e imagem, incluindo peso",
        "Erro médio incluindo peso (%)",
    )
    save_grouped_bar_chart(
        output_dir / "dimension_interval_hit_rate_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_dimension_interval_hit_rate"),
        "Taxa de acerto dimensional por modelo e imagem",
        "Taxa média dimensional",
        y_percent=True,
    )
    save_grouped_bar_chart(
        output_dir / "interval_hit_rate_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_all_interval_hit_rate"),
        "Taxa de acerto do intervalo por modelo e imagem, incluindo peso",
        "Taxa média incluindo peso",
        y_percent=True,
    )
    save_grouped_bar_chart(
        output_dir / "total_tokens_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_total_tokens"),
        "Tokens totais médios por modelo e imagem",
        "Tokens médios",
    )
    save_grouped_bar_chart(
        output_dir / "mean_cost_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_calculated_cost_usd"),
        "Custo médio por chamada por modelo e imagem",
        "Custo médio (USD)",
        y_currency=True,
    )
    save_grouped_bar_chart(
        output_dir / "total_cost_by_model_mode.svg",
        split_model_mode(model_mode_summary, "total_calculated_cost_usd"),
        "Gasto total por modelo e imagem",
        "Gasto total (USD)",
        y_currency=True,
    )
    save_grouped_bar_chart(
        output_dir / "cost_benefit_score_by_model_mode.svg",
        split_model_mode(model_mode_summary, "cost_benefit_score_dimensions"),
        "Custo-benefício dimensional por modelo e imagem",
        "Taxa de acerto dimensional / custo médio",
    )
    save_cost_benefit_scatter(
        output_dir / "cost_benefit_scatter_by_model_mode.svg",
        model_mode_summary,
    )
    save_grouped_bar_chart(
        output_dir / "cost_benefit_score_including_weight_by_model_mode.svg",
        split_model_mode(model_mode_summary, "cost_benefit_score_all"),
        "Custo-benefício incluindo peso por modelo e imagem",
        "Taxa de acerto geral / custo médio",
    )
    save_grouped_bar_chart(
        output_dir / "weight_absolute_error_grams_by_model_mode.svg",
        split_model_mode(model_mode_summary, "weight_mean_absolute_error_g"),
        "Erro absoluto médio de peso por modelo e imagem",
        "Erro médio (g)",
    )
    for threshold in WEIGHT_THRESHOLDS_GRAMS:
        save_grouped_bar_chart(
            output_dir / f"weight_within_{threshold}g_rate_by_model_mode.svg",
            split_model_mode(model_mode_summary, f"weight_within_{threshold}g_rate"),
            f"Peso com erro até {threshold}g por modelo e imagem",
            "Taxa",
            y_percent=True,
        )
    save_grouped_bar_chart(
        output_dir / "weight_within_20_percent_rate_by_model_mode.svg",
        split_model_mode(model_mode_summary, "weight_within_20_percent_rate"),
        "Peso com erro até 20% por modelo e imagem",
        "Taxa",
        y_percent=True,
    )
    save_grouped_bar_chart(
        output_dir / "duration_by_model_mode.svg",
        split_model_mode(model_mode_summary, "mean_duration_seconds"),
        "Duração média por modelo e imagem",
        "Segundos",
    )
    save_grouped_bar_chart(
        output_dir / "success_rate_by_model_mode.svg",
        split_model_mode(model_mode_summary, "success_rate"),
        "Taxa de sucesso por modelo e imagem",
        "Taxa de sucesso",
        y_percent=True,
    )

    measure_error = measure_summary[["measure", "mean_percent_error"]].copy()
    measure_error = measure_error.rename(columns={"measure": "group", "mean_percent_error": "value"}).dropna(subset=["value"])
    save_simple_bar_chart(
        output_dir / "mean_percent_error_by_measure.svg",
        measure_error,
        "Erro percentual médio por medida",
        "Erro médio (%)",
        color="#2563EB",
    )
    save_measure_heatmaps(output_dir, model_mode_measure_summary)
    save_model_mode_heatmaps(output_dir, model_mode_summary)
    save_image_count_heatmaps(
        output_dir,
        model_mode_image_count_summary,
        model_mode_image_count_measure_summary,
    )
    save_image_count_delta_heatmaps(
        output_dir,
        image_count_delta_summary,
        measure_image_count_delta_summary,
    )

    for measure in MEASURES:
        save_grouped_bar_chart(
            output_dir / f"mean_{measure}_percent_error_by_model_mode.svg",
            split_measure_model_mode(model_mode_measure_summary, measure, "mean_percent_error"),
            f"Erro percentual médio de {measure} por modelo e imagem",
            "Erro médio (%)",
        )

    final_bytes = mode_summary[["group", "mean_final_bytes"]].copy()
    final_bytes = final_bytes.rename(columns={"mean_final_bytes": "value"}).dropna(subset=["value"])
    save_simple_bar_chart(
        output_dir / "final_bytes_by_processing_mode.svg",
        final_bytes,
        "Tamanho médio final por modo de imagem",
        "Bytes médios",
    )

    write_report(
        output_dir / "report.md",
        input_csv,
        df,
        model_mode_summary,
        measure_summary,
        image_count_delta_summary,
    )


def main() -> None:
    args = parse_args()
    input_csv = args.input or latest_evaluation_csv()
    output_dir = args.output_dir or RESULTS_DIR / f"analysis_{input_csv.stem}"
    write_outputs(input_csv, output_dir)
    print(f"Análise gerada em: {output_dir}")


if __name__ == "__main__":
    main()
