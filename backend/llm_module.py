# backend/llm_module.py
import os
import google.generativeai as genai

# -----------------------------
# Gemini API Configuration
# -----------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
else:
    print("Warning: GEMINI_API_KEY not set. Gemini features will not work.")
    gemini_model = None


def generate_gemini_suggestion_v2(
    transaction_name: str,
    transaction_amount: float,
    category: str,
    user_context: dict = None,
) -> str:
    """Generate suggestions using Gemini API"""
    if not gemini_model:
        return "Gemini API not configured. Please set GEMINI_API_KEY."

    prompt = f"""
You are Clarity Cash AI, a friendly budgeting assistant.

Transaction:
- Name: {transaction_name}
- Amount: ${transaction_amount}
- Category: {category}

User context: {user_context if user_context else "None provided"}

Generate:
1. Up to 3 cheaper alternatives (Gemini options) with price and short explanation.
2. One micro-action to optimize user's spending related to this transaction.
3. Keep the tone friendly, concise, and playful. Include emoji if appropriate.
"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating suggestion: {str(e)}"


# -----------------------------
# General LLM suggestion
# -----------------------------
def generate_suggestion_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the generated text"""
    if not gemini_model:
        return "Gemini API not configured. Please set GEMINI_API_KEY."
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating suggestion: {str(e)}"