"""
Application Configuration

Central place for all configurable values.
"""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"

UPLOAD_DIR = DATA_DIR / "uploads"

AUDIO_DIR = DATA_DIR / "audio"

TRANSCRIPT_DIR = DATA_DIR / "transcripts"

LOG_DIR = PROJECT_ROOT / "logs"

# =============================================================================
# WHISPER CONFIGURATION
# =============================================================================

WHISPER_MODEL = "base"

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

CHUNK_OVERLAP_SEGMENTS = 1
# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

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

COLLECTION_NAME = "meeting_chunks"

VECTOR_DISTANCE = "Cosine"

VECTOR_SIZE = EMBEDDING_DIMENSION

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

LLM_MODEL = "llama3.1"

LLM_TEMPERATURE = 0.2

MAX_TOKENS = 2048


# =============================================================================
# RETRIEVAL CONFIGURATION
# =============================================================================

TOP_K = 5

RETRIEVAL_LIMIT = 5

SIMILARITY_THRESHOLD = 0.70