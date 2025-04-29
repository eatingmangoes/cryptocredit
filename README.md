# OrbitX Boost: Crypto-Backed Credit Line Simulation

**Project for OrbitX Hackathon @ [Your University Name]**

## Overview

This project simulates **OrbitX Boost**, a conceptual feature providing users with a dynamic, crypto-backed revolving credit line directly spendable through their OrbitX payment card.

The core idea is to allow users to unlock liquidity from their cryptocurrency holdings (like BTC, ETH, MATIC, and stablecoins including **USDT on Polygon**) without needing to sell them, addressing a key need in the Web3 space.

This simulation demonstrates the core mechanics:
*   Adding various crypto assets as collateral.
*   Calculating a dynamic credit limit based on real-time asset prices and pre-defined Loan-to-Value (LTV) ratios.
*   Simulating spending against the available credit line.
*   Repaying the utilized credit.
*   Monitoring the account's health (LTV) against margin call and liquidation thresholds.
*   Simulating an automated liquidation process if the LTV becomes critical.

**Disclaimer:** This is a conceptual simulation built for a hackathon pitch. It is **not** production-ready, does not interact with real wallets or smart contracts, and lacks robust error handling, security features, and precise financial calculations (like interest).

## Features Demonstrated

*   **Multi-Asset Collateral:** Supports BTC, ETH, MATIC, USDC, and **USDT on Polygon** as collateral (easily extensible).
*   **Dynamic Credit Line:** Calculates the maximum borrowable amount based on collateral value and individual asset LTVs.
*   **Real-Time Price Fetching:** Uses the CoinGecko API to get current market prices for collateral valuation.
*   **Simulated Spending:** Allows simulating card spending that draws down available credit.
*   **Repayment:** Allows simulating repayment of the utilized credit line.
*   **LTV Monitoring:** Continuously calculates the Loan-to-Value ratio (Utilized Credit / Total Collateral Value).
*   **Risk Management:** Simulates margin call warnings and automated liquidation based on pre-set LTV thresholds.
*   **Configurable Parameters:** LTV ratios, supported assets, and liquidation priority can be easily adjusted in the code's configuration section.

## How It Works (Algorithm Summary)

1.  **Configuration:** Define supported assets, LTV ratios, and risk thresholds.
2.  **Collateral Management:** User adds supported crypto assets to their simulated collateral pool.
3.  **Status Update (Core Loop):**
    *   Fetch current market prices for held collateral assets via CoinGecko API.
    *   Calculate the total USD value of all collateral.
    *   Calculate the maximum potential credit line based on each asset's value and its specific LTV ratio.
    *   Calculate the currently available credit (Max Credit Line - Utilized Credit).
    *   Calculate the current LTV ratio.
4.  **Spending:** If a spend amount is less than or equal to the available credit, increase utilized credit and recalculate status.
5.  **Repayment:** Decrease utilized credit by the repayment amount and recalculate status.
6.  **Health Check:** Compare the current LTV against margin call and liquidation thresholds, triggering alerts or liquidation.
7.  **Liquidation:** If LTV crosses the threshold, automatically simulate selling collateral (based on priority) to cover the debt.

## Supported Assets & Configuration (Default)

Defined near the top of the `boost_simulation.py` script:

*   **`COLLATERAL_ASSETS`**: Dictionary mapping symbols (e.g., 'BTC', 'ETH', 'MATIC', 'USDC', 'USDT_poly') to their CoinGecko API IDs.
*   **`LTV_RATIOS`**: Dictionary mapping symbols to their Loan-to-Value percentage (e.g., 'BTC': 0.60, 'MATIC': 0.55, 'USDT_poly': 0.90).
*   **`MARGIN_CALL_LTV`**: LTV threshold for warnings (e.g., 0.75).
*   **`LIQUIDATION_LTV`**: LTV threshold for simulated liquidation (e.g., 0.85).
*   **`LIQUIDATION_PRIORITY`**: List defining the order assets are sold during liquidation (e.g., `['USDT_poly', 'USDC', 'ETH', 'MATIC', 'BTC']`).

## Prerequisites

*   Python 3.6+
*   `requests` library (for CoinGecko API)

## Installation

1.  Clone the repository:
    ```bash
    git clone [your-repo-url]
    cd [your-repo-directory]
    ```
2.  Install the required library:
    ```bash
    pip install requests
    ```

## How to Run

Execute the simulation script from your terminal:

```bash
python boost_simulation.py
