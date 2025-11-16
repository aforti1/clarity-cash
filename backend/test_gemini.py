# test_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Create model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Test it
prompt = "Write a haiku about coding"
response = model.generate_content(prompt)
print(response.text)