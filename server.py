"""
server.py — FastAPI High-Performance Backend for SupplyPulse
Serves REST APIs for B2B Procurement, ML Demand Forecaster, Consumer Dispute Advocate,
and serves the ultra-modern custom Web UI.
"""

import sys
from pathlib import Path
from typing import Optional

# Setup paths so supplypulse package is discoverable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT.parent))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from supplypulse.agents.orchestrator import SupplyPulseOrchestrator

app = FastAPI(title="SupplyPulse AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "web"
STATIC_DIR.mkdir(exist_ok=True)

orchestrator = SupplyPulseOrchestrator(PROJECT_ROOT)


class DisputeRequest(BaseModel):
    customer_name: str
    order_id: str
    product_name: str
    purchase_price: float
    purchase_date: str
    incident_description: str


class ProcureRequest(BaseModel):
    sku_id: str


@app.get("/api/health")
def health():
    return {"status": "ONLINE", "agents_active": 5}


@app.get("/api/inventory")
def get_inventory():
    """Returns real-time warehouse inventory and ML stockout forecasts."""
    try:
        scan_results = orchestrator.sentinel.scan_warehouse()
        return scan_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/b2b/procure")
def run_b2b_procurement(req: ProcureRequest):
    """Executes multi-agent procurement cycle for a specific SKU."""
    try:
        res = orchestrator.run_b2b_procurement_cycle(target_sku_id=req.sku_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/consumer/dispute")
def run_consumer_dispute(req: DisputeRequest):
    """Executes customer advocate legal negotiation against corporate support."""
    try:
        res = orchestrator.run_consumer_dispute_resolution(
            customer_name=req.customer_name,
            order_id=req.order_id,
            product_name=req.product_name,
            purchase_price=req.purchase_price,
            purchase_date=req.purchase_date,
            incident_description=req.incident_description
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve static web frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "SupplyPulse API live. Web UI compiling..."}
