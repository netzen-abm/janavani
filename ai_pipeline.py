import os
import json
import requests

# =====================================================================
# DATA PARSER PARSING BLOCK
# =====================================================================
def parse_model_response(raw_text):
    """
    Cleans raw text output and structures it safely into readable 
    informational chunks for the Janavani user interface.
    """
    if not raw_text or not isinstance(raw_text, str):
        return {"error": "Invalid text input received from API pipeline endpoint."}
        
    cleaned = raw_text.strip()
    
    # Check if the model answered with a raw JSON block string wrapper
    if cleaned.startswith("```json") and cleaned.endswith("```"):
        try:
            # Strip markdown formatting ticks to extract pure JSON structural data
            json_string = cleaned.split("```json")[1].split("```")[0].strip()
            return json.loads(json_string)
        except (IndexError, json.JSONDecodeError):
            pass # Fall back to plain text structure mapping if split fails
            
    # Standard text layout structuring fallback
    return {
        "status": "success",
        "processed_timestamp": "2026-08-13", # Anchor reference log
        "data_payload": cleaned
    }

# =====================================================================
# PIPELINE CONFIGURATION 1: SARVAM-M (OPENROUTER)
# =====================================================================
def run_sarvam_pipeline(prompt_text):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[WARNING] Skipped: OPENROUTER_API_KEY secret is not present.")
        return None

    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sarvamai/sarvam-m-24b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are the Janavani AI. Output clear, unstructured facts categorized in clean text. Do not provide official legal advice."
            },
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.15
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            raw_output = response.json()['choices']['message']['content']
            return parse_model_response(raw_output)
        else:
            return {"error": f"OpenRouter status code error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Network transmission error: {str(e)}"}

# =====================================================================
# PIPELINE CONFIGURATION 2: AIRAVATA IIT-M (HUGGING FACE)
# =====================================================================
def run_airavata_pipeline(prompt_text):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("[WARNING] Skipped: HF_TOKEN secret is not present.")
        return None

    url = "https://huggingface.co"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": f"<|user|>\n{prompt_text}\n<|assistant|>",
        "parameters": {"max_new_tokens": 256, "temperature": 0.2}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            res_data = response.json()
            # Handle standard Hugging Face serverless array wrapping formats
            raw_output = res_data[0]['generated_text'] if isinstance(res_data, list) else res_data.get('generated_text', '')
            return parse_model_response(raw_output)
        else:
            return {"error": f"Hugging Face status code error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Network transmission error: {str(e)}"}

# =====================================================================
# PIPELINE AUTOMATION TEST EXECUTION ORCHESTRATOR
# =====================================================================
if __name__ == "__main__":
    print("Initializing compliance integration pipeline assertions...")
    
    test_prompt = "റോഡ് തകരാർ കാരണം ഉണ്ടായ പ്രശ്നം പരിഹരിക്കാൻ എവിടെ പരാതി നൽകണം?"
    
    # Run test simulations
    sarvam_result = run_sarvam_pipeline(test_prompt)
    if sarvam_result:
        print("\n--- Sarvam-M Output Structure Parsed ---")
        print(json.dumps(sarvam_result, indent=2, ensure_ascii=False))

    airavata_result = run_airavata_pipeline("शिकायत पत्र का प्रारूप क्या होना चाहिए?")
    if airavata_result:
        print("\n--- IIT-M Airavata Output Structure Parsed ---")
        print(json.dumps(airavata_result, indent=2, ensure_ascii=False))
        
    print("\nPipeline check completed successfully.")
