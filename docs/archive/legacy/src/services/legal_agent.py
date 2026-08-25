import requests
from typing import Dict, Any
from src.core.settings import ai_settings

class JanavaniLegalAgent:
    def __init__(self):
        self.openrouter_url = "https://openrouter.ai"
        self.hf_url = f"https://huggingface.co{ai_settings.IIT_MADRAS_TRANSLATION_MODEL}"
        
        # Rigid system instruction preventing casual use or general information search
        self.system_prompt = (
            "You are a deterministic legal document formatting engine for Janavani. "
            "Your ONLY function is to convert informal citizen complaints into structured official letters or RTIs. "
            "CRITICAL: Do not answer questions, do not chat, do not search, do not offer legal advice. "
            "If the user input is not a civic complaint or public service issue, return a strict error block. "
            "Output must strictly follow a JSON format matching the structural blocks."
        )

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        """
        Interacts with Hugging Face to leverage IIT Madras AI4Bharat models 
        for robust Indic language legal translations.
        """
        if not ai_settings.HUGGINGFACE_API_KEY:
            return text # Fallback to original text if credential missing
            
        headers = {"Authorization": f"Bearer {ai_settings.HUGGINGFACE_API_KEY}"}
        payload = {"inputs": text, "parameters": {"src_lang": "indic", "tgt_lang": target_lang}}
        
        try:
            response = requests.post(self.hf_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()[0].get("generated_text", text)
        except Exception:
            pass
        return text

    def draft_legal_document(self, citizen_issue: str) -> Dict[str, Any]:
        """
        Executes OpenRouter payload routing. Generates structured output 
        while strictly preventing chat mechanics.
        """
        # Step 1: Pre-process translation via AI4Bharat layer
        processed_issue = self.translate_input_if_needed(citizen_issue)

        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Forcing a structured JSON response schema to prevent conversational outputs
        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Draft formal complaint structure for: {processed_issue}"}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.openrouter_url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": True, "message": f"Engine failure: Status {response.status_code}"}
        except Exception as e:
            return {"error": True, "message": f"Connection dropped: {str(e)}"}

# --------------------

import requests
from typing import Dict, Any
from src.core.settings import ai_settings
from src.core.municipal_profiles import fetch_profile_by_code

class JanavaniLegalAgent:
    def __init__(self):
        self.openrouter_url = "https://openrouter.ai"
        self.hf_url = f"https://huggingface.co{ai_settings.IIT_MADRAS_TRANSLATION_MODEL}"
        
        self.system_prompt = (
            "You are a deterministic legal document formatting engine for Janavani. "
            "Your ONLY function is to convert informal citizen complaints into structured official letters or RTIs. "
            "CRITICAL: Do not answer questions, do not chat, do not search, do not offer legal advice. "
            "If the user input is not a civic complaint or public service issue, return a strict error block. "
            "Output must strictly follow a JSON format matching the structural blocks."
        )

    def translate_input_if_needed(self, text: str, target_lang: str = "en") -> str:
        if not ai_settings.HUGGINGFACE_API_KEY:
            return text
            
        headers = {"Authorization": f"Bearer {ai_settings.HUGGINGFACE_API_KEY}"}
        payload = {"inputs": text, "parameters": {"src_lang": "indic", "tgt_lang": target_lang}}
        
        try:
            response = requests.post(self.hf_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("generated_text", text)
        except Exception:
            pass
        return text

    def draft_legal_document(self, citizen_issue: str, location_code: str = "FALLBACK") -> Dict[str, Any]:
        """
        Executes OpenRouter payload routing. Generates structured output 
        while strictly preventing chat mechanics and anchoring local profiles.
        """
        processed_issue = self.translate_input_if_needed(citizen_issue)
        
        # Inject exact local body profile metadata parameters locally prior to issuing prompt context hooks
        regional_profile = fetch_profile_by_code(location_code)
        
        contextual_instruction = (
            f"{self.system_prompt} "
            f"The target recipient authority details are fixed as: {regional_profile['administrative_head_designation']}, "
            f"Address: {regional_profile['primary_postal_address']}, governing legal code statute context: {regional_profile['mandatory_rti_statute_reference']}."
        )

        headers = {
            "Authorization": f"Bearer {ai_settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": ai_settings.LEGAL_DRAFTING_MODEL,
            "messages": [
                {"role": "system", "content": contextual_instruction},
                {"role": "user", "content": f"Draft formal complaint structure for: {processed_issue}"}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.openrouter_url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": True, "message": f"Engine failure: Status {response.status_code}"}
        except Exception as e:
            return {"error": True, "message": f"Connection dropped: {str(e)}"}

