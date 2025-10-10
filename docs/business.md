## 1. Executive Summary

This project details the creation of a machine learning model to power a real-time fraud detection API. The model classifies mobile financial transactions as fraudulent or legitimate, with a primary focus on optimizing for financial performance. The analysis culminates in a quantitative assessment of the model's business value, projecting both client savings and revenue for the service provider.

## 2. Business Context & Problem Statement

### 2.1. The Company: "Blocker Fraud Systems"

"Blocker Fraud Systems" is a B2B SaaS company providing a fraud detection API to e-commerce and fintech clients. Clients integrate the API into their payment pipeline for real-time transaction risk scoring. The service is designed to reduce clients' fraud-related losses while protecting their customer experience by minimizing the rejection of legitimate transactions.

### 2.2. The Business & Monetization Model

The service operates on a performance-based hybrid pricing model:

*   **Base API Fee:**  A fixed fee of $0.02 per transaction analyzed.
*   **Performance Incentive Fee:** A commission of 8% on the monetary value of each transaction correctly identified as fraudulent (True Positive).
*   **False Positive Penalty:** A penalty of 2% on the monetary value of each legitimate transaction incorrectly flagged as fraudulent (False Positive).

This balanced model directly ties revenue to the model's ability to accurately detect fraud while protecting client relationships. The commission structure incentivizes fraud detection, but the false positive penalty ensures we maintain high precision and don't disrupt legitimate business. This creates a sustainable partnership where Blocker Fraud Systems only succeeds when delivering real value - catching fraud without alienating good customers.

## 3. Project Goals & Objectives

The central goal is to develop a machine learning model that maximizes revenue for "Blocker Fraud Systems" under the defined business model.

The project's objectives are:

1.  **Develop a Predictive Model:** Build and train a classification model to generate a fraud risk score for every incoming transaction.
2.  **Optimize for Profitability:** Determine the optimal classification threshold that maximizes financial return by balancing fraud detection against the potential for blocking legitimate transactions.
3.  **Quantify Financial Impact:** Translate the model's technical performance on a test dataset into a clear financial forecast for both the client and the company.

## 4. Scope of Analysis

The model's success is evaluated through a comprehensive framework that addresses the following areas:

*   **Classification Performance:** Measurement of the model's **Precision, Recall, and F1-Score**, with an analysis of the Precision-Recall curve to visualize performance trade-offs.
*   **Financial Value for the Client:** Calculation of the total monetary value of fraud prevented (savings from True Positives) versus the value of sales lost from incorrectly blocked transactions (losses from False Positives).
*   **Revenue Projection for Blocker Fraud Systems:** A forecast of total earnings, detailing revenue from both the base API fees and the performance incentive fees.
*   **Net Profitability Analysis:** An overall assessment of the financial viability of the service based on the model's performance.
