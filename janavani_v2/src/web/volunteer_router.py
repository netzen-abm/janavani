from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any, List, Optional
import redis
import json
import os

router = APIRouter(prefix="/api/v2/registry", tags=["Decentralized Volunteer Network"])

class VolunteerRegistrationSchema(BaseModel):
    registration_type: str = Field(..., description="Must be 'INDIVIDUAL', 'SOCIETY', 'INSTITUTE', or 'ORGANIZATION'")
    legal_name_or_title: str = Field(..., description="Official title or name of the registering entity.")
    area_of_expertise: str = Field(..., description="Field of focus, e.g., 'Legal Defense', 'RTI Tracking', 'Public Health', 'Labor Laws'")
    contact_email: EmailStr = Field(..., description="Secure destination email for coordinating civic actions.")
    operating_district_code: str = Field(..., description="Target regional tracking code, e.g., 'KL-TVM-01'")
    nostr_public_key: Optional[str] = Field(None, description="Optional Nostr pubkey for identity verification.")

def get_redis_client():
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

@router.post("/register", response_model=Dict[str, Any])
async def register_community_volunteer_node(payload: VolunteerRegistrationSchema, redis_db: redis.Redis = Depends(get_redis_client)):
    """Registers individuals, societies, or institutes as active nodes in Janavani's civic defense network."""
    
    # Standardize types and validate registration inputs
    reg_type = payload.registration_type.upper()
    if reg_type not in ["INDIVIDUAL", "SOCIETY", "INSTITUTE", "ORGANIZATION"]:
        raise HTTPException(status_code=400, detail="Invalid registration type profile classification.")

    registry_key = f"registry:district:{payload.operating_district_code}:type:{reg_type}"
    node_id = f"node:{uuid.uuid4().hex[:8]}"
    
    serialized_node_data = json.dumps(payload.model_dump())
    
    try:
        # Save registration profiles securely as hash indexes in memory
        redis_db.hset(registry_key, node_id, serialized_node_data)
        return {
            "status": "REGISTRATION_RECORDED_SUCCESSFULLY",
            "assigned_node_id": node_id,
            "district_code_bound": payload.operating_district_code
        }
    except redis.RedisError as db_fault:
        raise HTTPException(status_code=500, detail=f"Registry database allocation pool error: {str(db_fault)}")

@router.get("/list/{district_code}", response_model=List[Dict[str, Any]])
async def fetch_district_volunteer_network(district_code: str, redis_db: redis.Redis = Depends(get_redis_client)):
    """Allows client interfaces to query active legal aid nodes and volunteer networks within a target region."""
    combined_network_nodes = []
    target_types = ["INDIVIDUAL", "SOCIETY", "INSTITUTE", "ORGANIZATION"]
    
    try:
        for reg_type in target_types:
            registry_key = f"registry:district:{district_code}:type:{reg_type}"
            raw_hash_data = redis_db.hgetall(registry_key)
            for node_id, data_string in raw_hash_data.items():
                parsed_node = json.loads(data_string)
                parsed_node["node_id"] = node_id
                combined_network_nodes.append(parsed_node)
                
        return combined_network_nodes
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Failed to retrieve volunteer registry records.")
