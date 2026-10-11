"""
forecaster.py — SupplyPulse Machine Learning Demand Forecasting Engine
Combines time-series regression with dynamic Reorder Point (ROP) mathematics
to anticipate warehouse stockouts 7 to 14 days before they occur.
"""

from datetime import datetime, timedelta
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor


class DemandForecaster:
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def generate_synthetic_history(self, base_daily: float, days: int = 90) -> pd.DataFrame:
        """
        Synthesizes realistic daily sales history containing:
        - Day-of-week seasonality (Friday/Saturday/Sunday surges)
        - Monthly trend
        - Random demand noise
        - Occasional promo surge spikes (festivals/flash sales)
        """
        start_date = datetime.now() - timedelta(days=days)
        records = []

        for i in range(days):
            date = start_date + timedelta(days=i)
            dow = date.weekday()  # 0=Mon, 6=Sun
            
            # Weekend surge multiplier
            weekend_boost = 1.35 if dow in [4, 5, 6] else 1.0
            
            # Mid-month payday boost (around 1st-5th and 28th-30th)
            day_of_month = date.day
            payday_boost = 1.2 if (day_of_month in [1, 2, 3, 28, 29, 30]) else 1.0

            # Random market noise (normal distribution)
            noise = np.random.normal(1.0, 0.12)
            
            # Occasional flash sale spike (5% chance)
            spike = 1.65 if (np.random.rand() < 0.05) else 1.0

            sales = max(2, int(base_daily * weekend_boost * payday_boost * noise * spike))

            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": dow,
                "is_weekend": 1 if dow in [4, 5, 6] else 0,
                "day_of_month": day_of_month,
                "days_since_start": i,
                "sales": sales
            })

        df = pd.DataFrame(records)
        # Lag features
        df["lag_1"] = df["sales"].shift(1).bfill()
        df["lag_7"] = df["sales"].shift(7).bfill()
        df["rolling_mean_7"] = df["sales"].rolling(7, min_periods=1).mean()
        return df

    def train_and_forecast(self, history_df: pd.DataFrame, horizon_days: int = 14) -> dict:
        """
        Trains a gradient boosted regressor on historical sales and projects daily demand.
        """
        feature_cols = ["day_of_week", "is_weekend", "day_of_month", "days_since_start", "lag_1", "lag_7", "rolling_mean_7"]
        X = history_df[feature_cols]
        y = history_df["sales"]

        model = HistGradientBoostingRegressor(max_iter=100, random_state=self.random_seed)
        model.fit(X, y)

        last_day_idx = history_df["days_since_start"].max()
        last_sales = list(history_df["sales"].values[-7:])
        
        forecast_dates = []
        forecast_values = []
        start_date = datetime.now()

        for step in range(1, horizon_days + 1):
            future_date = start_date + timedelta(days=step)
            dow = future_date.weekday()
            is_wknd = 1 if dow in [4, 5, 6] else 0
            dom = future_date.day

            lag_1 = last_sales[-1]
            lag_7 = last_sales[-7] if len(last_sales) >= 7 else last_sales[0]
            rolling_7 = float(np.mean(last_sales[-7:]))

            row_features = pd.DataFrame([{
                "day_of_week": dow,
                "is_weekend": is_wknd,
                "day_of_month": dom,
                "days_since_start": last_day_idx + step,
                "lag_1": lag_1,
                "lag_7": lag_7,
                "rolling_mean_7": rolling_7
            }])

            predicted_sales = max(1, int(round(model.predict(row_features)[0])))
            last_sales.append(predicted_sales)
            
            forecast_dates.append(future_date.strftime("%Y-%m-%d"))
            forecast_values.append(predicted_sales)

        return {
            "dates": forecast_dates,
            "projected_daily_demand": forecast_values,
            "total_predicted_demand_14d": sum(forecast_values),
            "average_daily_projected": round(float(np.mean(forecast_values)), 1)
        }

    def evaluate_stockout_risk(self, sku_id: str, sku_meta: dict, forecast_data: dict) -> dict:
        """
        Calculates:
        - Reorder Point (ROP) = (Avg Daily Demand * Lead Time) + Safety Stock
        - Days of Inventory Remaining (DOIR)
        - Stockout Alert Boolean
        - Recommended Reorder Quantity
        """
        current_stock = sku_meta["current_stock"]
        lead_time = sku_meta["lead_time_days"]
        safety_stock = sku_meta["min_safety_stock"]
        avg_demand = forecast_data["average_daily_projected"]

        # Dynamic Reorder Point
        rop = int(math.ceil((avg_demand * lead_time) + safety_stock))
        
        # Cumulative runout calculation
        daily_forecasts = forecast_data["projected_daily_demand"]
        remaining = current_stock
        stockout_day = None

        for idx, demand in enumerate(daily_forecasts, 1):
            remaining -= demand
            if remaining <= 0 and stockout_day is None:
                stockout_day = idx

        days_of_inventory = max(0, round(current_stock / (avg_demand or 1), 1))
        is_reorder_needed = (current_stock <= rop) or (stockout_day is not None and stockout_day <= 7)

        # Economic reorder size (covers lead time + 14-day demand buffer - current stock)
        recommended_reorder_qty = max(0, int(math.ceil(forecast_data["total_predicted_demand_14d"] + safety_stock - current_stock)))
        # Round up to nearest batch of 50
        recommended_reorder_qty = max(100, int(math.ceil(recommended_reorder_qty / 50.0) * 50))

        return {
            "sku_id": sku_id,
            "sku_name": sku_meta["name"],
            "current_stock": current_stock,
            "reorder_point_rop": rop,
            "days_of_inventory": days_of_inventory,
            "stockout_in_days": stockout_day if stockout_day else ">14",
            "is_critical_reorder_needed": is_reorder_needed,
            "recommended_order_quantity": recommended_reorder_qty if is_reorder_needed else 0
        }
