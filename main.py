import requests
import time
import random

# --- Configuration ---
# CoinGecko IDs for assets
COLLATERAL_ASSETS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDC': 'usd-coin',
    'MATIC': 'matic-network' # Added Polygon (MATIC)
}

# Loan-to-Value Ratios
LTV_RATIOS = {
    'BTC': 0.60,  # 60%
    'ETH': 0.60,  # 60%
    'USDC': 0.90, # 90%
    'MATIC': 0.55 # 55% LTV for MATIC (Adjust as needed)
}

# LTV Thresholds for Actions
MARGIN_CALL_LTV = 0.75  # 75% - Warning issued
LIQUIDATION_LTV = 0.85 # 85% - Collateral starts getting sold to cover debt

# Liquidation Priority Order (Lower index = sold first)
LIQUIDATION_PRIORITY = ['USDC', 'ETH', 'MATIC', 'BTC'] # Added MATIC

# --- Helper Function: Get Crypto Prices ---
def get_crypto_prices(asset_ids):
    """Fetches current prices in USD from CoinGecko."""
    if not asset_ids:
        return {}
    ids_string = ','.join(asset_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = {symbol: data.get(cg_id, {}).get('usd', 0)
                  for symbol, cg_id in COLLATERAL_ASSETS.items() if cg_id in asset_ids}
        print(f"Fetched Prices: {prices}") # Debug print
        return prices
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prices: {e}")
        return {symbol: 0 for symbol, cg_id in COLLATERAL_ASSETS.items() if cg_id in asset_ids}

# --- OrbitX Boost Account Simulation Class ---
class BoostAccount:
    def __init__(self, user_id="User123"):
        self.user_id = user_id
        self.collateral = {} # Format: {'BTC': 0.5, 'ETH': 2.0, 'MATIC': 1000}
        self.utilized_credit_usd = 0.0
        self.total_collateral_value_usd = 0.0
        self.max_credit_line_usd = 0.0
        self.available_credit_usd = 0.0
        self.current_ltv = 0.0
        self.prices = {}

    def add_collateral(self, asset_symbol, amount):
        """Adds crypto asset to the collateral pool."""
        if asset_symbol in COLLATERAL_ASSETS:
            self.collateral[asset_symbol] = self.collateral.get(asset_symbol, 0) + amount
            print(f"Added {amount} {asset_symbol} as collateral.")
            self.update_status() # Recalculate credit line
        else:
            print(f"Error: {asset_symbol} is not supported as collateral.")

    def _update_calculations(self):
        """Internal function to fetch prices and recalculate all values."""
        collateral_cg_ids = [COLLATERAL_ASSETS[symbol] for symbol in self.collateral if symbol in COLLATERAL_ASSETS and self.collateral[symbol] > 0]
        if not collateral_cg_ids:
             # Reset if no collateral
             self.total_collateral_value_usd = 0.0
             self.max_credit_line_usd = 0.0
             self.available_credit_usd = 0.0
             self.current_ltv = 0.0
             self.prices = {}
             return

        self.prices = get_crypto_prices(collateral_cg_ids)
        time.sleep(0.5)

        self.total_collateral_value_usd = 0.0
        self.max_credit_line_usd = 0.0

        print("\n--- Calculating Collateral Value ---")
        # Iterate in a consistent order for display if needed
        sorted_symbols = sorted(self.collateral.keys())
        for symbol in sorted_symbols:
            if symbol in self.collateral and self.collateral[symbol] > 0:
                amount = self.collateral[symbol]
                price = self.prices.get(symbol, 0)
                value = amount * price
                ltv = LTV_RATIOS.get(symbol, 0)
                credit_contribution = value * ltv
                self.total_collateral_value_usd += value
                self.max_credit_line_usd += credit_contribution
                print(f"  {amount:.4f} {symbol} @ ${price:,.2f}/ea = ${value:,.2f} Value (LTV: {ltv*100:.0f}%, Credit: ${credit_contribution:,.2f})")

        print(f"Total Collateral Value: ${self.total_collateral_value_usd:,.2f}")
        print(f"Max Potential Credit Line: ${self.max_credit_line_usd:,.2f}")

        self.available_credit_usd = max(0, self.max_credit_line_usd - self.utilized_credit_usd)

        if self.total_collateral_value_usd > 0:
            self.current_ltv = self.utilized_credit_usd / self.total_collateral_value_usd
        else:
            self.current_ltv = 0.0

    def update_status(self):
        """Fetches latest prices and prints the current account status."""
        self._update_calculations()
        print("\n--- OrbitX Boost Status ---")
        print(f"Collateral Holdings: {self.collateral}")
        print(f"Total Collateral Value: ${self.total_collateral_value_usd:,.2f}")
        print(f"Utilized Credit: ${self.utilized_credit_usd:,.2f}")
        print(f"Available Credit: ${self.available_credit_usd:,.2f}")
        print(f"Current Loan-to-Value (LTV): {self.current_ltv:.2%}")
        self.check_health()
        print("---------------------------")

    def spend_on_card(self, amount_usd):
        """Simulates spending using the credit line."""
        print(f"\nAttempting to spend ${amount_usd:,.2f}...")
        if amount_usd <= self.available_credit_usd:
            self.utilized_credit_usd += amount_usd
            self.available_credit_usd -= amount_usd
            if self.total_collateral_value_usd > 0:
                self.current_ltv = self.utilized_credit_usd / self.total_collateral_value_usd
            else:
                 self.current_ltv = 0.0
            print(f"Success! Spent ${amount_usd:,.2f}. New Utilized Credit: ${self.utilized_credit_usd:,.2f}. New Available Credit: ${self.available_credit_usd:,.2f}. New LTV: {self.current_ltv:.2%}")
            self.check_health()
            return True
        else:
            print(f"Failed! Insufficient available credit. Tried to spend ${amount_usd:,.2f}, only ${self.available_credit_usd:,.2f} available.")
            return False

    def repay(self, amount_usd):
        """Simulates repaying the utilized credit."""
        print(f"\nAttempting to repay ${amount_usd:,.2f}...")
        repayment_amount = min(amount_usd, self.utilized_credit_usd)
        if repayment_amount > 0:
            self.utilized_credit_usd -= repayment_amount
            # Force recalculation after repayment
            self.update_status()
            print(f"Successfully repaid ${repayment_amount:,.2f}. New Utilized Credit: ${self.utilized_credit_usd:,.2f}")
        else:
            print("No credit utilized or invalid amount.")

    def check_health(self):
        """Checks LTV against thresholds and prints warnings."""
        if self.utilized_credit_usd <= 0: # Don't show warnings if no debt
             print(f"✅ Account health is good (No debt).")
             return

        if self.current_ltv >= LIQUIDATION_LTV:
            print(f"🚨 CRITICAL HEALTH! LTV ({self.current_ltv:.2%}) is >= Liquidation Threshold ({LIQUIDATION_LTV:.2%}). Liquidation process would start!")
        elif self.current_ltv >= MARGIN_CALL_LTV:
            print(f"⚠️ MARGIN CALL! LTV ({self.current_ltv:.2%}) is >= Margin Call Threshold ({MARGIN_CALL_LTV:.2%}). Add collateral or repay soon!")
        else:
            print(f"✅ Account health is good (LTV: {self.current_ltv:.2%}).")

    def initiate_liquidation(self):
        """Simulates the liquidation process."""
        print("\n--- SIMULATING LIQUIDATION ---")
        if self.utilized_credit_usd <= 0:
            print("No debt to liquidate.")
            return

        print(f"Need to cover debt of ${self.utilized_credit_usd:,.2f}")
        # Simulate selling slightly more for fees/slippage (e.g., 2% buffer)
        value_to_liquidate_target = self.utilized_credit_usd / (1 - 0.02)
        print(f"Targeting liquidation value of approx ${value_to_liquidate_target:,.2f}")

        liquidated_value_usd = 0
        temp_collateral = self.collateral.copy()

        # Use the defined priority list
        for symbol in LIQUIDATION_PRIORITY:
             if symbol in temp_collateral and temp_collateral[symbol] > 1e-9 and liquidated_value_usd < value_to_liquidate_target:
                 price = self.prices.get(symbol, 0)
                 if price > 0:
                    needed_value = value_to_liquidate_target - liquidated_value_usd
                    amount_available = temp_collateral[symbol]
                    value_available = amount_available * price

                    # Decide how much of this asset to sell
                    amount_to_sell = 0
                    sell_value = 0
                    if value_available >= needed_value:
                        # Sell just enough to cover remaining target
                        amount_to_sell = needed_value / price
                        sell_value = needed_value
                    else:
                        # Sell all available amount of this asset
                        amount_to_sell = amount_available
                        sell_value = value_available

                    print(f"  Liquidating {amount_to_sell:.4f} {symbol} for approx ${sell_value:,.2f}")
                    temp_collateral[symbol] -= amount_to_sell
                    if temp_collateral[symbol] < 1e-9: # Remove if near zero
                        del temp_collateral[symbol]
                    liquidated_value_usd += sell_value

        print(f"Total Liquidated Value (Simulated): ${liquidated_value_usd:,.2f}")
        self.collateral = temp_collateral # Update actual collateral
        self.utilized_credit_usd = max(0, self.utilized_credit_usd - liquidated_value_usd) # Reduce debt, don't go below zero
        print(f"Liquidation complete. Remaining Debt (if any): ${self.utilized_credit_usd:,.2f}")
        self.update_status()


# --- Pitch Demonstration ---
if __name__ == "__main__":
    print("--- OrbitX Boost Pitch Demo (with Polygon) ---")
    account = BoostAccount()

    # 1. User adds collateral (including MATIC)
    print("\nSTEP 1: User Adds Collateral")
    account.add_collateral('BTC', 0.05) # Reduced BTC a bit
    account.add_collateral('ETH', 1.0)  # Reduced ETH a bit
    account.add_collateral('MATIC', 1500) # Added MATIC
    account.add_collateral('USDC', 300) # Reduced USDC a bit
    # Initial status update happens within add_collateral calls

    # 2. User spends using the credit line
    print("\nSTEP 2: User Spends Using Credit")
    # Adjust spending based on potentially different credit limit
    account.spend_on_card(800.00)
    account.spend_on_card(400.00)

    # 3. Status check
    print("\nSTEP 3: Check Status After Spending")
    account.update_status()

    # 4. Simulate a Price Drop (Affecting all non-stablecoins)
    print("\nSTEP 4: Simulate Market Price Drop!")
    # Use fetched prices if available, otherwise set manually
    current_btc_price = account.prices.get('BTC', 60000)
    current_eth_price = account.prices.get('ETH', 3000)
    current_matic_price = account.prices.get('MATIC', 0.7)

    # Simulate a ~25% drop for volatile assets
    account.prices['BTC'] = current_btc_price * 0.75
    account.prices['ETH'] = current_eth_price * 0.70 # Make ETH drop slightly more
    account.prices['MATIC'] = current_matic_price * 0.65 # Make MATIC drop most
    print(f"  (Simulated New Prices: BTC=${account.prices['BTC']:,.2f}, ETH=${account.prices['ETH']:,.2f}, MATIC=${account.prices['MATIC']:,.2f})")

    # Recalculate everything with new prices
    account._update_calculations()
    account.update_status() # Print full status update with new prices

    # 5. User repays some credit
    print("\nSTEP 5: User Repays Some Credit")
    account.repay(200.00)

    # 6. Simulate Liquidation Scenario
    print("\nSTEP 6: Check and Potentially Initiate Liquidation")
    if account.current_ltv >= LIQUIDATION_LTV:
        account.initiate_liquidation()
    else:
        print("Liquidation threshold not reached in this simulation run.")

    print("\n--- End of Demo ---")