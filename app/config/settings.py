"""
Application Configuration

Central place for all configurable values.
"""

import os
import sys
from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Packaged builds keep user data outside the install folder.
FROZEN = getattr(sys, "frozen", False)

if os.environ.get("APP_DATA_DIR"):
    _APP_HOME = Path(os.environ["APP_DATA_DIR"])
elif FROZEN:
    _APP_HOME = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "AIMeeting"
else:
    _APP_HOME = PROJECT_ROOT

DATA_DIR = _APP_HOME / "data"

# Folder with bundled models (empty/missing means download from the hub).
MODELS_DIR = Path(os.environ.get("MODELS_DIR", PROJECT_ROOT / "models"))

UPLOAD_DIR = DATA_DIR / "uploads"

AUDIO_DIR = DATA_DIR / "audio"

TRANSCRIPT_DIR = DATA_DIR / "transcripts"

LOG_DIR = _APP_HOME / "logs"

# =============================================================================
# WHISPER CONFIGURATION
# =============================================================================

WHISPER_MODEL = "base"

if (MODELS_DIR / "whisper-base").is_dir():
    WHISPER_MODEL = str(MODELS_DIR / "whisper-base")

WHISPER_DEVICE = "cpu"
# "cuda" if using NVIDIA GPU

WHISPER_COMPUTE_TYPE = "int8"
# int8
# float16
# float32

WHISPER_BEAM_SIZE = 5

WHISPER_VAD_FILTER = True
# VAD stands for Voice Activity Detection to filter out non-speech segments. Set to False to disable.

# =============================================================================
# CHUNKING CONFIGURATION
# =============================================================================

CHUNK_SIZE = 120

CHUNK_OVERLAP = 20

MAX_WORDS_PER_CHUNK = 120

MAX_TOKENS_PER_CHUNK = 180

MIN_WORDS_PER_CHUNK = 60

CHUNK_OVERLAP_SEGMENTS = 0
# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

if (MODELS_DIR / "bge-small-en-v1.5").is_dir():
    EMBEDDING_MODEL = str(MODELS_DIR / "bge-small-en-v1.5")

EMBEDDING_PROVIDER = "sentence_transformers"

EMBEDDING_DEVICE = "cpu"
# "cuda" for NVIDIA GPU

EMBEDDING_NORMALIZE = True

EMBEDDING_BATCH_SIZE = 32

EMBEDDING_DIMENSION = 384

# =============================================================================
# QDRANT CONFIGURATION
# =============================================================================

QDRANT_HOST = "localhost"

QDRANT_PORT = 6333

# Set to use embedded on-disk Qdrant instead of a server.
QDRANT_PATH = os.environ.get("QDRANT_PATH") or (
    str(DATA_DIR / "qdrant") if os.environ.get("EMBEDDED_QDRANT") == "1" or FROZEN else None
)

COLLECTION_NAME = "meeting_chunks"

VECTOR_DISTANCE = "Cosine"

VECTOR_SIZE = EMBEDDING_DIMENSION

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

LLM_MODEL = "llama3.1"

LLM_TEMPERATURE = 0.2

MAX_TOKENS = 2048

LLM_NUM_CTX = 8192

LLM_TIMEOUT_SECONDS = 600


# =============================================================================
# RETRIEVAL CONFIGURATION
# =============================================================================

TOP_K = 5

RETRIEVAL_LIMIT = 5

SIMILARITY_THRESHOLD = 0.70