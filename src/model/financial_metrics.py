"""This module provides a class to perform financial analysis on model predictions."""

import numpy as np
from sklearn.metrics import confusion_matrix


class FinancialAnalyzer:
    """A class to analyze the financial performance of a classification model."""

    def __init__(
        self,
        base_api_fee: float = 0.02,
        commission: float = 0.08,
        penalty: float = 0.02,
    ):
        """
        Initialize the FinancialAnalyzer.

        Args:
            base_api_fee (float): The base fee per transaction.
            commission (float): The commission on true positives.
            penalty (float): The penalty on false positives.
        """
        self.base_api_fee = base_api_fee
        self.commission = commission
        self.penalty = penalty

    def calculate_profit(
        self, y_true: np.ndarray, y_pred: np.ndarray, amounts: np.ndarray
    ) -> float:
        """
        Calculate the total profit based on the business model.

        Args:
            y_true (np.ndarray): The true labels.
            y_pred (np.ndarray): The predicted labels.
            amounts (np.ndarray): The transaction amounts.

        Returns:
            float: The total profit.
        """
        conf_matrix = confusion_matrix(y_true, y_pred)
        if conf_matrix.shape == (1, 1):
            if y_true[0] == 0:  # Only negatives
                tn, fp, fn, tp = conf_matrix[0, 0], 0, 0, 0
            else:  # Only positives
                tn, fp, fn, tp = 0, 0, 0, conf_matrix[0, 0]
        else:
            tn, fp, fn, tp = conf_matrix.ravel()

        total_transactions = len(y_true)

        fp_amounts = amounts[(y_true == 0) & (y_pred == 1)].sum()
        tp_amounts = amounts[(y_true == 1) & (y_pred == 1)].sum()

        profit = (
            (total_transactions * self.base_api_fee)
            + (tp_amounts * self.commission)
            - (fp_amounts * self.penalty)
        )

        return float(profit)

    def find_optimal_threshold(
        self, y_true: np.ndarray, y_pred_proba: np.ndarray, amounts: np.ndarray
    ) -> tuple[float, float]:
        """
        Find the classification threshold that maximizes profit.

        Args:
            y_true (np.ndarray): The true labels.
            y_pred_proba (np.ndarray): The predicted probabilities for the positive class.
            amounts (np.ndarray): The transaction amounts.

        Returns:
            tuple[float, float]: A tuple containing the optimal threshold and the maximum profit.
        """
        thresholds = np.linspace(0, 1, 101)
        profits = []

        for threshold in thresholds:
            y_pred = (y_pred_proba >= threshold).astype(int)
            profit = self.calculate_profit(y_true, y_pred, amounts)
            profits.append(profit)

        best_profit_index = np.argmax(profits)
        optimal_threshold = thresholds[best_profit_index]
        max_profit = profits[best_profit_index]

        return optimal_threshold, max_profit
