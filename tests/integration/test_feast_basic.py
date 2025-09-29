"""
Basic tests for the Feast feature store.

These tests verify that the feature store is correctly configured and that features
can be retrieved for both training (historical) and online serving.
"""

from pathlib import Path

import pandas as pd
import pytest
from feast import FeatureStore


@pytest.fixture(scope="module")
def feature_store():
    """
    Pytest fixture to initialize the feature store from the feature_repo directory.
    """
    return FeatureStore(
        repo_path=str(Path(__file__).parent.parent.parent / "feature_repo")
    )


def test_feature_definition_loading(feature_store):
    """
    Verify that all feature views and services can be loaded from the repository.
    """
    # List all registered feature views and services
    feature_views = feature_store.list_feature_views()
    feature_services = feature_store.list_feature_services()

    # Assert that the lists are not empty, confirming they are loaded
    assert (
        len(feature_views) > 0
    ), "No feature views found. The repository may be misconfigured."
    assert (
        len(feature_services) > 0
    ), "No feature services found. The repository may be misconfigured."


def test_can_retrieve_historical_features(feature_store):
    """
    Verify we can get features from the offline store.
    """
    # Use a real entity and timestamp discovered from the debug test.
    # The data exists at 2024-01-01 01:00:00. We will request features for one hour after that.
    start_date = pd.Timestamp("2024-01-01", tz="UTC")
    entity_df = pd.DataFrame(
        {
            "event_timestamp": [start_date + pd.to_timedelta(2, unit="h")],
            "nameOrig": ["C1231006815"],
            "nameDest": ["M1979787155"],
        }
    )

    # Define the features to retrieve
    features_to_retrieve = [
        "transaction_features:amount",
        "transaction_features:oldbalanceOrg",
        "transaction_features:newbalanceOrig",
    ]

    # Retrieve features for the known entities
    retrieved_features = feature_store.get_historical_features(
        entity_df=entity_df, features=features_to_retrieve
    ).to_df()

    # Assert features are returned and not null
    assert not retrieved_features.empty
    assert "amount" in retrieved_features.columns
    assert "oldbalanceOrg" in retrieved_features.columns
    assert "newbalanceOrig" in retrieved_features.columns
    assert retrieved_features["amount"].isnull().sum() == 0


def test_can_retrieve_online_features(feature_store):
    """
    Verify we can get features from the online store.

    NOTE: This test will fail if the online store has not been populated
    using the 'feast materialize' or 'feast materialize-incremental' command.
    """
    # Use a real entity from the dataset
    entity_rows = [
        {"nameOrig": "C1231006815", "nameDest": "M1979787155"},
    ]

    # Define the features to retrieve
    features_to_retrieve = [
        "transaction_features:amount",
        "transaction_features:isFraud",
    ]

    # Get features for the specific entities
    online_features = feature_store.get_online_features(
        features=features_to_retrieve, entity_rows=entity_rows
    ).to_dict()

    # Assert features match expected values
    assert "amount" in online_features
    assert "isFraud" in online_features
    assert len(online_features["amount"]) == 1
    assert online_features["amount"][0] is not None
    assert online_features["isFraud"][0] is not None


def test_offline_online_consistency(feature_store):
    """
    Verify that feature values are consistent between the online and offline stores.
    """
    # Define a specific entity to test
    entity_row = {"nameOrig": "C1231006815", "nameDest": "M1979787155"}
    features_to_retrieve = [
        "transaction_features:amount",
        "transaction_features:isFraud",
    ]

    # 1. Get features from the online store
    online_features = feature_store.get_online_features(
        features=features_to_retrieve, entity_rows=[entity_row]
    ).to_dict()

    # 2. Get the latest features from the offline store
    # We need a timestamp to query the offline store.
    # We use a fixed timestamp that aligns with the materialized data.
    entity_df = pd.DataFrame(
        {
            "event_timestamp": [pd.Timestamp("2024-01-01T01:00:00", tz="UTC")],
            "nameOrig": [entity_row["nameOrig"]],
            "nameDest": [entity_row["nameDest"]],
        }
    )
    historical_features = feature_store.get_historical_features(
        entity_df=entity_df, features=features_to_retrieve
    ).to_df()

    # 3. Compare the results
    # Ensure both online and offline stores returned data
    assert len(online_features["amount"]) == 1, "Online store did not return a value."
    assert not historical_features.empty, "Offline store did not return a value."

    # Extract values for comparison
    online_amount = online_features["amount"][0]
    offline_amount = historical_features["amount"].iloc[0]

    online_is_fraud = online_features["isFraud"][0]
    offline_is_fraud = historical_features["isFraud"].iloc[0]

    # Assert consistency
    assert (
        online_amount == offline_amount
    ), f"Amount mismatch: Online={online_amount}, Offline={offline_amount}"
    assert (
        online_is_fraud == offline_is_fraud
    ), f"isFraud mismatch: Online={online_is_fraud}, Offline={offline_is_fraud}"
