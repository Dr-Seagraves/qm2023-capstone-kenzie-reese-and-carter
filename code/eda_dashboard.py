"""
Milestone 2: EDA Dashboard for QM 2023 Capstone Project
========================================================

This script implements the exploratory data analysis pipeline according to
M2 specifications. It generates 8 required visualizations and summary statistics.

Requirements:
- All plots are publication-ready (titles, labels, legends, captions)
- Every visualization saved to results/figures/ as PNG (300 DPI)
- Economic interpretations provided for each insight
- Summary markdown documenting key findings and M3 hypotheses

Author: QM 2023 Capstone Team
Date: March 2026
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.stats import pearsonr

# Import project configuration
sys.path.insert(0, os.path.dirname(__file__))
from config_paths import (
    ensure_directories,
    PROJECT_ROOT,
    FINAL_DATA_DIR,
    FIGURES_DIR,
    REPORTS_DIR
)

# Set visualization defaults
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("colorblind")
plt.rcParams["font.size"] = 11
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.labelsize"] = 12


class EDADashboard:
    """
    Main EDA pipeline class.
    
    Loads M1 output (final merged panels) and generates all required visualizations.
    """
    
    def __init__(self, data_type="metro"):
        """
        Initialize EDA Dashboard.
        
        Parameters
        ----------
        data_type : str
            Either "metro" for metro_mortgage_panel.csv or "reit" for reit_mortgage_panel.csv
        """
        self.ensure_dirs()
        self.data_type = data_type
        self.data = None
        self.outcome_var = None
        self.driver_var = None
        self.control_vars = []
        self.group_var = None
        self.load_data()
        
    def ensure_dirs(self):
        """Create required output directories."""
        ensure_directories()
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """Load M1 output based on data_type."""
        if self.data_type == "metro":
            filepath = FINAL_DATA_DIR / "metro_mortgage_panel.csv"
            self.outcome_var = "price_index"
            self.driver_var = "MORTGAGE30US"
            self.control_vars = ["RegionName", "StateName"]
            self.group_var = "RegionName"  # Or classify as Urban/Suburban
        else:
            filepath = FINAL_DATA_DIR / "reit_mortgage_panel.csv"
            self.outcome_var = "usdret"
            self.driver_var = "MORTGAGE30US"
            self.control_vars = ["market_equity", "btm", "beta"]
            self.group_var = "ticker"
        
        print(f"Loading {self.data_type} data from {filepath}...")
        self.data = pd.read_csv(filepath)
        print(f"Loaded {len(self.data)} rows, {len(self.data.columns)} columns")
        
        # Parse date column
        if "date" in self.data.columns:
            self.data["date"] = pd.to_datetime(self.data["date"])
        
        return self.data
    
    def print_summary_stats(self):
        """Print summary statistics for outcome and driver variables."""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        numeric_cols = [self.outcome_var, self.driver_var] + [
            c for c in self.control_vars if c in self.data.select_dtypes(include=[np.number]).columns
        ]
        print(self.data[numeric_cols].describe())
        print(f"\nMissing values:\n{self.data[numeric_cols].isnull().sum()}")
    
    # ========== PLOT 1: Correlation Heatmap ==========
    def plot_correlation_heatmap(self):
        """
        REQUIRED: Plot 1 - Correlation Heatmap
        
        Identifies which variables are strongly correlated with outcome.
        Warns of multicollinearity among controls.
        """
        print("\n[1] Creating Correlation Heatmap...")
        
        # Select numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix = self.data[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            square=True,
            cbar_kws={"label": "Correlation Coefficient"},
            ax=ax
        )
        ax.set_title(
            f"Correlation Matrix: {self.data_type.upper()} Dataset\n"
            f"Outcome: {self.outcome_var}, Driver: {self.driver_var}",
            fontsize=14,
            fontweight="bold"
        )
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "01_correlation_heatmap.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print interpretation
        outcome_corr = corr_matrix[self.outcome_var].sort_values(ascending=False)
        print(f"\n  Top correlations with {self.outcome_var}:")
        print(outcome_corr.head(5))
        
        return filepath
    
    # ========== PLOT 2: Time Series of Outcome ==========
    def plot_outcome_timeseries(self):
        """
        REQUIRED: Plot 2 - Time Series of Outcome Variable
        
        Visualizes trends, volatility, and outlier periods.
        """
        print("\n[2] Creating Outcome Time Series...")
        
        if "date" not in self.data.columns:
            print("  ⚠ No 'date' column found. Skipping time series plot.")
            return None
        
        # Aggregate across all entities
        ts_data = self.data.groupby("date")[self.outcome_var].mean()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(ts_data.index, ts_data.values, linewidth=2, color="steelblue")
        ax.fill_between(ts_data.index, ts_data.values, alpha=0.3, color="steelblue")
        
        ax.set_title(
            f"Average {self.outcome_var} Over Time ({self.data_type.upper()})",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel(f"{self.outcome_var}", fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "02_outcome_timeseries.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print statistics
        print(f"\n  Mean: {ts_data.mean():.4f}")
        print(f"  Std:  {ts_data.std():.4f}")
        print(f"  Min:  {ts_data.min():.4f} (on {ts_data.idxmin().date()})")
        print(f"  Max:  {ts_data.max():.4f} (on {ts_data.idxmax().date()})")
        
        return filepath
    
    # ========== PLOT 3: Dual-Axis Plot ==========
    def plot_dual_axis(self):
        """
        REQUIRED: Plot 3 - Dual-Axis Plot (Outcome vs. Driver)
        
        Visualizes co-movement between outcome and key driver.
        """
        print("\n[3] Creating Dual-Axis Plot...")
        
        if "date" not in self.data.columns:
            print("  ⚠ No 'date' column found. Skipping dual-axis plot.")
            return None
        
        # Aggregate across entities
        ts_outcome = self.data.groupby("date")[self.outcome_var].mean()
        ts_driver = self.data.groupby("date")[self.driver_var].mean()
        
        fig, ax1 = plt.subplots(figsize=(14, 6))
        
        # Left axis: outcome
        color1 = "steelblue"
        ax1.plot(ts_outcome.index, ts_outcome.values, color=color1, linewidth=2, label=self.outcome_var)
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel(self.outcome_var, color=color1, fontsize=12)
        ax1.tick_params(axis="y", labelcolor=color1)
        
        # Right axis: driver
        ax2 = ax1.twinx()
        color2 = "darkorange"
        ax2.plot(ts_driver.index, ts_driver.values, color=color2, linewidth=2, label=self.driver_var)
        ax2.set_ylabel(self.driver_var, color=color2, fontsize=12)
        ax2.tick_params(axis="y", labelcolor=color2)
        
        fig.suptitle(
            f"{self.outcome_var} vs. {self.driver_var} ({self.data_type.upper()})",
            fontsize=14,
            fontweight="bold"
        )
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "03_dual_axis.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Compute correlation
        corr = ts_outcome.corr(ts_driver)
        print(f"\n  Correlation between {self.outcome_var} and {self.driver_var}: {corr:.4f}")
        
        return filepath
    
    # ========== PLOT 4: Lagged Effect Analysis ==========
    def plot_lagged_effects(self, lags=[0, 1, 2, 3, 6, 12]):
        """
        REQUIRED: Plot 4 - Lagged Effect Analysis
        
        Determines optimal lag structure for driver variable.
        """
        print("\n[4] Creating Lagged Effect Analysis...")
        
        correlations = []
        for lag in lags:
            # Create lagged driver by entity
            self.data[f"{self.driver_var}_lag{lag}"] = \
                self.data.groupby(self.group_var)[self.driver_var].shift(lag)
            
            # Compute correlation (drop NaNs)
            valid = self.data[[self.outcome_var, f"{self.driver_var}_lag{lag}"]].dropna()
            if len(valid) > 0:
                corr = valid[self.outcome_var].corr(valid[f"{self.driver_var}_lag{lag}"])
            else:
                corr = np.nan
            correlations.append(corr)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["darkred" if c == min([x for x in correlations if not np.isnan(x)]) else "steelblue" for c in correlations]
        ax.bar(range(len(lags)), correlations, color=colors, alpha=0.7, edgecolor="black")
        ax.set_xticks(range(len(lags)))
        ax.set_xticklabels(lags)
        ax.set_xlabel("Lag (periods)", fontsize=12)
        ax.set_ylabel("Correlation with Outcome", fontsize=12)
        ax.set_title(
            f"Lagged Effect Analysis: {self.driver_var} → {self.outcome_var}",
            fontsize=14,
            fontweight="bold"
        )
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "04_lagged_effects.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print optimal lag
        optimal_lag = lags[np.nanargmin(np.abs(correlations))]
        print(f"\n  Optimal lag: {optimal_lag} periods")
        print(f"  Lag correlations: {dict(zip(lags, [f'{c:.4f}' for c in correlations]))}")
        
        # Clean up lag columns
        for lag in lags:
            self.data.drop(f"{self.driver_var}_lag{lag}", axis=1, inplace=True)
        
        return filepath
    
    # ========== PLOT 5: Group Box Plots ==========
    def plot_group_boxplots(self, n_groups=10):
        """
        CONDITIONAL: Plot 5 - Group Box Plots
        
        Compares outcome distributions across groups.
        """
        print(f"\n[5] Creating Group Box Plots (top {n_groups} groups)...")
        
        if self.group_var is None or self.group_var not in self.data.columns:
            print("  ⚠ No valid grouping variable. Skipping group box plots.")
            return None
        
        # Get top groups by frequency
        top_groups = self.data[self.group_var].value_counts().head(n_groups).index
        plot_data = self.data[self.data[self.group_var].isin(top_groups)]
        
        fig, ax = plt.subplots(figsize=(14, 6))
        plot_data.boxplot(column=self.outcome_var, by=self.group_var, ax=ax)
        
        ax.set_title(
            f"Distribution of {self.outcome_var} by {self.group_var} (Top {n_groups})",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel(self.group_var, fontsize=12)
        ax.set_ylabel(self.outcome_var, fontsize=12)
        plt.suptitle("")  # Remove default suptitle
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "05_group_boxplots.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print group statistics
        print(f"\n  Group statistics for {self.outcome_var}:")
        print(plot_data.groupby(self.group_var)[self.outcome_var].describe())
        
        return filepath
    
    # ========== PLOT 6: Group Sensitivity Analysis ==========
    def plot_group_sensitivity(self, threshold=-0.3, n_groups=10):
        """
        CONDITIONAL: Plot 6 - Group Sensitivity Analysis
        
        Identifies groups most sensitive to driver variable.
        """
        print(f"\n[6] Creating Group Sensitivity Analysis...")
        
        if self.group_var is None or self.group_var not in self.data.columns:
            print("  ⚠ No valid grouping variable. Using rolling correlation instead.")
            return self.plot_rolling_correlation()
        
        # Compute group-level sensitivity
        group_sensitivity = {}
        for group in self.data[self.group_var].unique():
            group_data = self.data[self.data[self.group_var] == group]
            valid = group_data[[self.outcome_var, self.driver_var]].dropna()
            if len(valid) > 10:
                sens = valid[self.outcome_var].corr(valid[self.driver_var])
                group_sensitivity[group] = sens
        
        # Sort and plot top groups
        sensitivity_series = pd.Series(group_sensitivity).sort_values()
        # Select bottom n and top n groups
        bottom_idx = list(range(min(n_groups, len(sensitivity_series))))
        top_idx = list(range(max(0, len(sensitivity_series) - n_groups), len(sensitivity_series)))
        selected_idx = sorted(set(bottom_idx + top_idx))
        sensitivity_series = sensitivity_series.iloc[selected_idx]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = ["darkred" if s < threshold else "steelblue" for s in sensitivity_series.values]
        sensitivity_series.plot(kind="barh", color=colors, ax=ax, alpha=0.7, edgecolor="black")
        ax.set_xlabel("Correlation with Driver", fontsize=12)
        ax.set_ylabel(self.group_var, fontsize=12)
        ax.set_title(
            f"Group Sensitivity to {self.driver_var}",
            fontsize=14,
            fontweight="bold"
        )
        ax.axvline(x=threshold, color="red", linestyle="--", linewidth=2, label=f"Sensitivity Threshold ({threshold})")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="x")
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "06_group_sensitivity.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print sensitive groups
        sensitive = sensitivity_series[sensitivity_series < threshold]
        resilient = sensitivity_series[sensitivity_series >= threshold]
        print(f"\n  Sensitive groups (r < {threshold}): {len(sensitive)}")
        print(f"  Resilient groups (r >= {threshold}): {len(resilient)}")
        
        return filepath
    
    def plot_rolling_correlation(self, window=12):
        """
        ALTERNATIVE: Plot 7 - Rolling Correlation Analysis
        
        When numeric control variables are unavailable, this plot shows
        the stability of the outcome-driver relationship over time using
        a rolling window correlation coefficient.
        """
        print(f"\n[7] Creating Rolling Correlation Analysis (window={window} quarters)...")
        
        if "date" not in self.data.columns:
            print("  ⚠ No 'date' column. Skipping rolling correlation.")
            return None
        
        # Sort by date and aggregate
        data_sorted = self.data.sort_values("date")
        ts_outcome = data_sorted.groupby("date")[self.outcome_var].mean()
        ts_driver = data_sorted.groupby("date")[self.driver_var].mean()
        
        rolling_corr = ts_outcome.rolling(window=window).corr(ts_driver)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(rolling_corr.index, rolling_corr.values, linewidth=2.5, color="steelblue", label="Moving Correlation")
        ax.fill_between(rolling_corr.index, rolling_corr.values, alpha=0.3, color="steelblue")
        ax.set_title(
            f"Rolling Correlation: {self.outcome_var} vs. {self.driver_var} ({window}-Quarter Window)",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Correlation Coefficient", fontsize=12)
        ax.axhline(y=0, color="red", linestyle="--", linewidth=1.5, label="Zero Correlation")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "07_rolling_correlation.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        # Print summary statistics
        valid_corr = rolling_corr.dropna()
        print(f"  Mean rolling correlation: {valid_corr.mean():.4f}")
        print(f"  Std deviation: {valid_corr.std():.4f}")
        print(f"  Range: [{valid_corr.min():.4f}, {valid_corr.max():.4f}]")
        
        return filepath
    
    # ========== PLOT 7: Control Variable Scatter Plots ==========
    def plot_control_scatters(self):
        """
        REQUIRED: Plot 7 - Factor/Control Variable Scatter Plots
        
        Visualizes bivariate relationships with outcome.
        """
        print("\n[7] Creating Control Variable Scatter Plots...")
        
        numeric_controls = [
            c for c in self.control_vars 
            if c in self.data.select_dtypes(include=[np.number]).columns
        ]
        
        if not numeric_controls:
            print("  ⚠ No numeric control variables found.")
            return None
        
        n_plots = min(len(numeric_controls), 4)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, control in enumerate(numeric_controls[:n_plots]):
            ax = axes[idx]
            
            # Remove NaNs
            valid = self.data[[self.outcome_var, control]].dropna()
            
            # Scatter plot with regression line
            ax.scatter(valid[control], valid[self.outcome_var], alpha=0.5, s=20)
            
            # Add regression line
            z = np.polyfit(valid[control], valid[self.outcome_var], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[control].min(), valid[control].max(), 100)
            ax.plot(x_line, p(x_line), "r-", linewidth=2, label="Regression Line")
            
            ax.set_xlabel(control, fontsize=10)
            ax.set_ylabel(self.outcome_var, fontsize=10)
            ax.set_title(f"{self.outcome_var} vs. {control}")
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Compute correlation
            corr = valid[self.outcome_var].corr(valid[control])
            ax.text(0.05, 0.95, f"r = {corr:.3f}", 
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        
        # Hide unused subplots
        for idx in range(n_plots, 4):
            axes[idx].set_visible(False)
        
        fig.suptitle(f"Control Variables vs. {self.outcome_var}", fontsize=14, fontweight="bold")
        plt.tight_layout()
        
        filepath = FIGURES_DIR / "07_control_scatters.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"  ✓ Saved to {filepath}")
        plt.close()
        
        return filepath
    
    # ========== PLOT 8: Time Series Decomposition ==========
    def plot_decomposition(self):
        """
        REQUIRED: Plot 8 - Time Series Decomposition
        
        Separates trend, seasonal, and residual components.
        """
        print("\n[8] Creating Time Series Decomposition...")
        
        if "date" not in self.data.columns:
            print("  ⚠ No 'date' column. Skipping decomposition.")
            return None
        
        # Aggregate to time series
        ts_data = self.data.sort_values("date").groupby("date")[self.outcome_var].mean()
        
        # Determine period (4 for quarterly, 12 for monthly, 252 for daily)
        period = 4 if len(ts_data) > 200 else 12
        
        try:
            decomposition = seasonal_decompose(ts_data, model="additive", period=period)
            
            fig, axes = plt.subplots(4, 1, figsize=(14, 10))
            
            ts_data.plot(ax=axes[0], color="steelblue", linewidth=2)
            axes[0].set_ylabel("Observed")
            axes[0].set_title(f"Time Series Decomposition: {self.outcome_var}", fontsize=14, fontweight="bold")
            axes[0].grid(True, alpha=0.3)
            
            decomposition.trend.plot(ax=axes[1], color="darkgreen", linewidth=2)
            axes[1].set_ylabel("Trend")
            axes[1].grid(True, alpha=0.3)
            
            decomposition.seasonal.plot(ax=axes[2], color="darkorange", linewidth=2)
            axes[2].set_ylabel("Seasonal")
            axes[2].grid(True, alpha=0.3)
            
            decomposition.resid.plot(ax=axes[3], color="darkred", linewidth=1)
            axes[3].set_ylabel("Residual")
            axes[3].set_xlabel("Date")
            axes[3].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filepath = FIGURES_DIR / "08_decomposition.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"  ✓ Saved to {filepath}")
            plt.close()
            
            # Print decomposition statistics
            print(f"\n  Decomposition Period: {period} periods")
            print(f"  Trend explains: {(1 - decomposition.resid.var() / ts_data.var()):.2%} of variance")
            
            return filepath
        except Exception as e:
            print(f"  ⚠ Decomposition failed: {e}")
            return None
    
    def run_all(self):
        """Execute full EDA pipeline."""
        print("\n" + "="*60)
        print(f"EDA DASHBOARD FOR {self.data_type.upper()} DATA")
        print("="*60)
        
        self.print_summary_stats()
        
        # Generate all plots
        plots = {
            "1_correlation": self.plot_correlation_heatmap(),
            "2_timeseries": self.plot_outcome_timeseries(),
            "3_dual_axis": self.plot_dual_axis(),
            "4_lagged": self.plot_lagged_effects(),
            "5_boxplots": self.plot_group_boxplots(),
            "6_sensitivity": self.plot_group_sensitivity(),
            "7_rolling_corr": self.plot_rolling_correlation(),  # Alternative to control scatters
            "8_decomposition": self.plot_decomposition(),
        }
        
        print("\n" + "="*60)
        print("EDA DASHBOARD COMPLETE")
        print("="*60)
        print(f"\nGenerated plots: {sum(1 for v in plots.values() if v is not None)}/8")
        print(f"All figures saved to: {FIGURES_DIR}")
        
        return plots


def main():
    """Main entry point."""
    # Choose data type: "metro" or "reit"
    data_type = "metro"  # Change to "reit" for REIT analysis
    
    # Initialize and run EDA
    eda = EDADashboard(data_type=data_type)
    eda.run_all()


if __name__ == "__main__":
    main()
