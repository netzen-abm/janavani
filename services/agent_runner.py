from typing import Dict, Any, List
from services import rag_agent, agent_tools


def generate_complaint(user_info: Dict[str, Any], facts: str, k: int = 4) -> str:
    """Simple orchestration: retrieve top-k contexts, then generate a complaint draft."""
    # Retrieve contexts
    hits = rag_agent.retrieve(facts, k=k)
    contexts = [h["text"] for h in hits]
    # Generate letter using the local model (or fallback)
    letter = agent_tools.generate_complaint_tool(user_info, facts, contexts)
    return letter
