"""
negotiator.py — Agent 3: Autonomous Dynamic Negotiation Agent
Executes multi-turn game-theoretic procurement bargaining between the Buyer AI
and Supplier Bots to secure maximum bulk discounts, waived surcharges, and locked SLAs.
"""

from typing import Dict, Any, List


class ProcurementNegotiatorAgent:
    def __init__(self, aggressive_mode: bool = True):
        self.aggressive_mode = aggressive_mode

    def negotiate(
        self,
        sku_id: str,
        sku_name: str,
        quantity: int,
        target_unit_price: float,
        supplier: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs a 3-turn autonomous bargaining protocol:
        Turn 1: Initial Price Discovery & Quote
        Turn 2: Volume Leverage & Competitor Counter-Offer
        Turn 3: Final Agreement with Locked Delivery SLA
        """
        supplier_name = supplier["supplier_name"]
        initial_price = supplier["offered_unit_price"]
        flexibility = supplier["negotiation_flexibility"]

        transcript: List[Dict[str, str]] = []

        # Turn 1: Buyer Opening
        buyer_turn_1 = (
            f"SupplyPulse Procurement: We need an urgent allocation of {quantity} units of {sku_name} ({sku_id}). "
            f"Your catalog list price is Rs. {supplier['base_price']}, offering Rs. {initial_price} with standard volume discount. "
            f"Our target budget threshold is Rs. {target_unit_price}/unit with delivery within 48 hours."
        )
        vendor_turn_1 = (
            f"{supplier_name}: Acknowledged. We can fulfill the {quantity} units. "
            f"However, guaranteed 48-hour delivery requires our express logistics lane, which typically carries a "
            f"{supplier['fast_track_surcharge_pct']}% expedited surcharge. Best standard offer is Rs. {initial_price}/unit."
        )
        transcript.append({"speaker": "Buyer AI", "message": buyer_turn_1})
        transcript.append({"speaker": f"{supplier_name} Bot", "message": vendor_turn_1})

        # Turn 2: Buyer Tactical Counter
        # The AI offers Net-15 prompt payment + mentions rival supplier leverage
        target_discount_price = round(min(initial_price, target_unit_price) * 0.92, 2)
        buyer_turn_2 = (
            f"Buyer AI: That surcharge exceeds our landed cost ceiling. If we commit to immediate Net-15 electronic settlement "
            f"and guarantee preferred vendor priority for the upcoming quarter, can you waive the express surcharge and "
            f"meet us at Rs. {target_discount_price}/unit for all {quantity} units?"
        )
        # Vendor calculates concession based on flexibility factor
        vendor_concession_price = round(
            initial_price - ((initial_price - target_discount_price) * flexibility), 2
        )
        vendor_concession_price = min(initial_price, vendor_concession_price)

        vendor_turn_2 = (
            f"{supplier_name} Bot: In consideration of Net-15 payment terms and quarterly volume commitment, our executive desk "
            f"authorizes waiving the express courier fee completely, and we can adjust the unit price down to Rs. {vendor_concession_price}."
        )
        transcript.append({"speaker": "Buyer AI", "message": buyer_turn_2})
        transcript.append({"speaker": f"{supplier_name} Bot", "message": vendor_turn_2})

        # Turn 3: Final Close & SLA Lock
        final_unit_price = vendor_concession_price
        total_initial_cost = initial_price * quantity
        total_negotiated_cost = final_unit_price * quantity
        total_savings = round(total_initial_cost - total_negotiated_cost, 2)
        savings_pct = round((total_savings / total_initial_cost) * 100, 1)

        buyer_turn_3 = (
            f"Buyer AI: Deal accepted at Rs. {final_unit_price}/unit with guaranteed 48-hour warehouse dock delivery. "
            f"Total order value: Rs. {total_negotiated_cost:,.2f}. Generating formal Purchase Order with liquidated damages clause for transit delay."
        )
        transcript.append({"speaker": "Buyer AI", "message": buyer_turn_3})

        return {
            "status": "NEGOTIATION_SUCCESSFUL",
            "sku_id": sku_id,
            "sku_name": sku_name,
            "quantity": quantity,
            "supplier_id": supplier["supplier_id"],
            "supplier_name": supplier_name,
            "initial_unit_price": initial_price,
            "final_unit_price": final_unit_price,
            "total_initial_cost": total_initial_cost,
            "total_negotiated_cost": total_negotiated_cost,
            "total_savings_inr": total_savings,
            "savings_percentage": savings_pct,
            "agreed_delivery_sla_hours": 48,
            "payment_terms": "Net-15 Electronic Transfer",
            "transcript": transcript
        }
