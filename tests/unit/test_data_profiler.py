# tests/unit/test_data_profiler.py
import json

import numpy as np
import pandas as pd
import pytest

from src.data.data_profiler import DataProfiler


@pytest.fixture
def sample_df():
    """Returns a sample DataFrame for profiling."""
    data = {
        "step": [1, 2, 3, 4, 5],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
        "amount": [100.0, 200.0, 50.0, 150.0, 300.0],
        "isFraud": [0, 1, 0, 0, 1],
        "isFlaggedFraud": [0, 0, 0, 1, 0],
        "oldbalanceOrg": [1000.0, 2000.0, 500.0, 1500.0, 3000.0],
        "newbalanceOrig": [900.0, 1800.0, 450.0, 1350.0, 2700.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def profiler(sample_df):
    """Returns a DataProfiler instance."""
    return DataProfiler(sample_df)


def test_initialization(profiler, sample_df):
    """Tests that the profiler is initialized correctly."""
    assert profiler.df.equals(sample_df)


def test_generate_profile(profiler):
    """Tests the structure of the generated profile."""
    profile = profiler.generate_profile()

    assert "basic_info" in profile
    assert "data_types" in profile
    assert "missing_values" in profile
    assert "numerical_stats" in profile
    assert "categorical_stats" in profile
    assert "data_quality_issues" in profile
    assert "class_distribution" in profile
    assert "temporal_analysis" in profile


def test_export_profile(profiler, tmp_path):
    """Tests that the profile is exported to a JSON file."""
    profiler.generate_profile()
    file_path = tmp_path / "profile.json"
    profiler.export_profile(str(file_path))

    assert file_path.exists()
    with open(file_path) as f:
        profile = json.load(f)
    assert "basic_info" in profile


def test_get_summary_report(profiler):
    """Tests that the summary report is a non-empty string."""
    profiler.generate_profile()
    report = profiler.get_summary_report()
    assert isinstance(report, str)
    assert len(report) > 0


def test_missing_values_is_problematic():
    """Tests that a high percentage of missing values is flagged as problematic."""
    data = {"col1": [1, 2, 3, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert profile["missing_values"]["col1"]["is_problematic"]


def test_missing_values_is_not_problematic():
    """Tests that a low percentage of missing values is not flagged as problematic."""
    data = {"col1": [1, 2, 3, 4, 5, 6, 7, np.nan, np.nan, np.nan]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert not profile["missing_values"]["col1"]["is_problematic"]


def test_numerical_stats_all_nan():
    """Tests numerical stats on a column with all NaNs."""
    data = {"col1": [np.nan, np.nan]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert "col1" not in profile["numerical_stats"]


def test_no_duplicate_rows():
    """Tests that no duplicate row issue is raised when there are no duplicates."""
    data = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert not any(
        issue["type"] == "duplicate_rows" for issue in profile["data_quality_issues"]
    )


def test_no_constant_columns():
    """Tests that no constant column issue is raised when there are no constant columns."""
    data = {"col1": [1, 2, 3]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert not any(
        issue["type"] == "constant_column" for issue in profile["data_quality_issues"]
    )


def test_no_high_missing_data():
    """Tests that no high missing data issue is raised when there is no high missing data."""
    data = {"col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert not any(
        issue["type"] == "high_missing_data" for issue in profile["data_quality_issues"]
    )


def test_balance_consistency_no_mismatch():
    """Tests that no balance inconsistency issue is raised when there is no mismatch."""
    data = {
        "type": ["CASH_OUT"],
        "amount": [100.0],
        "oldbalanceOrg": [1000.0],
        "newbalanceOrig": [900.0],
    }
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert not any(
        issue["type"] == "balance_inconsistency"
        for issue in profile["data_quality_issues"]
    )


def test_class_distribution_no_fraud_col():
    """Tests class distribution when the fraud column is not present."""
    data = {"col1": [1, 2, 3]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert "error" in profile["class_distribution"]


def test_class_distribution_no_fraud_cases():
    """Tests class distribution with no fraud cases."""
    data = {"isFraud": [0, 0, 0]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert profile["class_distribution"]["fraud_cases"] == 0


def test_class_distribution_empty_df():
    """Tests class distribution with an empty DataFrame."""
    df = pd.DataFrame({"isFraud": []})
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert profile["class_distribution"]["fraud_percentage"] == 0
    assert profile["class_distribution"]["is_highly_imbalanced"] is False


def test_temporal_analysis_no_step_col():
    """Tests temporal analysis when the step column is not present."""
    data = {"col1": [1, 2, 3]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert "step_analysis" not in profile["temporal_analysis"]


def test_temporal_analysis_no_significant_hours():
    """Tests temporal analysis with no significant hours."""
    data = {"step": [1, 2, 3], "isFraud": [0, 1, 0]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert "fraud_temporal_pattern" not in profile["temporal_analysis"]


def test_get_summary_report_no_profile():
    """Tests that get_summary_report generates a profile if it doesn't exist."""
    df = pd.DataFrame({"col1": [1, 2, 3]})
    profiler = DataProfiler(df)
    report = profiler.get_summary_report()
    assert isinstance(report, str)
    assert len(report) > 0


def test_get_summary_report_no_step_analysis():
    """Tests the summary report when step_analysis is not present."""
    data = {"col1": [1, 2, 3]}
    df = pd.DataFrame(data)
    profiler = DataProfiler(df)
    profiler.generate_profile()
    report = profiler.get_summary_report()
    assert "Temporal Coverage" not in report
