import os
import io
import json
import uuid
import logging
from celery import Celery
import redis
from src.utils.validators import PrivacyPreservingTokenizer
from src.services.document_generator import MultiFormatDocumentEngine

# Initialize Celery and bind it to your volatile internal Docker network link
REDIS_URL = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/0"
celery_app = Celery("janavani_workers", broker=REDIS_URL, backend=REDIS_URL)

logger = logging.getLogger("janavani.worker")

@celery_app.task(name="tasks.process_multimodal_grievance_async")
def process_multimodal_grievance_async(task_id: str, raw_text: str, has_voice: bool, location_code: str, export_format: str):
    """
    Executes heavy multi-modal compilation, privacy tokenization, 
    and document formatting loops inside isolated background workers.
    """
    logger.info(f"🚀 Initializing background task thread for ID: {task_id}")
    
    r_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)
    
    # 1. Clean data fields locally using privacy filters
    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(raw_text)
    
    # 2. Build the final structured legal petition template text
    formal_letter_body = (
        f"FORMAL PUBLIC GRIEVANCE PETITION / MEMORANDUM OF ACCOUNTABILITY\n"
        f"====================================================================\n"
        f"AUTHORITY ANCHOR: Derived under the Preamble ('WE, THE PEOPLE OF INDIA') "
        f"read with Article 51A (Fundamental Duties) of the Constitution of India.\n\n"
        f"FACTUAL DISCLOSURES:\n"
        f"- {scrubbed_data['sanitized_text']}\n\n"
        f"Submitted Sincerely,\n"
        f"A Sovereign Citizen of India\n\n"
        f"--------------------------------------------------------------------\n"
        f"ELECTRONIC RECORD DELIVERY NOTICE:\n"
        f"Please acknowledge receipt of this email (electronic record) u/s 12(1) "
        f"of the Information Technology Act, 2000."
    )
    
    # 3. Compile raw binary streams based on format choices
    if export_format.upper() == "DOCX":
        stream = MultiFormatDocumentEngine.generate_docx_stream(formal_letter_body)
        binary_payload = stream.getvalue()
    else:
        stream = MultiFormatDocumentEngine.generate_pdf_stream(formal_letter_body)
        binary_payload = stream.getvalue()
        
    # 4. Save the generated asset to transient storage with a strict 30-minute expiration
    result_key = f"transient_doc:results:{task_id}"
    r_client.hset(result_key, mapping={
        "status": "COMPLETED",
        "format": export_format.upper(),
        "document_text": formal_letter_body
    })
    r_client.expire(result_key, 1800)
    
    logger.info(f"✔ Task Thread {task_id} successfully compiled and committed to volatile cache arrays.")
    return True
