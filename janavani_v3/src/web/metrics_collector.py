import os
import redis
import psutil
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.responses import Response
from fastapi.security.api_key import APIKeyHeader

router = APIRouter(prefix="/api/v3/core", tags=["System Telemetry & Metrics"])

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-v3-token", "web-v3-token", "whatsapp-v3-token", "messenger-v3-token", "prometheus-scraper-token"}

def verify_metrics_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized metrics collection request.")
    return token

@router.get("/metrics")
async def fetch_production_telemetry_stream(token: str = Depends(verify_metrics_token)):
    """
    Exposes raw system performance counters to the internal Prometheus scraper.
    CRITICAL: Contains zero user data, tracking identifiers, or case context records.
    """
    # 1. Gather Host Virtual Memory and CPU Utilization Statistics
    cpu_usage_pct = psutil.cpu_percent(interval=None)
    memory_info = psutil.virtual_memory()
    
    # 2. Extract Transient Queue Volumes from Volatile Redis Memory Grid
    redis_host = os.getenv("REDIS_HOST", "localhost")
    try:
        r_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        active_document_drafts = len(r_client.keys("transient_doc:results:*"))
        revoked_security_tokens = len(r_client.keys("security:blacklisted_tokens:*"))
        system_errors_logged = int(r_client.get("metrics:global:total_errors") or 0)
    except Exception:
        active_document_drafts = 0
        revoked_security_tokens = 0
        system_errors_logged = -1  # Indicates redis connection timeout status flag

    # 3. Format Telemetry Output Lines matching the standard open-metrics text specification
    prometheus_lines = [
        "# HELP janavani_host_cpu_utilization_percent Current system CPU load percentage on the host node.",
        "# TYPE janavani_host_cpu_utilization_percent gauge",
        f"janavani_host_cpu_utilization_percent {cpu_usage_pct}",
        
        "# HELP janavani_host_memory_usage_bytes Current virtual system memory usage footprint in bytes.",
        "# TYPE janavani_host_memory_usage_bytes gauge",
        f"janavani_host_memory_usage_bytes {memory_info.used}",
        
        "# HELP janavani_transient_active_drafts_count Number of active document tracks currently alive inside the volatile RAM cache.",
        "# TYPE janavani_transient_active_drafts_count gauge",
        f"janavani_transient_active_drafts_count {active_document_drafts}",
        
        "# HELP janavani_revoked_interface_tokens_count Cumulative volume of interface client access tokens blacklisted by SOS triggers.",
        "# TYPE janavani_revoked_interface_tokens_count counter",
        f"janavani_revoked_interface_tokens_count {revoked_security_tokens}",
        
        "# HELP janavani_pipeline_system_errors_total Cumulative counter logging background task worker connection drop events.",
        "# TYPE janavani_pipeline_system_errors_total counter",
        f"janavani_pipeline_system_errors_total {system_errors_logged}"
    ]

    return Response(content="\n".join(prometheus_lines), media_type="text/plain")
