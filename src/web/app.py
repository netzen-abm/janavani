from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from src.services.legal_agent import JanavaniLegalAgent
from src.utils.validators import PrivacyPreservingTokenizer, LegalDocumentSchema
import json

app = FastAPI(title="Janavani Agentic AI Service Gateway")
router = APIRouter(prefix="/api/v1/agent")

# Independent interface authentication layer protecting the internal AI microservice
INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-mvp-token-xyz", "web-mvp-token-abc", "android-client-token-123"}

def verify_interface_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface client credential request.")
    return token

class ProcessIssueRequest(BaseModel):
    citizen_raw_input: str

@router.post("/draft", response_model=LegalDocumentSchema)
async def process_citizen_document_workflow(
    payload: ProcessIssueRequest,
    interface_token: str = Depends(verify_interface_token)
):
    """
    Decoupled endpoint handling input asynchronously across individual network channel interfaces.
    Fails completely isolated without disrupting parallel frontend engines.
    """
    if not payload.citizen_raw_input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be blank.")

    # Step 1: Execute Local Privacy Scrubbing Layer
    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(payload.citizen_raw_input)
    
    # Step 2: Query AI Routing Agent Engine 
    agent = JanavaniLegalAgent()
    ai_raw_response = agent.draft_legal_document(scrubbed_data["sanitized_text"])
    
    if "error" in ai_raw_response:
        raise HTTPException(status_code=502, detail=ai_raw_response["message"])
        
    try:
        # Enforce structural consistency via JSON schemas using Pydantic mapping
        choices = ai_raw_response.get("choices", [{}])
        content_string = choices[0].get("message", {}).get("content", "{}")
        parsed_json = json.loads(content_string)
        
        validated_document = LegalDocumentSchema(**parsed_json)
        return validated_document
        
    except Exception as parse_error:
        raise HTTPException(
            status_code=422, 
            detail=f"AI output violated structured legal formatting bounds. Refusing generation. Trace: {str(parse_error)}"
        )

app.include_router(router)


# --------------------------

from flask import Flask, request, jsonify

# reuse your existing system
from src.conversation.engine import handle_message

app = Flask(__name__)

# simple session memory (temporary)
sessions = {}

@app.route("/")
def home():
    return "Janavani Web App Running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    user_id = data.get("user_id", "web_user")
    message = data.get("message", "")

    if user_id not in sessions:
        sessions[user_id] = {}

    state = sessions[user_id]

    response = handle_message(message, state)

    return jsonify({
        "response": response,
        "state": state
    })


if __name__ == "__main__":
    app.run(debug=True)

# -----------------------------

import uuid
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from src.services.legal_agent import JanavaniLegalAgent
from src.utils.validators import PrivacyPreservingTokenizer, LegalDocumentSchema
from src.storage.cache import TransientStorageEngine
import json

app = FastAPI(title="Janavani Agentic AI Service Gateway")
router = APIRouter(prefix="/api/v1/agent")

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-mvp-token-xyz", "web-mvp-token-abc", "android-client-token-123"}

def verify_interface_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface client credential request.")
    return token

class ProcessIssueRequest(BaseModel):
    citizen_raw_input: str

@router.post("/draft", response_model=Dict[str, Any])
async def process_citizen_document_workflow(
    payload: ProcessIssueRequest,
    interface_token: str = Depends(verify_interface_token)
):
    if not payload.citizen_raw_input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be blank.")

    # 1. Execute local anonymization layer
    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(payload.citizen_raw_input)
    
    # 2. Run legal extraction workflow
    agent = JanavaniLegalAgent()
    ai_raw_response = agent.draft_legal_document(scrubbed_data["sanitized_text"])
    
    if "error" in ai_raw_response:
        raise HTTPException(status_code=502, detail=ai_raw_response["message"])
        
    try:
        choices = ai_raw_response.get("choices", [{}])
        content_string = choices[0].get("message", {}).get("content", "{}")
        parsed_json = json.loads(content_string)
        
        # Enforce anti-chat constraints via schema mapping validation
        validated_document = LegalDocumentSchema(**parsed_json)
        
        # 3. Create a unique document state tracker ID
        tracking_id = str(uuid.uuid4())
        
        # 4. Offload parsed structure safely into Redis memory grid
        cache_engine = TransientStorageEngine()
        success = cache_engine.cache_transient_document(tracking_id, validated_document.model_dump())
        
        if not success:
            raise HTTPException(status_code=500, detail="Secured memory pipeline caching error occurred.")
            
        return {
            "status": "GENERATED_SUCCESSFULLY",
            "tracking_id": tracking_id,
            "lifecycle_ttl_seconds": 1800,
            "document": validated_document.model_dump()
        }
        
    except Exception as parse_error:
        raise HTTPException(
            status_code=422, 
            detail=f"AI framework violated strict administrative structuring requirements. Refusing payload parsing. Trace: {str(parse_error)}"
        )

@router.get("/retrieve/{tracking_id}", response_model=LegalDocumentSchema)
async def fetch_cached_document(tracking_id: str, interface_token: str = Depends(verify_interface_token)):
    """Allows decoupled interfaces to securely poll generated structural blocks prior to automatic deletion."""
    cache_engine = TransientStorageEngine()
    document_data = cache_engine.retrieve_transient_document(tracking_id)
    
    if not document_data:
        raise HTTPException(status_code=404, detail="Document tracker has expired or does not exist.")
        
    return LegalDocumentSchema(**document_data)

app.include_router(router)

# -----------------------------

import uuid
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any
from src.services.legal_agent import JanavaniLegalAgent
from src.utils.validators import PrivacyPreservingTokenizer, LegalDocumentSchema
from src.storage.cache import TransientStorageEngine
from src.storage.analytics import PrivacyPreservingAnalytics
import json

