# src/data/data_profiler.py
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class DataProfiler:
    """Automated data profiling for fraud detection datasets."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profile: dict[str, Any] = {}

    def generate_profile(self) -> dict[str, Any]:
        """Generate comprehensive data profile."""
        self.profile = {
            "basic_info": self._get_basic_info(),
            "data_types": self._get_data_types(),
            "missing_values": self._get_missing_values(),
            "numerical_stats": self._get_numerical_stats(),
            "categorical_stats": self._get_categorical_stats(),
            "data_quality_issues": self._identify_quality_issues(),
            "class_distribution": self._get_class_distribution(),
            "temporal_analysis": self._get_temporal_analysis(),
            "profiling_timestamp": datetime.now().isoformat(),
        }
        return self.profile

    def _get_basic_info(self) -> dict[str, Any]:
        """Get basic dataset information."""
        return {
            "n_rows": len(self.df),
            "n_columns": len(self.df.columns),
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / 1024**2,
            "column_names": self.df.columns.tolist(),
        }

    def _get_data_types(self) -> dict[str, str]:
        """Get data types for each column."""
        return {str(col): str(dtype) for col, dtype in self.df.dtypes.items()}

    def _get_missing_values(self) -> dict[str, dict[str, Any]]:
        """Analyze missing values."""
        missing_stats = {}
        for col in self.df.columns:
            n_missing = self.df[col].isnull().sum()
            missing_stats[col] = {
                "n_missing": int(n_missing),
                "pct_missing": round(n_missing / len(self.df) * 100, 2),
                "is_problematic": n_missing / len(self.df) > 0.3,  # >30% missing
            }
        return missing_stats

    def _get_numerical_stats(self) -> dict[str, dict[str, float]]:
        """Get statistics for numerical columns."""
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        stats = {}

        for col in numerical_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:  # Only compute stats if we have data
                stats[col] = {
                    "mean": round(col_data.mean(), 4),
                    "median": round(col_data.median(), 4),
                    "std": round(col_data.std(), 4),
                    "min": round(col_data.min(), 4),
                    "max": round(col_data.max(), 4),
                    "q1": round(col_data.quantile(0.25), 4),
                    "q3": round(col_data.quantile(0.75), 4),
                    "iqr": round(col_data.quantile(0.75) - col_data.quantile(0.25), 4),
                    "n_outliers": int(self._count_outliers(col_data)),
                    "n_zeros": int((col_data == 0).sum()),
                    "n_negative": int((col_data < 0).sum()),
                }
        return stats

    def _get_categorical_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for categorical columns."""
        categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns
        stats = {}

        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            stats[col] = {
                "n_unique": self.df[col].nunique(),
                "top_5_values": value_counts.head(5).to_dict(),
                "has_high_cardinality": self.df[col].nunique() > 100,
            }
        return stats

    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method."""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return ((series < lower_bound) | (series > upper_bound)).sum()

    def _identify_quality_issues(self) -> list[dict[str, str]]:
        """Identify potential data quality issues."""
        issues = []

        # Check for duplicate rows
        n_duplicates = self.df.duplicated().sum()
        if n_duplicates > 0:
            issues.append(
                {
                    "type": "duplicate_rows",
                    "severity": "medium",
                    "description": f"Found {n_duplicates} duplicate rows",
                    "recommendation": "Investigate and remove duplicates if not intentional",
                }
            )

        # Check for constant columns
        for col in self.df.columns:
            if self.df[col].nunique() == 1:
                issues.append(
                    {
                        "type": "constant_column",
                        "severity": "high",
                        "description": f"Column '{col}' has only one unique value",
                        "recommendation": "Consider removing this column",
                    }
                )

        # Check for high missing data
        for col, missing_info in self._get_missing_values().items():
            if missing_info["is_problematic"]:
                issues.append(
                    {
                        "type": "high_missing_data",
                        "severity": "high",
                        "description": f"Column '{col}' has {missing_info['pct_missing']}% missing values",
                        "recommendation": "Consider imputation or removal",
                    }
                )

        # PaySim specific: Check balance consistency
        if all(
            col in self.df.columns
            for col in ["oldbalanceOrg", "newbalanceOrig", "amount"]
        ):
            # For outgoing transactions, newBalance should be oldBalance - amount
            balance_check = self.df[
                self.df["type"].isin(["CASH_OUT", "PAYMENT", "TRANSFER"])
            ]
            if len(balance_check) > 0:
                expected_balance = (
                    balance_check["oldbalanceOrg"] - balance_check["amount"]
                )
                balance_mismatch = (
                    abs(balance_check["newbalanceOrig"] - expected_balance) > 0.01
                ).sum()
                if balance_mismatch > 0:
                    issues.append(
                        {
                            "type": "balance_inconsistency",
                            "severity": "medium",
                            "description": f"Found {balance_mismatch} transactions with balance inconsistencies",
                            "recommendation": "Investigate balance calculation logic",
                        }
                    )

        return issues

    def _get_class_distribution(self) -> dict[str, Any]:
        """Analyze class distribution for fraud detection."""
        # Check for both common fraud column names
        fraud_col = None
        for col in ["isFraud", "is_fraud", "fraud", "label"]:  # Added 'isFraud'
            if col in self.df.columns:
                fraud_col = col
                break

        if fraud_col:
            fraud_counts = self.df[fraud_col].value_counts()
            total = len(self.df)
            fraud_cases = fraud_counts.get(1, 0)
            normal_cases = fraud_counts.get(0, 0)

            return {
                "fraud_column": fraud_col,
                "fraud_cases": int(fraud_cases),
                "normal_cases": int(normal_cases),
                "fraud_percentage": (
                    round(fraud_cases / total * 100, 2) if total > 0 else 0
                ),
                "imbalance_ratio": (
                    round(normal_cases / fraud_cases, 2)
                    if fraud_cases > 0
                    else float("inf")
                ),
                "is_highly_imbalanced": (
                    fraud_cases / total < 0.01 if total > 0 else False
                ),
            }
        return {"error": "No fraud label column found"}

    def _get_temporal_analysis(self) -> dict[str, Any]:
        """Analyze temporal aspects of the data."""
        temporal_stats = {}

        # Check for PaySim 'step' column (time in hours)
        if "step" in self.df.columns:
            temporal_stats["step_analysis"] = {
                "min_step": int(self.df["step"].min()),
                "max_step": int(self.df["step"].max()),
                "duration_hours": int(self.df["step"].max() - self.df["step"].min()),
                "duration_days": round(
                    (self.df["step"].max() - self.df["step"].min()) / 24, 2
                ),
                "unique_steps": int(self.df["step"].nunique()),
            }

            # Analyze fraud rate over time
            if any(col in self.df.columns for col in ["isFraud", "is_fraud"]):
                fraud_col = "isFraud" if "isFraud" in self.df.columns else "is_fraud"
                hourly_fraud = self.df.groupby("step")[fraud_col].mean()
                temporal_stats["fraud_temporal_pattern"] = {
                    "avg_hourly_fraud_rate": round(hourly_fraud.mean() * 100, 4),
                    "max_hourly_fraud_rate": round(hourly_fraud.max() * 100, 4),
                    "min_hourly_fraud_rate": round(hourly_fraud.min() * 100, 4),
                    "fraud_rate_std": round(hourly_fraud.std() * 100, 4),
                }

        # Check for actual datetime columns
        datetime_cols = self.df.select_dtypes(include=["datetime64"]).columns
        if len(datetime_cols) > 0:
            for col in datetime_cols:
                temporal_stats[col] = {
                    "min_date": str(self.df[col].min()),
                    "max_date": str(self.df[col].max()),
                    "date_range_days": (self.df[col].max() - self.df[col].min()).days,
                    "has_future_dates": self.df[col].max() > pd.Timestamp.now(),
                }

        return temporal_stats

    def export_profile(self, filepath: str) -> None:
        """Export profile to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.profile, f, indent=2, default=str)

    def get_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        if not self.profile:
            self.generate_profile()

        # Get fraud info
        fraud_info = self.profile.get("class_distribution", {})

        report = f"""
        Data Quality Summary Report
        ==========================
        Generated on: {self.profile['profiling_timestamp']}

        Basic Information:
        - Rows: {self.profile['basic_info']['n_rows']:,}
        - Columns: {self.profile['basic_info']['n_columns']}
        - Memory Usage: {self.profile['basic_info']['memory_usage_mb']:.2f} MB

        Class Distribution:
        - Fraud Cases: {fraud_info.get('fraud_cases', 'N/A')} ({fraud_info.get('fraud_percentage', 'N/A')}%)
        - Normal Cases: {fraud_info.get('normal_cases', 'N/A')}
        - Imbalance Ratio: 1:{fraud_info.get('imbalance_ratio', 'N/A')}

        Data Quality Issues Found: {len(self.profile['data_quality_issues'])}"""

        for issue in self.profile["data_quality_issues"]:
            report += f"\n- [{issue['severity'].upper()}] {issue['description']}"

        # Add temporal analysis if available
        temporal = self.profile.get("temporal_analysis", {})
        if "step_analysis" in temporal:
            step_info = temporal["step_analysis"]
            report += f"\n\nTemporal Coverage:\n- Duration: {step_info['duration_days']} days ({step_info['duration_hours']} hours)"

        return report


def quick_profile(df: pd.DataFrame, export_path: str = None) -> dict[str, Any]:
    """Quick profiling function for convenience."""
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()

    if export_path:
        profiler.export_profile(export_path)
        print(f"Profile exported to: {export_path}")

    print(profiler.get_summary_report())
    return profile
