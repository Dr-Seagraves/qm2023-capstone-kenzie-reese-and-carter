"""
QM 2023 Capstone: Milestone 3 Econometric Models
Team: Kenzie, Reese, and Carter
Date: 2026-04-13

This script estimates panel regression models to identify the effect of mortgage
rate shocks on metro-level home price growth. It implements:
1) Model A: Fixed Effects regression (entity and time FE via PanelOLS)
2) Model B: Difference-in-Differences
3) Required diagnostics and robustness checks
4) Machine learning benchmarks on held-out future periods

Outputs:
- Tables: results/tables/M3_*.csv and results/tables/M3_*.txt
- Figures: results/figures/M3_*.png
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS
from scipy import stats
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

try:
    from code.config_paths import FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR, ensure_directories
except ImportError:
    # Fallback for direct script execution from unusual working directories.
    PROJECT_ROOT = Path(__file__).resolve().parent
    FINAL_DATA_DIR = PROJECT_ROOT / "data" / "final"
    FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
    TABLES_DIR = PROJECT_ROOT / "results" / "tables"

    def ensure_directories() -> None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load and minimally clean metro panel data."""
    path = FINAL_DATA_DIR / "metro_mortgage_panel.csv"
    df = pd.read_csv(path)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["RegionName", "date"]).copy()

    for col in ["price_index", "MORTGAGE30US", "SizeRank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create outcome, key drivers, and DiD treatment indicators."""
    work = df.copy()

    # Outcome: monthly price growth (percent).
    work["price_growth"] = (
        work.groupby("RegionName")["price_index"].pct_change() * 100.0
    )

    # Lagged controls and mortgage lags.
    work["price_growth_lag1"] = work.groupby("RegionName")["price_growth"].shift(1)
    for lag in [1, 2, 3]:
        work[f"mortgage_lag{lag}"] = work.groupby("RegionName")["MORTGAGE30US"].shift(lag)

    # Region-level exposure: pre-2022 average absolute price volatility.
    pre_period = work[work["date"] < pd.Timestamp("2022-01-01")].copy()
    exposure = (
        pre_period.groupby("RegionName")["price_growth"]
        .apply(lambda s: np.nanmean(np.abs(s)))
        .rename("exposure")
    )
    work = work.merge(exposure, on="RegionName", how="left")

    # Driver for FE model: mortgage lag x region exposure.
    work["mortgage_exposure_lag3"] = work["mortgage_lag3"] * work["exposure"]

    # DiD design.
    cutoff = pd.Timestamp("2022-03-01")
    work["post_hike"] = (work["date"] >= cutoff).astype(int)
    treat_threshold = work["exposure"].quantile(0.75)
    work["treated"] = (work["exposure"] >= treat_threshold).astype(int)
    work["treated_post"] = work["treated"] * work["post_hike"]

    # Time FE key as compact monthly string.
    work["month_id"] = work["date"].dt.to_period("M").astype(str)

    # Drop rows needed for model estimation.
    work = work.dropna(
        subset=[
            "price_growth",
            "price_growth_lag1",
            "mortgage_lag1",
            "mortgage_lag2",
            "mortgage_lag3",
            "mortgage_exposure_lag3",
            "exposure",
            "month_id",
            "RegionName",
        ]
    ).copy()

    return work


def fit_model_a(df: pd.DataFrame):
    """Model A: FE with entity and time fixed effects using PanelOLS."""
    panel = df.set_index(["RegionName", "date"]).sort_index()
    y = panel["price_growth"]
    x = panel[["mortgage_exposure_lag3", "price_growth_lag1"]]

    model_std = PanelOLS(y, x, entity_effects=True, time_effects=True).fit(
        cov_type="unadjusted"
    )
    model_cluster = PanelOLS(y, x, entity_effects=True, time_effects=True).fit(
        cov_type="clustered", cluster_entity=True
    )
    return model_std, model_cluster


def fit_model_b_did(df: pd.DataFrame):
    """Model B: Difference-in-Differences with FE controls."""
    panel = df.set_index(["RegionName", "date"]).sort_index()
    y = panel["price_growth"]
    x = panel[["treated_post", "price_growth_lag1"]]

    model_did = PanelOLS(y, x, entity_effects=True, time_effects=True).fit(
        cov_type="clustered", cluster_entity=True
    )
    return model_did


def run_diagnostics(df: pd.DataFrame, model_std, model_cluster) -> pd.DataFrame:
    """Run heteroskedasticity, VIF, and save residual diagnostic plots."""
    # Breusch-Pagan on non-FE regressors as a practical proxy.
    bp_x = add_constant(df[["mortgage_exposure_lag3", "price_growth_lag1"]])
    bp_test = het_breuschpagan(np.asarray(model_std.resids), bp_x)

    vif_x = add_constant(df[["mortgage_exposure_lag3", "price_growth_lag1"]])
    vif_rows = []
    for i, col in enumerate(vif_x.columns):
        if col == "const":
            continue
        vif_rows.append(
            {
                "variable": col,
                "vif": variance_inflation_factor(vif_x.values, i),
            }
        )
    vif_df = pd.DataFrame(vif_rows)

    diag_df = pd.DataFrame(
        {
            "metric": [
                "breusch_pagan_lm_stat",
                "breusch_pagan_lm_pvalue",
                "breusch_pagan_f_stat",
                "breusch_pagan_f_pvalue",
                "n_obs_model_a",
            ],
            "value": [bp_test[0], bp_test[1], bp_test[2], bp_test[3], model_cluster.nobs],
        }
    )

    diag_out = pd.concat(
        [
            diag_df,
            vif_df.rename(columns={"variable": "metric", "vif": "value"}),
        ],
        ignore_index=True,
    )

    # Residuals vs Fitted
    plt.figure(figsize=(10, 6))
    fitted = np.asarray(model_cluster.fitted_values.iloc[:, 0])
    resid = np.asarray(model_cluster.resids)
    plt.scatter(fitted, resid, alpha=0.25)
    plt.axhline(0.0, color="red", linestyle="--", linewidth=1)
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.title("M3: Residuals vs Fitted (Model A)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_residuals_vs_fitted.png", dpi=300)
    plt.close()

    # Q-Q plot
    plt.figure(figsize=(8, 8))
    stats.probplot(resid, dist="norm", plot=plt)
    plt.title("M3: Q-Q Plot (Model A Residuals)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_qq_plot.png", dpi=300)
    plt.close()

    return diag_out


def plot_did_pretrends(df: pd.DataFrame) -> None:
    """Plot treated vs control pre-trends for visual DiD assumption checks."""
    policy_cutoff = pd.Timestamp("2022-03-01")
    placebo_cutoff = pd.Timestamp("2021-03-01")

    pre = df[df["date"] < policy_cutoff].copy()
    group_means = (
        pre.groupby(["date", "treated"], as_index=False)["price_growth"]
        .mean()
        .rename(columns={"price_growth": "avg_price_growth"})
    )

    pretrend = (
        group_means
        .pivot(index="date", columns="treated", values="avg_price_growth")
        .sort_index()
        .rename(columns={0: "control", 1: "treated"})
    )

    # Smooth monthly noise slightly to make trend differences easier to read.
    pretrend_smooth = pretrend.rolling(window=3, min_periods=1).mean()

    plt.figure(figsize=(11, 6))
    if "control" in pretrend_smooth.columns:
        plt.plot(
            pretrend_smooth.index,
            pretrend_smooth["control"],
            linewidth=2,
            label="Control metros (3-mo mean)",
        )
    if "treated" in pretrend_smooth.columns:
        plt.plot(
            pretrend_smooth.index,
            pretrend_smooth["treated"],
            linewidth=2,
            label="Treated metros (3-mo mean)",
        )

    plt.axvline(
        placebo_cutoff,
        color="orange",
        linestyle=":",
        linewidth=2,
        label="Placebo cutoff (2021-03)",
    )
    plt.axvline(
        policy_cutoff,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Policy cutoff (2022-03)",
    )
    plt.title("M3: DiD Pre-Trends Check (Treated vs Control)")
    plt.xlabel("Date")
    plt.ylabel("Average Quarterly Price Growth (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_did_pretrends.png", dpi=300)
    plt.close()


def run_robustness_checks(df: pd.DataFrame, model_std, model_cluster) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run three robustness checks and return output tables."""
    # 1) Compare standard vs clustered SE for key FE coefficient.
    key = "mortgage_exposure_lag3"
    se_compare = pd.DataFrame(
        {
            "coefficient": [key],
            "coef_standard": [model_std.params.get(key, np.nan)],
            "se_standard": [model_std.std_errors.get(key, np.nan)],
            "coef_clustered": [model_cluster.params.get(key, np.nan)],
            "se_clustered": [model_cluster.std_errors.get(key, np.nan)],
        }
    )

    # 2) Alternative lag structures.
    lag_rows = []
    for lag in [1, 2, 3]:
        lag_var = f"mortgage_lag{lag}"
        df_lag = df.copy()
        df_lag["mortgage_exposure_lag"] = df_lag[lag_var] * df_lag["exposure"]

        panel_lag = df_lag.set_index(["RegionName", "date"]).sort_index()
        y_lag = panel_lag["price_growth"]
        x_lag = panel_lag[["mortgage_exposure_lag", "price_growth_lag1"]]

        model_lag = PanelOLS(
            y_lag, x_lag, entity_effects=True, time_effects=True
        ).fit(
            cov_type="clustered", cluster_entity=True
        )

        lag_rows.append(
            {
                "lag": lag,
                "coef": model_lag.params.get("mortgage_exposure_lag", np.nan),
                "std_err": model_lag.std_errors.get("mortgage_exposure_lag", np.nan),
                "p_value": model_lag.pvalues.get("mortgage_exposure_lag", np.nan),
                "n_obs": model_lag.nobs,
            }
        )

    lag_table = pd.DataFrame(lag_rows)

    # 3) Exclude outlier COVID shock window and re-estimate.
    mask_outlier = (df["date"] >= pd.Timestamp("2020-03-01")) & (
        df["date"] <= pd.Timestamp("2020-05-31")
    )
    df_no_outlier = df.loc[~mask_outlier].copy()

    panel_no_outlier = df_no_outlier.set_index(["RegionName", "date"]).sort_index()
    y_no_outlier = panel_no_outlier["price_growth"]
    x_no_outlier = panel_no_outlier[["mortgage_exposure_lag3", "price_growth_lag1"]]
    model_no_outlier = PanelOLS(
        y_no_outlier, x_no_outlier, entity_effects=True, time_effects=True
    ).fit(
        cov_type="clustered", cluster_entity=True
    )

    outlier_table = pd.DataFrame(
        {
            "specification": ["baseline", "exclude_2020_03_to_2020_05"],
            "coef_mortgage_exposure_lag3": [
                model_cluster.params.get("mortgage_exposure_lag3", np.nan),
                model_no_outlier.params.get("mortgage_exposure_lag3", np.nan),
            ],
            "se_mortgage_exposure_lag3": [
                model_cluster.std_errors.get("mortgage_exposure_lag3", np.nan),
                model_no_outlier.std_errors.get("mortgage_exposure_lag3", np.nan),
            ],
            "p_value_mortgage_exposure_lag3": [
                model_cluster.pvalues.get("mortgage_exposure_lag3", np.nan),
                model_no_outlier.pvalues.get("mortgage_exposure_lag3", np.nan),
            ],
            "n_obs": [model_cluster.nobs, model_no_outlier.nobs],
        }
    )

    # 4) Placebo test for DiD on pre-treatment sample.
    placebo_cutoff = pd.Timestamp("2021-03-01")
    actual_cutoff = pd.Timestamp("2022-03-01")
    df_pre = df[df["date"] < actual_cutoff].copy()
    df_pre["placebo_post"] = (df_pre["date"] >= placebo_cutoff).astype(int)
    df_pre["treated_placebo"] = df_pre["treated"] * df_pre["placebo_post"]

    panel_pre = df_pre.set_index(["RegionName", "date"]).sort_index()
    y_pre = panel_pre["price_growth"]
    x_pre = panel_pre[["treated_placebo", "price_growth_lag1"]]
    model_placebo = PanelOLS(
        y_pre, x_pre, entity_effects=True, time_effects=True
    ).fit(
        cov_type="clustered", cluster_entity=True
    )

    placebo_table = pd.DataFrame(
        {
            "specification": ["did_placebo_pretrend"],
            "coef_treated_placebo": [
                model_placebo.params.get("treated_placebo", np.nan)
            ],
            "se_treated_placebo": [
                model_placebo.std_errors.get("treated_placebo", np.nan)
            ],
            "p_value_treated_placebo": [
                model_placebo.pvalues.get("treated_placebo", np.nan)
            ],
            "n_obs": [model_placebo.nobs],
        }
    )

    robustness = pd.concat(
        [
            se_compare.assign(check="se_comparison"),
            outlier_table.assign(check="outlier_exclusion"),
            placebo_table.assign(check="did_placebo"),
        ],
        ignore_index=True,
        sort=False,
    )

    return lag_table, robustness


def get_ml_feature_columns() -> list[str]:
    """Return feature columns used for ML models."""
    return [
        "MORTGAGE30US",
        "mortgage_lag1",
        "mortgage_lag2",
        "mortgage_lag3",
        "price_growth_lag1",
        "exposure",
        "mortgage_exposure_lag3",
        "treated",
        "post_hike",
        "treated_post",
        "SizeRank",
        "year",
        "quarter",
    ]


def get_ml_model_specs() -> dict[str, object]:
    """Return ML model configurations for benchmark comparisons."""
    return {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=20,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.8,
            random_state=42,
        ),
    }


def run_time_series_cross_validation(
    ml_df: pd.DataFrame,
    feature_cols: list[str],
    model_specs: dict[str, object],
    n_splits: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run expanding-window time-series cross-validation by date."""
    unique_dates = np.sort(ml_df["date"].unique())
    if len(unique_dates) < 12:
        raise ValueError("Not enough time periods for time-series cross-validation.")

    initial_train_size = max(8, int(len(unique_dates) * 0.5))
    remaining = len(unique_dates) - initial_train_size
    effective_splits = max(1, min(n_splits, remaining))
    fold_size = max(1, remaining // effective_splits)

    rows = []
    for fold in range(effective_splits):
        train_end_idx = initial_train_size + fold * fold_size
        test_start_idx = train_end_idx
        if test_start_idx >= len(unique_dates):
            continue

        if fold == effective_splits - 1:
            test_end_idx = len(unique_dates)
        else:
            test_end_idx = min(len(unique_dates), test_start_idx + fold_size)

        train_end_date = pd.Timestamp(unique_dates[train_end_idx - 1])
        test_start_date = pd.Timestamp(unique_dates[test_start_idx])
        test_end_date = pd.Timestamp(unique_dates[test_end_idx - 1])

        train = ml_df[ml_df["date"] <= train_end_date].copy()
        test = ml_df[
            (ml_df["date"] >= test_start_date) & (ml_df["date"] <= test_end_date)
        ].copy()

        if train.empty or test.empty:
            continue

        X_train = train[feature_cols]
        y_train = train["price_growth"]
        X_test = test[feature_cols]
        y_test = test["price_growth"]

        for model_name, base_model in model_specs.items():
            model = clone(base_model)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            rows.append(
                {
                    "fold": fold + 1,
                    "model": model_name,
                    "train_end": train_end_date.strftime("%Y-%m-%d"),
                    "test_start": test_start_date.strftime("%Y-%m-%d"),
                    "test_end": test_end_date.strftime("%Y-%m-%d"),
                    "train_rows": len(train),
                    "test_rows": len(test),
                    "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
                    "mae": float(mean_absolute_error(y_test, preds)),
                    "r2": float(r2_score(y_test, preds)),
                }
            )

    cv_results = pd.DataFrame(rows)
    if cv_results.empty:
        raise ValueError("Time-series cross-validation produced no valid folds.")

    cv_summary = (
        cv_results.groupby("model", as_index=False)
        .agg(
            folds=("fold", "nunique"),
            rmse_mean=("rmse", "mean"),
            rmse_std=("rmse", "std"),
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            r2_mean=("r2", "mean"),
            r2_std=("r2", "std"),
        )
        .sort_values("rmse_mean")
        .reset_index(drop=True)
    )
    cv_summary["rank_by_cv_rmse"] = np.arange(1, len(cv_summary) + 1)

    return cv_results, cv_summary


def run_machine_learning_models(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Benchmark ML regressors on holdout data and expanding-window CV."""
    ml_df = df.copy()
    ml_df["year"] = ml_df["date"].dt.year
    ml_df["quarter"] = ml_df["date"].dt.quarter

    feature_cols = get_ml_feature_columns()
    model_specs = get_ml_model_specs()

    ml_df = ml_df.dropna(subset=feature_cols + ["price_growth", "date"]).copy()
    unique_dates = np.sort(ml_df["date"].unique())
    if len(unique_dates) < 10:
        raise ValueError("Not enough time periods for machine learning train/test split.")

    split_idx = max(1, int(len(unique_dates) * 0.8))
    split_idx = min(split_idx, len(unique_dates) - 1)
    split_date = pd.Timestamp(unique_dates[split_idx])

    train = ml_df[ml_df["date"] < split_date].copy()
    test = ml_df[ml_df["date"] >= split_date].copy()

    if train.empty or test.empty:
        raise ValueError("Time split produced an empty train or test set for machine learning.")

    X_train = train[feature_cols]
    y_train = train["price_growth"]
    X_test = test[feature_cols]
    y_test = test["price_growth"]

    metric_rows = []
    predictions_by_model: dict[str, pd.DataFrame] = {}
    fitted_models = {}

    for name, base_model in model_specs.items():
        model = clone(base_model)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        metric_rows.append(
            {
                "model": name,
                "train_rows": len(train),
                "test_rows": len(test),
                "split_date": split_date.strftime("%Y-%m-%d"),
                "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
                "mae": float(mean_absolute_error(y_test, preds)),
                "r2": float(r2_score(y_test, preds)),
            }
        )

        predictions_by_model[name] = pd.DataFrame(
            {
                "date": test["date"].to_numpy(),
                "actual": y_test.to_numpy(),
                "predicted": preds,
            }
        )
        fitted_models[name] = model

    metrics = pd.DataFrame(metric_rows).sort_values("rmse").reset_index(drop=True)
    metrics["rank_by_rmse"] = np.arange(1, len(metrics) + 1)

    cv_results, cv_summary = run_time_series_cross_validation(
        ml_df=ml_df,
        feature_cols=feature_cols,
        model_specs=model_specs,
        n_splits=3,
    )

    best_model_name = cv_summary.loc[0, "model"]
    best_model = fitted_models[best_model_name]
    best_preds = predictions_by_model[best_model_name]

    if hasattr(best_model, "feature_importances_"):
        importance_values = np.asarray(best_model.feature_importances_)
    elif hasattr(best_model, "coef_"):
        importance_values = np.abs(np.asarray(best_model.coef_))
    else:
        importance_values = np.full(len(feature_cols), np.nan)

    feature_importance = (
        pd.DataFrame({"feature": feature_cols, "importance": importance_values})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    feature_importance.insert(0, "model", best_model_name)

    plot_df = (
        best_preds.groupby("date", as_index=False)[["actual", "predicted"]]
        .mean()
        .sort_values("date")
    )

    plt.figure(figsize=(11, 6))
    plt.plot(plot_df["date"], plot_df["actual"], linewidth=2, label="Actual mean price growth")
    plt.plot(
        plot_df["date"],
        plot_df["predicted"],
        linewidth=2,
        label=f"Predicted ({best_model_name})",
    )
    plt.title("M3 ML: Actual vs Predicted Price Growth (Holdout)")
    plt.xlabel("Date")
    plt.ylabel("Average Price Growth (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_ml_actual_vs_predicted.png", dpi=300)
    plt.close()

    return metrics, feature_importance, cv_results, cv_summary


def significance_stars(p_value: float) -> str:
    """Return significance stars for conventional thresholds."""
    if pd.isna(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def build_regression_table(model_cluster, model_did) -> pd.DataFrame:
    """Create publication-ready side-by-side comparison table."""
    rows = []
    keys = ["mortgage_exposure_lag3", "price_growth_lag1", "treated_post"]

    for key in keys:
        a_coef = model_cluster.params.get(key, np.nan)
        a_se = model_cluster.std_errors.get(key, np.nan)
        a_t = model_cluster.tstats.get(key, np.nan)
        a_p = model_cluster.pvalues.get(key, np.nan)

        b_coef = model_did.params.get(key, np.nan)
        b_se = model_did.std_errors.get(key, np.nan)
        b_t = model_did.tstats.get(key, np.nan)
        b_p = model_did.pvalues.get(key, np.nan)

        rows.append(
            {
                "variable": key,
                "model_a_coef": a_coef,
                "model_a_se": a_se,
                "model_a_t": a_t,
                "model_a_p": a_p,
                "model_a_sig": significance_stars(a_p),
                "model_a_coef_star": (
                    f"{a_coef:.4f}{significance_stars(a_p)}" if pd.notna(a_coef) else ""
                ),
                "model_b_did_coef": b_coef,
                "model_b_did_se": b_se,
                "model_b_did_t": b_t,
                "model_b_did_p": b_p,
                "model_b_did_sig": significance_stars(b_p),
                "model_b_did_coef_star": (
                    f"{b_coef:.4f}{significance_stars(b_p)}" if pd.notna(b_coef) else ""
                ),
            }
        )

    # Notes rows to satisfy publication table metadata requirements.
    note_rows = [
        {
            "variable": "Entity FE",
            "model_a_coef_star": "Yes",
            "model_b_did_coef_star": "Yes",
        },
        {
            "variable": "Time FE",
            "model_a_coef_star": "Yes",
            "model_b_did_coef_star": "Yes",
        },
        {
            "variable": "Clustered SE",
            "model_a_coef_star": "Yes",
            "model_b_did_coef_star": "Yes",
        },
        {
            "variable": "N",
            "model_a_coef_star": f"{int(model_cluster.nobs)}",
            "model_b_did_coef_star": f"{int(model_did.nobs)}",
        },
        {
            "variable": "R2",
            "model_a_coef_star": f"{model_cluster.rsquared:.4f}",
            "model_b_did_coef_star": f"{model_did.rsquared:.4f}",
        },
        {
            "variable": "Significance",
            "model_a_coef_star": "*** p<0.01, ** p<0.05, * p<0.10",
            "model_b_did_coef_star": "*** p<0.01, ** p<0.05, * p<0.10",
        },
    ]

    for note in note_rows:
        rows.append(
            {
                "variable": note["variable"],
                "model_a_coef": np.nan,
                "model_a_se": np.nan,
                "model_a_t": np.nan,
                "model_a_p": np.nan,
                "model_a_sig": "",
                "model_a_coef_star": note["model_a_coef_star"],
                "model_b_did_coef": np.nan,
                "model_b_did_se": np.nan,
                "model_b_did_t": np.nan,
                "model_b_did_p": np.nan,
                "model_b_did_sig": "",
                "model_b_did_coef_star": note["model_b_did_coef_star"],
            }
        )

    return pd.DataFrame(rows)


def save_outputs(
    reg_table: pd.DataFrame,
    diagnostics: pd.DataFrame,
    lag_table: pd.DataFrame,
    robustness: pd.DataFrame,
    model_a_cluster,
    model_b_did,
    ml_metrics: pd.DataFrame | None = None,
    ml_feature_importance: pd.DataFrame | None = None,
    ml_cv_results: pd.DataFrame | None = None,
    ml_cv_summary: pd.DataFrame | None = None,
) -> None:
    """Write all tables and text summaries to results/tables."""
    reg_table.to_csv(TABLES_DIR / "M3_regression_table.csv", index=False)
    diagnostics.to_csv(TABLES_DIR / "M3_diagnostics.csv", index=False)
    lag_table.to_csv(TABLES_DIR / "M3_robustness_lags.csv", index=False)
    robustness.to_csv(TABLES_DIR / "M3_robustness_checks.csv", index=False)
    if ml_metrics is not None:
        ml_metrics.to_csv(TABLES_DIR / "M3_ml_metrics.csv", index=False)
    if ml_feature_importance is not None:
        ml_feature_importance.to_csv(TABLES_DIR / "M3_ml_feature_importance.csv", index=False)
    if ml_cv_results is not None:
        ml_cv_results.to_csv(TABLES_DIR / "M3_ml_cv_results.csv", index=False)
    if ml_cv_summary is not None:
        ml_cv_summary.to_csv(TABLES_DIR / "M3_ml_cv_summary.csv", index=False)

    with open(TABLES_DIR / "M3_modelA_summary.txt", "w", encoding="utf-8") as f:
        f.write(str(model_a_cluster.summary))

    with open(TABLES_DIR / "M3_modelB_did_summary.txt", "w", encoding="utf-8") as f:
        f.write(str(model_b_did.summary))


def main() -> None:
    ensure_directories()

    df_raw = load_data()
    df = engineer_features(df_raw)

    model_a_std, model_a_cluster = fit_model_a(df)
    model_b_did = fit_model_b_did(df)

    diagnostics = run_diagnostics(df, model_a_std, model_a_cluster)
    plot_did_pretrends(df)
    lag_table, robustness = run_robustness_checks(df, model_a_std, model_a_cluster)
    reg_table = build_regression_table(model_a_cluster, model_b_did)
    ml_metrics, ml_feature_importance, ml_cv_results, ml_cv_summary = run_machine_learning_models(df)

    save_outputs(
        reg_table=reg_table,
        diagnostics=diagnostics,
        lag_table=lag_table,
        robustness=robustness,
        model_a_cluster=model_a_cluster,
        model_b_did=model_b_did,
        ml_metrics=ml_metrics,
        ml_feature_importance=ml_feature_importance,
        ml_cv_results=ml_cv_results,
        ml_cv_summary=ml_cv_summary,
    )

    print("M3 modeling pipeline complete.")
    print(f"Tables saved to: {TABLES_DIR}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
