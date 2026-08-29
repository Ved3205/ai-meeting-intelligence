"""
Project-wide constants.

This file stores reusable constants that are fixed across the application.

Configurable application settings such as model names, paths, chunk sizes,
Qdrant configuration, and LLM configuration are defined in:

    app/config/settings.py

Do not duplicate configurable values from settings.py here.
"""

# ==========================================================
# Supported Formats
# ==========================================================

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
}

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
}

# ==========================================================
# FFmpeg / Audio Processing
# ==========================================================

DEFAULT_AUDIO_EXTENSION = ".wav"

AUDIO_SAMPLE_RATE = 16000

AUDIO_CHANNELS = 1

AUDIO_CODEC = "pcm_s16le"
