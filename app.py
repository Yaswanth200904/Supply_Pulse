"""
app.py — SupplyPulse Interactive Command Center (Streamlit)
Two-in-One Autonomous Platform:
Tab 1: B2B Warehouse Autopilot & Multi-Agent Negotiation Swarm
Tab 2: Customer AI Advocate (Warranty, Defect & Support Care Negotiator)
"""

import sys
from pathlib import Path
import json

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from supplypulse.agents.orchestrator import SupplyPulseOrchestrator

st.set_page_config(
    page_title="SupplyPulse — Autonomous Supply Chain & Consumer Advocate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark-mode modern dashboard
st.markdown("""
<style>
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        color: white;
    }
    .badge-critical {
        background: #ef4444;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }
    .badge-healthy {
        background: #10b981;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }
    .chat-bubble-ai {
        background: #0f172a;
        border-left: 4px solid #0284c7;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #e2e8f0;
    }
    .chat-bubble-vendor {
        background: #1e1b4b;
        border-left: 4px solid #8b5cf6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #e2e8f0;
    }
    .chat-bubble-corporate {
        background: #451a03;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #fef3c7;
    }
    .chat-bubble-resolved {
        background: #064e3b;
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #d1fae5;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_orchestrator():
    return SupplyPulseOrchestrator()

orchestrator = get_orchestrator()

# Header
st.title("⚡ SupplyPulse: Autonomous AI Operations Platform")
st.caption("Machine Learning Demand Forecaster • Multi-Agent Procurement Swarm • Consumer Rights Defense Bot")

tabs = st.tabs([
    "🏢 B2B Warehouse & Procurement Swarm",
    "🛡️ Customer AI Advocate (Warranty & Damage Defenses)"
])

# ==========================================
# TAB 1: B2B WAREHOUSE & PROCUREMENT SWARM
# ==========================================
with tabs[0]:
    st.subheader("Autonomous Warehouse Telemetry & Predictive Restocking")
    
    # Run scan
    with st.spinner("Analyzing live telemetry & training ML forecast models..."):
        scan_results = orchestrator.sentinel.scan_warehouse()

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    total_skus = scan_results["total_skus_scanned"]
    critical_alerts = scan_results["critical_stockout_alerts_count"]
    
    m1.metric("Active Catalog SKUs", total_skus)
    m2.metric("Stockout Risk Alerts", critical_alerts, delta="-Critical" if critical_alerts > 0 else "Optimal", delta_color="inverse")
    m3.metric("ML Forecast Horizon", "14 Days", "Daily Precision")
    m4.metric("Agent Negotiation Status", "Online & Ready")

    st.markdown("---")

    # Inventory Table
    st.write("### 📦 Real-Time Warehouse Stock & Reorder Points (ROP)")
    table_data = []
    for rep in scan_results["sku_reports"]:
        status = "⚠️ CRITICAL RESTOCK" if rep["is_critical_reorder_needed"] else "✅ HEALTHY"
        table_data.append({
            "SKU ID": rep["sku_id"],
            "Product Name": rep["sku_name"],
            "Current Stock": rep["current_stock"],
            "Reorder Point (ROP)": rep["reorder_point_rop"],
            "Runout In (Days)": rep["stockout_in_days"],
            "Recommended Order": rep["recommended_order_quantity"],
            "Status": status
        })
    df_inventory = pd.DataFrame(table_data)
    st.dataframe(df_inventory, use_container_width=True)

    st.markdown("---")

    # Autonomous Action Trigger
    st.write("### 🤖 Launch Multi-Agent Procurement & Dynamic Negotiation")
    col_sel, col_btn = st.columns([2, 1])
    
    sku_options = [r["sku_id"] for r in scan_results["sku_reports"]]
    selected_sku = col_sel.selectbox("Select SKU to Restock Autonomously:", sku_options, index=0)
    
    if col_btn.button("🚀 Run Autonomous Swarm", type="primary", use_container_width=True):
        with st.spinner("Agents scanning suppliers, executing multi-turn price negotiations, and generating PO..."):
            procurement_result = orchestrator.run_b2b_procurement_cycle(target_sku_id=selected_sku)

        st.success(f"Procurement Cycle Complete for {procurement_result['stockout_risk_identified']['sku_name']}!")
        
        # Details & Negotiation
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.write("#### 💬 Live Multi-Turn Negotiation Arena")
            neg = procurement_result["negotiation_outcome"]
            for chat in neg["transcript"]:
                speaker = chat["speaker"]
                msg = chat["message"]
                if "Buyer" in speaker:
                    st.markdown(f"<div class='chat-bubble-ai'><strong>🤖 {speaker}</strong><br>{msg}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble-vendor'><strong>🏢 {speaker}</strong><br>{msg}</div>", unsafe_allow_html=True)

        with c_right:
            st.write("#### 📄 Audited Electronic Purchase Order (PO)")
            po = procurement_result["final_purchase_order"]
            st.json(po)
            st.metric("Total Hard-Dollar Savings Secured", f"Rs. {neg['total_savings_inr']:,.2f}", f"{neg['savings_percentage']}% Off")
            st.metric("Locked Delivery SLA", po["delivery_sla_deadline"])


# ==========================================
# TAB 2: CUSTOMER AI ADVOCATE (CONSUMER RIGHTS)
# ==========================================
with tabs[1]:
    st.subheader("Customer AI Advocate: Autonomous Warranty, Damage & Rights Defense")
    st.caption("Stonewalled by customer care? Let the AI Advocate invoke the Consumer Protection Act and fight on your behalf.")

    col_form, col_chat = st.columns([1, 1])

    with col_form:
        st.write("### 📝 Enter Product Issue / Grievance")
        
        # Presets
        preset = st.radio("Load Sample Dispute:", ["None", "Dead Ultrawide Monitor (Latent Defect)", "Broken Air Fryer Basket (Transit Damage)"], horizontal=True)
        
        if preset == "Dead Ultrawide Monitor (Latent Defect)":
            c_name = "Rohan Verma"
            c_order = "OD-2026-99381"
            c_prod = "Ultrawide Gaming Monitor 34-inch"
            c_price = 28999.0
            c_date = "2026-09-15"
            c_desc = "Display panel has green vertical lines and flickers continuously on startup. Defective out of the box."
        elif preset == "Broken Air Fryer Basket (Transit Damage)":
            c_name = "Pooja Sharma"
            c_order = "OD-2026-88124"
            c_prod = "Air Fryer 6.5L Digital"
            c_price = 6499.0
            c_date = "2026-10-04"
            c_desc = "Glass fry basket was received completely shattered inside the delivery box."
        else:
            c_name = "Govindu Tarun"
            c_order = "OD-2026-77291"
            c_prod = "65W Fast Charger Multi-Port"
            c_price = 1499.0
            c_date = "2026-09-20"
            c_desc = "Type-C port does not deliver power; sparking sound on plug-in."

        cust_name = st.text_input("Customer Name", c_name)
        cust_order = st.text_input("Order ID", c_order)
        cust_product = st.text_input("Product Name", c_prod)
        cust_price = st.number_input("Purchase Price (INR)", value=float(c_price))
        cust_date = st.text_input("Purchase Date (YYYY-MM-DD)", c_date)
        cust_desc = st.text_area("Defect / Damage Description", c_desc)

        fight_btn = st.button("⚔️ Deploy AI Advocate to Fight Support", type="primary", use_container_width=True)

    with col_chat:
        st.write("### ⚖️ Live Dispute Resolution Arena")
        if fight_btn:
            with st.spinner("AI Advocate analyzing legal statutes, countering customer care bot, and securing settlement..."):
                advocacy_result = orchestrator.run_consumer_dispute_resolution(
                    customer_name=cust_name,
                    order_id=cust_order,
                    product_name=cust_product,
                    purchase_price=cust_price,
                    purchase_date=cust_date,
                    incident_description=cust_desc
                )

            st.balloons()
            st.success(f"VICTORY: {advocacy_result['settlement_type']}")
            st.metric("Total Recovered Value", f"Rs. {advocacy_result['recovered_amount_inr']:,.2f}", "100% Compensation")

            st.write("#### 📜 Negotiation Transcript:")
            for msg in advocacy_result["transcript"]:
                spk = msg["speaker"]
                txt = msg["message"]
                if "Customer AI Advocate" in spk:
                    st.markdown(f"<div class='chat-bubble-ai'><strong>🛡️ {spk}</strong><br>{txt}</div>", unsafe_allow_html=True)
                elif "Corporate Support" in spk:
                    st.markdown(f"<div class='chat-bubble-corporate'><strong>🤖 {spk}</strong><br>{txt}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble-resolved'><strong>✅ {spk}</strong><br>{txt}</div>", unsafe_allow_html=True)
        else:
            st.info("Fill the form on the left or select a sample preset, then click 'Deploy AI Advocate' to watch the bot defeat stubborn corporate customer care!")
