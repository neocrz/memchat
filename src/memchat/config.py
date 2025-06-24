# src/memchat/config.py


import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = True if os.getenv("DEBUG_MODE").lower() == "true" else False


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

