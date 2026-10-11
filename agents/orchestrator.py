"""
orchestrator.py — SupplyPulse Multi-Agent Swarm Orchestrator
Coordinates the end-to-end autonomous lifecycle across both B2B Supply Chain
and Customer Advocacy pipelines.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from supplypulse.agents.inventory_sentinel import InventorySentinelAgent
from supplypulse.agents.supplier_discovery import SupplierDiscoveryAgent
from supplypulse.agents.negotiator import ProcurementNegotiatorAgent
from supplypulse.agents.po_generator import POGeneratorAgent
from supplypulse.agents.consumer_advocate import CustomerAdvocateAgent


class SupplyPulseOrchestrator:
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            self.project_root = Path(__file__).resolve().parent.parent
        else:
            self.project_root = project_root

        self.data_dir = self.project_root / "data"

        # Initialize sub-agents
        self.sentinel = InventorySentinelAgent(self.data_dir)
        self.discovery = SupplierDiscoveryAgent(self.data_dir)
        self.negotiator = ProcurementNegotiatorAgent()
        self.consumer_advocate = CustomerAdvocateAgent()

    def run_b2b_procurement_cycle(self, target_sku_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes autonomous B2B replenishment lifecycle:
        1. Scan inventory & forecast demand (InventorySentinel)
        2. Filter SKUs requiring reorder
        3. Discover & rank suppliers (SupplierDiscovery)
        4. Execute multi-turn price negotiation (ProcurementNegotiator)
        5. Generate audited Purchase Order (POGenerator)
        """
        # Step 1: Scan
        scan_results = self.sentinel.scan_warehouse()
        critical_alerts = scan_results["critical_alerts"]

        if not critical_alerts and not target_sku_id:
            return {
                "status": "INVENTORY_HEALTHY_NO_ACTION_REQUIRED",
                "scan_summary": scan_results
            }

        # Select target SKU
        selected_alert = None
        if target_sku_id:
            for alert in critical_alerts:
                if alert["sku_id"] == target_sku_id:
                    selected_alert = alert
                    break
            # If not in critical alerts, look up directly from scan reports
            if not selected_alert:
                for rep in scan_results["sku_reports"]:
                    if rep["sku_id"] == target_sku_id:
                        selected_alert = {
                            "sku_id": rep["sku_id"],
                            "sku_name": rep["sku_name"],
                            "current_stock": rep["current_stock"],
                            "stockout_in_days": rep["stockout_in_days"],
                            "recommended_order_quantity": rep["recommended_order_quantity"] or 300,
                            "target_cost": 500.0,
                            "lead_time_days": 3
                        }
                        break
        else:
            selected_alert = critical_alerts[0]

        sku_id = selected_alert["sku_id"]
        sku_name = selected_alert["sku_name"]
        order_qty = selected_alert["recommended_order_quantity"]
        target_cost = selected_alert["target_cost"]

        # Step 2: Discover and Rank Suppliers
        ranked_suppliers = self.discovery.discover_and_rank(sku_id, order_qty, target_cost)
        if not ranked_suppliers:
            return {
                "status": "NO_SUPPLIERS_FOUND",
                "sku_id": sku_id,
                "scan_summary": scan_results
            }

        top_supplier = ranked_suppliers[0]

        # Step 3: Run Multi-Turn Dynamic Negotiation
        negotiation_result = self.negotiator.negotiate(
            sku_id=sku_id,
            sku_name=sku_name,
            quantity=order_qty,
            target_unit_price=target_cost,
            supplier=top_supplier
        )

        # Step 4: Generate Audited Purchase Order
        po_record = POGeneratorAgent.generate_purchase_order(negotiation_result)

        return {
            "status": "B2B_REPLENISHMENT_COMPLETED",
            "stockout_risk_identified": selected_alert,
            "shortlisted_suppliers": ranked_suppliers,
            "selected_supplier": top_supplier,
            "negotiation_outcome": negotiation_result,
            "final_purchase_order": po_record,
            "all_inventory_reports": scan_results["sku_reports"]
        }

    def run_consumer_dispute_resolution(
        self,
        customer_name: str,
        order_id: str,
        product_name: str,
        purchase_price: float,
        purchase_date: str,
        incident_description: str
    ) -> Dict[str, Any]:
        """
        Executes autonomous customer grievance resolution:
        1. Forensically inspects defect evidence & invoice
        2. Deploys Customer Advocate Bot against corporate support chatbot
        3. Invokes statutory legal frameworks
        4. Secures 100% refund, replacement, or RMA settlement
        """
        return self.consumer_advocate.advocate_and_resolve(
            customer_name=customer_name,
            order_id=order_id,
            product_name=product_name,
            purchase_price=purchase_price,
            purchase_date=purchase_date,
            incident_description=incident_description
        )
