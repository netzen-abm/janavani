import os
from typing import Dict, Any, List

# Optional local LLM generator using Hugging Face transformers
# If no model configured, generator will return a simple template response.

LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "")  # e.g. 'gpt2' or path to local ggml/gguf wrapper


def generate_with_local_model(prompt: str, max_new_tokens: int = 512) -> str:
    """Attempt to generate text with a local HF model if configured.

    This function is best-effort: if the transformers model cannot be loaded (e.g., due to missing GPU
    or large model on CPU), it will return a fallback string so the system remains testable.
    """
    if not LOCAL_LLM_MODEL:
        return "[NO_LOCAL_LLM_CONFIGURED] " + prompt[:1000]

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        import torch

        device = 0 if torch.cuda.is_available() else -1
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_LLM_MODEL)
        model = AutoModelForCausalLM.from_pretrained(LOCAL_LLM_MODEL)
        gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
        out = gen(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        return out[0]["generated_text"]
    except Exception as e:
        # Return a readable fallback so users can continue testing retrieval and UI flow.
        return f"[LOCAL_LLM_ERROR: {e}] \nPrompt:\n" + prompt[:1500]


# High-level tool functions used by the simple agent runner

def rag_search_tool(question: str, retriever_fn) -> List[Dict[str, Any]]:
    """Call the retriever function (provided by services.rag_agent) and return raw results."""
    return retriever_fn(question)


def generate_complaint_tool(user_info: Dict[str, Any], facts: str, retrieved_contexts: List[str]) -> str:
    """Compose a prompt combining user info, facts, and retrieved contexts, then call the local generator."""
    prompt = (
        "You are an assistant that drafts a formal legal complaint letter for India. "
        "Use the facts and legal context provided. Keep it concise and professional.\n\n"
        f"User info:\n{user_info}\n\nFacts:\n{facts}\n\n"
        "Relevant context:\n"
        + "\n---\n".join(retrieved_contexts)
        + "\n\nDraft the complaint letter:\n"
    )
    return generate_with_local_model(prompt)
