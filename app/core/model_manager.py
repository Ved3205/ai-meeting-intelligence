from __future__ import annotations

from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer

from app.config.settings import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    EMBEDDING_BATCH_SIZE,
)


class ModelManager:

    _whisper_model: WhisperModel | None = None
    _embedding_model: SentenceTransformer | None = None

    @classmethod
    def get_whisper_model(cls):

        if cls._whisper_model is None:

            print("Loading Whisper Model...")

            cls._whisper_model = WhisperModel(
                WHISPER_MODEL,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
            )

            print("Whisper Loaded.")

        return cls._whisper_model

    @classmethod
    def get_embedding_model(cls):

        if cls._embedding_model is None:

            print("Loading Embedding Model...")

            cls._embedding_model = SentenceTransformer(
                EMBEDDING_MODEL,
                device=EMBEDDING_DEVICE,
            )

            print("Embedding Model Loaded.")

        return cls._embedding_model