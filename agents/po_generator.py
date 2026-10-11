"""
po_generator.py — Agent 5: Purchase Order & Settlement Auditor
Generates audit-ready, legally enforceable Purchase Orders (POs) for B2B procurement
and official Settlement Resolution Memorandums for consumer disputes.
"""

from datetime import datetime
import uuid
from typing import Dict, Any


class POGeneratorAgent:
    @staticmethod
    def generate_purchase_order(negotiation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a formal electronic Purchase Order record.
        """
        po_id = f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        qty = negotiation_data["quantity"]
        unit_price = negotiation_data["final_unit_price"]
        subtotal = round(qty * unit_price, 2)
        gst_tax = round(subtotal * 0.18, 2)  # 18% GST standard
        total_payable = round(subtotal + gst_tax, 2)

        return {
            "po_number": po_id,
            "created_at": order_date,
            "status": "APPROVED_AWAITING_DISPATCH",
            "vendor_name": negotiation_data["supplier_name"],
            "vendor_id": negotiation_data["supplier_id"],
            "sku_id": negotiation_data["sku_id"],
            "item_description": negotiation_data["sku_name"],
            "quantity_ordered": qty,
            "unit_price_inr": unit_price,
            "initial_catalog_price_inr": negotiation_data["initial_unit_price"],
            "negotiated_savings_inr": negotiation_data["total_savings_inr"],
            "subtotal_inr": subtotal,
            "tax_gst_18pct_inr": gst_tax,
            "total_landed_cost_inr": total_payable,
            "delivery_sla_deadline": f"{negotiation_data['agreed_delivery_sla_hours']} Hours Guaranteed Dock Delivery",
            "payment_terms": negotiation_data["payment_terms"],
            "legal_clauses": [
                "Strict SLA Adherence: Penalty of 1.5% per 6 hours delay past 48h deadline.",
                "Quality Warranty: Right of inspection on warehouse bay; 100% replacement for transit damage.",
                "Electronic Invoicing: Conforms to GST e-invoicing schema under Indian tax law."
            ]
        }