app = FastAPI(title="Janavani Agentic AI Service Gateway")
router = APIRouter(prefix="/api/v1/agent")

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-mvp-token-xyz", "web-mvp-token-abc", "android-client-token-123"}

def verify_interface_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface client credential request.")
    return token

class ProcessIssueRequest(BaseModel):
    citizen_raw_input: str

@router.post("/draft", response_model=Dict[str, Any])
async def process_citizen_document_workflow(
    payload: ProcessIssueRequest,
    interface_token: str = Depends(verify_interface_token)
):
    if not payload.citizen_raw_input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be blank.")

    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(payload.citizen_raw_input)
    
    agent = JanavaniLegalAgent()
    ai_raw_response = agent.draft_legal_document(scrubbed_data["sanitized_text"])
    
    if "error" in ai_raw_response:
        # Register a generation failure for monitoring analytics
        analytics_engine = PrivacyPreservingAnalytics()
        analytics_engine.increment_generation_counter(document_type="UNKNOWN", status="FAILED")
        raise HTTPException(status_code=502, detail=ai_raw_response["message"])
        
    try:
        choices = ai_raw_response.get("choices", [{}])
        content_string = choices.get("message", {}).get("content", "{}")
        parsed_json = json.loads(content_string)
        
        validated_document = LegalDocumentSchema(**parsed_json)
        tracking_id = str(uuid.uuid4())
        
        cache_engine = TransientStorageEngine()
        success = cache_engine.cache_transient_document(tracking_id, validated_document.model_dump())
        
        if not success:
            raise HTTPException(status_code=500, detail="Secured memory pipeline caching error occurred.")
            
        # Log successful aggregate telemetry data cleanly and anonymously
        analytics_engine = PrivacyPreservingAnalytics()
        analytics_engine.increment_generation_counter(
            document_type=validated_document.document_type, 
            status="SUCCESS"
        )
            
        return {
            "status": "GENERATED_SUCCESSFULLY",
            "tracking_id": tracking_id,
            "lifecycle_ttl_seconds": 1800,
            "document": validated_document.model_dump()
        }
        
    except Exception as parse_error:
        raise HTTPException(
            status_code=422, 
            detail=f"AI framework output parsing error. Trace: {str(parse_error)}"
        )

@router.get("/metrics", dependencies=[Depends(verify_interface_token)])
async def fetch_platform_metrics():
    """Allows administrators to view global aggregate platform usage metrics safely."""
    analytics_engine = PrivacyPreservingAnalytics()
    return analytics_engine.retrieve_aggregate_insights()

app.include_router(router)

# -----------------

import uuid
import json
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any
from src.services.legal_agent import JanavaniLegalAgent
from src.utils.validators import PrivacyPreservingTokenizer, LegalDocumentSchema
from src.storage.cache import TransientStorageEngine
from src.storage.analytics import PrivacyPreservingAnalytics

app = FastAPI(title="Janavani Agentic AI Service Gateway")
router = APIRouter(prefix="/api/v1/agent")

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-mvp-token-xyz", "web-mvp-token-abc", "android-client-token-123"}

def verify_interface_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface client credential request.")
    return token

class ProcessIssueRequest(BaseModel):
    citizen_raw_input: str

@router.post("/draft", response_model=Dict[str, Any])
async def process_citizen_document_workflow(
    payload: ProcessIssueRequest,
    interface_token: str = Depends(verify_interface_token)
):
    if not payload.citizen_raw_input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be blank.")

    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(payload.citizen_raw_input)
    
    agent = JanavaniLegalAgent()
    ai_raw_response = agent.draft_legal_document(scrubbed_data["sanitized_text"])
    
    analytics_engine = PrivacyPreservingAnalytics()
    if "error" in ai_raw_response:
        analytics_engine.increment_generation_counter(document_type="UNKNOWN", status="FAILED")
        raise HTTPException(status_code=502, detail=ai_raw_response["message"])
        
    try:
        choices = ai_raw_response.get("choices", [{}])
        content_string = choices.get("message", {}).get("content", "{}")
        parsed_json = json.loads(content_string)
        
        validated_document = LegalDocumentSchema(**parsed_json)
        tracking_id = str(uuid.uuid4())
        
        cache_engine = TransientStorageEngine()
        success = cache_engine.cache_transient_document(tracking_id, validated_document.model_dump())
        
        if not success:
            raise HTTPException(status_code=500, detail="Secured memory pipeline caching error occurred.")
            
        analytics_engine.increment_generation_counter(
            document_type=validated_document.document_type, 
            status="SUCCESS"
        )
            
        return {
            "status": "GENERATED_SUCCESSFULLY",
            "tracking_id": tracking_id,
            "lifecycle_ttl_seconds": 1800,
            "document": validated_document.model_dump()
        }
        
    except Exception as parse_error:
        raise HTTPException(
            status_code=422, 
            detail=f"AI framework output parsing error. Trace: {str(parse_error)}"
        )

@router.get("/metrics")
async def fetch_platform_metrics(interface_token: str = Depends(verify_interface_token)):
    """Exposes structured metric fields to the internal Prometheus tracking scraper securely."""
    analytics_engine = PrivacyPreservingAnalytics()
    insights = analytics_engine.retrieve_aggregate_insights()
    
    # Format telemetry output using the standard Prometheus text line format
    prometheus_format_lines = [
        "# HELP janavani_total_documents_generated_globally Cumulative volume of administrative documents created.",
        "# TYPE janavani_total_documents_generated_globally counter",
        f"janavani_total_documents_generated_globally {insights['total_documents_generated_globally']}"
    ]
    from fastapi.responses import Response
    return Response(content="\n".join(prometheus_format_lines), media_type="text/plain")

app.include_router(router)
