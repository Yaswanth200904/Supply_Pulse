"""
inventory_sentinel.py — Agent 1: Autonomous Inventory Sentinel
Continuously evaluates live warehouse telemetry against ML predictive demand curves,
identifying critical shortages and spawning procurement alerts before stock runs dry.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from supplypulse.models.forecaster import DemandForecaster


class InventorySentinelAgent:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.forecaster = DemandForecaster()
        self.inventory_path = data_dir / "inventory.json"

    def scan_warehouse(self) -> Dict[str, Any]:
        """
        Scans all SKUs in the warehouse inventory.
        For each SKU, trains the ML forecaster on 90-day simulated history,
        computes the 14-day demand forecast, and detects stockout risks.
        """
        with open(self.inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        reports = []
        critical_alerts = []

        for sku_id, meta in inventory.items():
            # 1. Synthesize historical demand & train forecast model
            history_df = self.forecaster.generate_synthetic_history(base_daily=meta["daily_avg_sales"])
            forecast_result = self.forecaster.train_and_forecast(history_df, horizon_days=14)
            
            # 2. Evaluate risk & Reorder Point (ROP)
            risk = self.forecaster.evaluate_stockout_risk(sku_id, meta, forecast_result)
            risk["forecast_14d"] = forecast_result
            
            reports.append(risk)

            if risk["is_critical_reorder_needed"]:
                critical_alerts.append({
                    "sku_id": sku_id,
                    "sku_name": meta["name"],
                    "current_stock": meta["current_stock"],
                    "stockout_in_days": risk["stockout_in_days"],
                    "recommended_order_quantity": risk["recommended_order_quantity"],
                    "target_cost": meta["target_cost"],
                    "lead_time_days": meta["lead_time_days"]
                })

        return {
            "timestamp": "2026-10-10T20:00:00Z",
            "total_skus_scanned": len(inventory),
            "critical_stockout_alerts_count": len(critical_alerts),
            "critical_alerts": critical_alerts,
            "sku_reports": reports
        }
