import redis
import json
import logging
from typing import Optional, Dict, Any
from src.core.settings import ai_settings

logger = logging.getLogger("janavani.storage.cache")

class TransientStorageEngine:
    """
    In-memory transient cache system utilizing strict time-to-live rules.
    Guarantees no raw citizen text metadata hits non-volatile system disk arrays.
    """
    def __init__(self):
        # Default connection settings point to the internal Docker compose link network
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        # Automated self-destruct threshold (e.g., 1800 seconds = 30 minutes)
        self.expiry_ttl_seconds = 1800

    def cache_transient_document(self, task_id: str, document_payload: Dict[str, Any]) -> bool:
        """Serializes and pushes payload down to active memory with strict expiration parameters."""
        try:
            serialized_data = json.dumps(document_payload)
            return self.redis_client.setex(
                name=f"transient_doc:{task_id}",
                time=self.expiry_ttl_seconds,
                value=serialized_data
            )
        except redis.RedisError as e:
            logger.error(f"Failed to commit memory buffer block safely: {str(e)}")
            return False

    def retrieve_transient_document(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Pulls transient metadata matrix block from storage grid if lifecycle is active."""
        try:
            raw_data = self.redis_client.get(f"transient_doc:{task_id}")
            if raw_data:
                return json.loads(raw_data)
        except redis.RedisError as e:
            logger.error(f"Transient tracking pool query dropped: {str(e)}")
        return None
