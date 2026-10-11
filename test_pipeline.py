"""
test_pipeline.py — Comprehensive End-to-End Pipeline Verification
Runs and asserts both the B2B Supply Chain Swarm and Customer AI Advocate Bot.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from supplypulse.agents.orchestrator import SupplyPulseOrchestrator


def test_b2b_supply_chain_pipeline():
    print("=" * 70)
    print("TEST 1: B2B AUTONOMOUS INVENTORY & PROCUREMENT SWARM")
    print("=" * 70)

    orchestrator = SupplyPulseOrchestrator()
    result = orchestrator.run_b2b_procurement_cycle(target_sku_id="SKU-101")

    assert result["status"] == "B2B_REPLENISHMENT_COMPLETED", f"Expected B2B success, got {result['status']}"
    assert "final_purchase_order" in result, "Missing final purchase order"
    
    po = result["final_purchase_order"]
    neg = result["negotiation_outcome"]

    print(f"\n[+] Stockout Risk Detected for: {result['stockout_risk_identified']['sku_name']}")
    print(f"    Current Stock: {result['stockout_risk_identified']['current_stock']} units")
    print(f"    Predicted Stockout: In {result['stockout_risk_identified']['stockout_in_days']} days!")
    print(f"    Recommended Reorder Qty: {result['stockout_risk_identified']['recommended_order_quantity']} units")

    print(f"\n[+] Selected Supplier: {result['selected_supplier']['supplier_name']} (Composite Score: {result['selected_supplier']['composite_rank_score']}/100)")
    print(f"[+] Initial Quote: Rs. {neg['initial_unit_price']} / unit")
    print(f"[+] Negotiated Price: Rs. {neg['final_unit_price']} / unit")
    print(f"[+] Total Savings Secured: Rs. {neg['total_savings_inr']:,.2f} ({neg['savings_percentage']}%)")
    print(f"[+] Agreed Delivery SLA: {neg['agreed_delivery_sla_hours']} Hours Guaranteed Dock Delivery")

    print(f"\n[+] Generated PO Number: {po['po_number']}")
    print(f"    Total Landed Cost (incl. 18% GST): Rs. {po['total_landed_cost_inr']:,.2f}")
    print("\n--- Negotiation Transcript Snippet ---")
    for msg in neg["transcript"]:
        print(f"[{msg['speaker']}]: {msg['message']}")
    print("\n[OK] B2B Pipeline Passed!\n")


def test_consumer_advocate_pipeline():
    print("=" * 70)
    print("TEST 2: CUSTOMER AI ADVOCATE BOT (WARRANTY & DAMAGE NEGOTIATION)")
    print("=" * 70)

    orchestrator = SupplyPulseOrchestrator()
    dispute_result = orchestrator.run_consumer_dispute_resolution(
        customer_name="Rohan Verma",
        order_id="OD-2026-99381",
        product_name="Ultrawide Gaming Monitor 34-inch",
        purchase_price=28999.0,
        purchase_date="2026-09-15",
        incident_description="Screen has green vertical artifacts and panel flickers on startup. Defective out of the box."
    )

    assert dispute_result["status"] == "DISPUTE_WON_FULL_SETTLEMENT"
    assert dispute_result["recovered_amount_inr"] == 28999.0

    print(f"\n[+] Customer: {dispute_result['customer_name']} (Order #{dispute_result['order_id']})")
    print(f"[+] Product: {dispute_result['product_name']} (Value: Rs. {dispute_result['recovered_amount_inr']:,.2f})")
    print(f"[+] Statutory Ground: {dispute_result['statute_cited']}")
    print(f"[+] Final Resolution: {dispute_result['settlement_type']}")
    print(f"[+] Recovered Value: Rs. {dispute_result['recovered_amount_inr']:,.2f} (100% Full Refund)")

    print("\n--- Support Dispute Chat Transcript ---")
    for msg in dispute_result["transcript"]:
        print(f"\n[{msg['speaker']}]:\n  \"{msg['message']}\"")
    print("\n[OK] Customer Advocate Pipeline Passed!\n")


if __name__ == "__main__":
    test_b2b_supply_chain_pipeline()
    test_consumer_advocate_pipeline()
    print("=" * 70)
    print("ALL SUPPLYPULSE PIPELINES VERIFIED SUCCESSFULLY!")
    print("=" * 70)
