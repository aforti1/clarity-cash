# backend/llm_module.py
import os
import requests

# -----------------------------
# Hugging Face model config
# -----------------------------
HF_MODEL = "your-username/clarity_llm"  # Replace with your hosted model repo
# HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
# if not HF_API_TOKEN:
#     raise ValueError("HF_API_TOKEN not set in environment variables. Add it to your .env file.")

# HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# -----------------------------
# General LLM suggestion
# -----------------------------
def generate_suggestion(prompt: str, max_tokens: int = 100) -> str:
    """
    Send a prompt to the Hugging Face hosted model and return the generated text.
    """
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=HEADERS,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    try:
        return response.json()[0]["generated_text"]
    except (KeyError, IndexError):
        return "No suggestion generated."

# -----------------------------
# Gemini transaction suggestion
# -----------------------------
def generate_gemini_suggestion(
    transaction_name: str,
    transaction_amount: float,
    category: str,
    user_context: dict = None,
    max_tokens: int = 150
) -> str:
    """
    Generate up to 3 cheaper alternatives and 1 micro-action for a transaction.
    """
    prompt = f"""
You are Clarity Cash AI, a friendly budgeting assistant.

Transaction:
- Name: {transaction_name}
- Amount: ${transaction_amount}
- Category: {category}

User context: {user_context}

Generate:
1. Up to 3 cheaper alternatives (Gemini options) with price and short explanation.
2. One micro-action to optimize user's spending related to this transaction.
3. Keep the tone friendly, concise, and playful. Include emoji if appropriate.
"""
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=HEADERS,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    try:
        return response.json()[0]["generated_text"]
    except (KeyError, IndexError):
        return "No suggestion generated."
