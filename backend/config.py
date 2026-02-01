import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# --- SERVER SETTINGS ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# --- OLLAMA SETTINGS ---
# Default to localhost for Mac/Local dev.
# Use 'http://host.docker.internal:11434' ONLY if running backend inside Docker.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TIMEOUT_SECONDS = 300

# --- MODEL REGISTRY ---
# Standard Dimensions: Nomic/BERT = 768.
EMBED_DIMENSION = 768
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder")
VISION_MODEL = os.getenv("VISION_MODEL", "llama3.2-vision")

# --- GLINER SETTINGS ---
NER_MODEL_NAME = "urchade/gliner_small-v2.1"
GLINER_MODEL_NAME = NER_MODEL_NAME  # backwards compatibility
GLINER_LOCAL_DIR = "gliner_small"

# --- PRIVACY SETTINGS ---
DEFAULT_EPSILON = 1.0
L1_SENSITIVITY = 0.1  # Adjusted for better default utility with embedding vectors
MIN_EPSILON = 0.0001
PRIVACY_BUDGET_THRESHOLD = 0.5

# --- VISUAL SETTINGS ---
PDF_RENDER_SCALE = 2.0
AUDIT_BOX_WIDTH = 5
BLUR_RADIUS = 15

# --- YUNET SETTINGS ---
FACE_DETECTION_MODEL_NAME = 'face_detection_yunet_2023mar.onnx'
FACE_DETECTION_MODEL_DIR = "face_detection_yunet"
FACE_DETECTION_MODEL_PATH = os.path.join("data", "models", FACE_DETECTION_MODEL_DIR, FACE_DETECTION_MODEL_NAME)
DEFAULT_TEST_IMAGE = os.path.join("data", "test_data", "selfie_test.jpg")
DEFAULT_BLURRED_OUTPUT = os.path.join("data", "results", "blurred_selfie.jpg")
FACE_CONFIDENCE_THRESHOLD = 0.9
FACE_BLUR_KERNEL_SIZE = 51

# --- DETECTION RULES ---
NER_THRESHOLD = 0.3

SCANNER_CHUNK_SIZE = 300
SCANNER_CHUNK_OVERLAP = 50

NER_LABELS = [
    "person", "organization", "location",
    "email", "phone number", "credit card number",
    "internal project name",
    "ip address", "passport number"
]

SECRET_KEYWORDS = [
    "def ", "class ", "import ", "API_KEY", "secret",
    "{", "};", "sk-", "Key", "password", "token",
    "api key", "sk"
]

PII_REGEX_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', 'openai_key'),
    (r'ghp_[a-zA-Z0-9]{36,}', 'github_token'),
    (r'(?i)(?:AKIA|ASIA)[A-Z0-9]{16}', 'aws_access_key'),
    (r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*', 'bearer_token'),
    (r'(?i)(password|pwd|passwd)\s*[:=]\s*\S+', 'password'),
    (r'\b[A-Z]{2,}[A-Z0-9]{8,}\b', 'generic_key'),
    (r'\b[a-f0-9]{32,}\b', 'hash_or_key'),
    (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'credit_card'),
    (r'\b[A-Za-z0-9._%+-]+(?:\s*@\s*|\s+at\s+)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email_address'),
    (r'(?:\+?\d{1,3}[- .]?)?\(?\d{3}\)?[- .]?\d{3}[- .]?\d{4,}', 'phone_number'),
    (r'\+\d{1,3}\s?\d{4,}', 'phone_number'),
]

# --- SYSTEM PROMPTS ---
CODE_SCANNER_PROMPT = """
You are a Security Auditor. Your task is to identify SENSITIVE SECRETS in the provided text.
Target Entities:
1. API Keys (e.g., sk-..., AWS_ACCESS_KEY)
2. Hardcoded Passwords
3. Database Connection Strings
4. Private Key Blocks

Instructions:
- Return ONLY a JSON list of the exact strings found.
- If no secrets are found, return an empty list [].
- Do not output any markdown or conversational text.
"""

VISION_ANALYSIS_PROMPT = """
You are shown an image. Describe the main elements in the foreground with clear and vivid detail, 
keeping the description concise and limited to a maximum of 3 sentences.
"""

VISION_PDF_ANALYSIS_PROMPT = """
You are given a PDF document. Summarize the main content, focusing on key information and insights, 
while strictly excluding any personally identifiable information (PII).
"""

# --- PII EXTRACTION SETTINGS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATA_DIR = os.path.join(BASE_DIR, "data")

PII_TEST_DOCUMENT_IMAGE = os.path.join("data", "test_data", "document_image_test.png")
PII_IMAGE_MAX_DIMENSION = 700
PII_IMAGE_QUALITY = 96
PII_MODEL_TEMPERATURE = 0.0

PII_EXTRACTOR_SYSTEM_PROMPT = (
    "You are a PII extraction API. Output JSON ONLY. "
    "Extract clearly visible: names, id_numbers, addresses, "
    "date_of_birth, phone_numbers, emails, social_security_numbers, "
    "api_keys, credit_cards. "
    "Format: {\"names\": [\"John Doe\"], ...}. "
    "If nothing found, return empty lists."
)

# --- AUDIO SETTINGS ---
WHISPER_MODEL_SIZE = "small"
WHISPER_DEVICE = "cpu"

# --- API & WEB SETTINGS ---
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Max Upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'wav', 'mp3'}
DEBUG = os.getenv("DEBUG", "True").lower() == "true"