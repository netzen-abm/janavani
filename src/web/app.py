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
