import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "milk_management_secret_key_2026")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# AI / LLM configuration
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() != "false"
AI_LLM_DISABLED = os.getenv("AI_LLM_DISABLED", "0") == "1"
AI_CHAT_MAX_TOKENS = int(os.getenv("AI_CHAT_MAX_TOKENS", "700"))
AI_CHAT_MAX_REQUESTS_PER_MINUTE = int(os.getenv("AI_CHAT_MAX_REQUESTS_PER_MINUTE", "20"))
