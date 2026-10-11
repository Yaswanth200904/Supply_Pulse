"""
supplier_discovery.py — Agent 2: Supplier Discovery & Vetting Agent
Scans registered enterprise vendors, calculates multi-criteria utility scores,
and shortlists the best candidates for autonomous price and SLA negotiation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class SupplierDiscoveryAgent:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.suppliers_path = data_dir / "suppliers.json"

    def discover_and_rank(self, sku_id: str, required_qty: int, target_cost: float) -> List[Dict[str, Any]]:
        """
        Filters vendors supporting the SKU and scores them using multi-criteria utility:
        - Cost Efficiency (40%)
        - Reliability History (35%)
        - Delivery Lead Time (25%)
        """
        with open(self.suppliers_path, "r", encoding="utf-8") as f:
            suppliers = json.load(f)

        candidates = []

        for supp in suppliers:
            if sku_id not in supp["supported_skus"]:
                continue

            base_price = supp["base_prices"][sku_id]
            
            # Check bulk discount eligibility
            discount_pct = 0.0
            for rule in sorted(supp["bulk_discount_rules"], key=lambda r: r["min_qty"], reverse=True):
                if required_qty >= rule["min_qty"]:
                    discount_pct = rule["discount_pct"]
                    break

            effective_unit_price = round(base_price * (1 - (discount_pct / 100.0)), 2)
            
            # Multi-Criteria Scoring (Normalized 0 to 100)
            cost_score = max(0, min(100, 100 * (target_cost / effective_unit_price)))
            rel_score = supp["reliability_score"]
            speed_score = max(0, min(100, 100 * (3 / max(1, supp["std_lead_time_days"]))))

            composite_score = round(
                (0.40 * cost_score) + (0.35 * rel_score) + (0.25 * speed_score), 1
            )

            candidates.append({
                "supplier_id": supp["id"],
                "supplier_name": supp["name"],
                "base_price": base_price,
                "offered_unit_price": effective_unit_price,
                "initial_discount_pct": discount_pct,
                "std_lead_time_days": supp["std_lead_time_days"],
                "fast_track_lead_time_days": supp["fast_track_lead_time_days"],
                "fast_track_surcharge_pct": supp["fast_track_surcharge_pct"],
                "reliability_score": rel_score,
                "negotiation_flexibility": supp.get("negotiation_flexibility", 0.8),
                "composite_rank_score": composite_score
            })

        # Sort highest composite score first
        candidates.sort(key=lambda c: c["composite_rank_score"], reverse=True)
        return candidates
