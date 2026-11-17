"""
app/pipelines/video_pipeline.py

Orchestrates the end-to-end ingestion of a raw meeting video into the
AI Meeting Intelligence Platform:

    Video Upload -> Audio Extraction -> Transcription -> Metadata
    Generation -> Chunking -> Embedding -> Qdrant Upload -> PipelineResult

Design notes
------------
This module contains ONLY orchestration logic. All business logic
(transcription, chunking, embedding, vector storage, metadata rules)
lives in the existing services under `app.services.*` and is invoked
exclusively through their public APIs, per SERVICES.md:

    TranscriptionService.transcribe()
    ChunkingService.chunk_transcript()
    EmbeddingService.embed_chunks()
    MetadataService.generate()
    VectorStoreService.upload_chunks()

Audio extraction has no dedicated service in the current codebase, so
a small, isolated helper (`extract_audio_from_video`) is provided here.
It performs no transcription/chunking/embedding logic -- it only shells
out to `ffmpeg` and reads back basic WAV properties -- so it does not
duplicate any existing service responsibility.

All services (and the audio extractor) are injected via the
`VideoPipeline` constructor, defaulting to real implementations. This
keeps the pipeline unit-testable without requiring Whisper, Qdrant, or
ffmpeg to be installed / running.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import time
import uuid
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional

from app.models.audio import Audio
from app.models.chunk import Chunk
from app.models.meeting import Meeting
from app.models.pipeline_result import PipelineResult
from app.models.transcript import Transcript

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.metadata_service import MetadataService
from app.services.transcription_service import TranscriptionService
from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

# Video extensions the pipeline is willing to accept.
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"}

# Type alias for the injectable audio-extraction callable.
AudioExtractor = Callable[[Path, Path], Audio]


# ---------------------------------------------------------------------------
# Audio extraction helper
# ---------------------------------------------------------------------------
def extract_audio_from_video(video_path: Path, output_dir: Path) -> Audio:
    """
    Extract a mono, 16kHz PCM WAV audio track from a video file using ffmpeg.

    This is a thin utility function, not a service: it performs no
    business logic beyond turning a video container into an Audio model
    that downstream services can consume.

    Args:
        video_path: Path to the source video file.
        output_dir: Directory the extracted .wav file should be written to.
            Created if it does not already exist.

    Returns:
        An `Audio` model describing the extracted file.

    Raises:
        RuntimeError: If ffmpeg is not available, exits non-zero, or does
            not produce the expected output file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}.wav"

    command = [
        "ffmpeg",
        "-y",  # overwrite output if present
        "-i",
        str(video_path),
        "-vn",  # no video stream
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(audio_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffmpeg executable not found. Install ffmpeg and ensure it is "
            "on PATH."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed to extract audio (exit code {result.returncode}): "
            f"{result.stderr.strip()[-2000:]}"
        )

    if not audio_path.exists():
        raise RuntimeError(
            f"ffmpeg reported success but no output file was created at "
            f"{audio_path}"
        )

    with wave.open(str(audio_path), "rb") as wf:
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        duration = (n_frames / float(sample_rate)) if sample_rate else 0.0

    return Audio(
        file_path=audio_path,
        duration=duration,
        sample_rate=sample_rate,
        channels=channels,
        codec="pcm_s16le",
    )


# ---------------------------------------------------------------------------
# Video ingestion pipeline
# ---------------------------------------------------------------------------
class VideoPipeline:
    """
    Orchestrates ingestion of a single meeting video from disk into
    the vector store, producing a fully embedded and indexed set of
    Chunks along the way.

    The pipeline itself contains no business logic: every stage after
    validation/model construction is a call into an existing service's
    public API.
    """

    def __init__(
        self,
        transcription_service: Optional[TranscriptionService] = None,
        chunking_service: Optional[ChunkingService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        metadata_service: Optional[MetadataService] = None,
        vector_store_service: Optional[VectorStoreService] = None,
        audio_extractor: Optional[AudioExtractor] = None,
        audio_output_dir: Optional[Path] = None,
    ) -> None:
        """
        Args:
            transcription_service: Injected TranscriptionService instance.
                Defaults to a real `TranscriptionService()`.
            chunking_service: Injected ChunkingService instance.
                Defaults to a real `ChunkingService()`.
            embedding_service: Injected EmbeddingService instance.
                Defaults to a real `EmbeddingService()`.
            metadata_service: Injected MetadataService instance.
                Defaults to a real `MetadataService()`.
            vector_store_service: Injected VectorStoreService instance.
                Defaults to a real `VectorStoreService()`.
            audio_extractor: Callable(video_path, output_dir) -> Audio.
                Defaults to `extract_audio_from_video` (ffmpeg-based).
                Overriding this is the recommended way to test the
                pipeline without ffmpeg installed.
            audio_output_dir: Base directory under which per-meeting audio
                subdirectories are created. Defaults to a temp directory.
        """
        self.transcription_service = transcription_service or TranscriptionService()
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.metadata_service = metadata_service or MetadataService()
        self.vector_store_service = vector_store_service or VectorStoreService()
        self._audio_extractor: AudioExtractor = audio_extractor or extract_audio_from_video
        self._audio_output_dir = audio_output_dir or Path(tempfile.gettempdir()) / "meeting_intel_audio"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self,
        video_path: Path | str,
        *,
        title: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
    ) -> PipelineResult:
        """
        Execute the full video ingestion pipeline.

        Args:
            video_path: Path to the source video file on disk.
            title: Optional human-readable meeting title. Defaults to the
                video file's stem.
            uploaded_by: Optional identifier of the uploading user.
            workspace: Optional workspace identifier.
            project: Optional project identifier.

        Returns:
            A `PipelineResult` describing the outcome. `success` is False
            if any stage failed; partial artifacts produced before the
            failure are still populated so callers can inspect progress.
        """
        start_time = time.perf_counter()
        errors: List[str] = []
        warnings: List[str] = []
        video_path = Path(video_path)

        logger.info("Starting video pipeline for '%s'", video_path)

        try:
            # Step 1: Validate video ----------------------------------
            try:
                self._validate_video(video_path)
            except Exception as exc:
                logger.error("Video validation failed: %s", exc)
                errors.append(f"Validation error: {exc}")
                return self._fail(start_time, errors, warnings)

            # Step 2: Build Meeting model ------------------------------
            meeting = self._build_meeting(video_path, title, uploaded_by, workspace, project)
            logger.info("Created meeting %s ('%s')", meeting.meeting_id, meeting.title)

            # Step 3: Extract audio -------------------------------------
            try:
                logger.info("Extracting audio...")
                meeting_audio_dir = self._audio_output_dir / meeting.meeting_id
                audio = self._audio_extractor(video_path, meeting_audio_dir)
                logger.info(
                    "Finished audio extraction: duration=%.2fs, sample_rate=%d, channels=%d",
                    audio.duration,
                    audio.sample_rate,
                    audio.channels,
                )
            except Exception as exc:
                logger.exception("Audio extraction failed")
                errors.append(f"Audio extraction error: {exc}")
                return self._fail(start_time, errors, warnings, meeting=meeting)

            # Step 4: Transcribe -----------------------------------------
            try:
                logger.info("Starting transcription...")
                transcript = self.transcription_service.transcribe(meeting.meeting_id, audio)
                logger.info(
                    "Finished transcription: %d segments, language=%s",
                    len(transcript.segments),
                    transcript.language,
                )
            except Exception as exc:
                logger.exception("Transcription failed")
                errors.append(f"Transcription error: {exc}")
                return self._fail(start_time, errors, warnings, meeting=meeting, audio=audio)

            # Step 5: Generate metadata ------------------------------------
            try:
                logger.info("Generating metadata...")
                metadata = self.metadata_service.generate(meeting, audio, transcript)
                logger.info("Finished metadata generation.")
            except Exception as exc:
                logger.exception("Metadata generation failed")
                errors.append(f"Metadata error: {exc}")
                return self._fail(
                    start_time, errors, warnings, meeting=meeting, audio=audio, transcript=transcript
                )

            # Step 6: Generate semantic chunks ------------------------------
            try:
                logger.info("Generating semantic chunks...")
                chunks = self.chunking_service.chunk_transcript(transcript)
                for chunk in chunks:
                    chunk.metadata = metadata
                logger.info("Generated %d chunks.", len(chunks))
                if not chunks:
                    warnings.append("No chunks were generated from the transcript.")
            except Exception as exc:
                logger.exception("Chunking failed")
                errors.append(f"Chunking error: {exc}")
                return self._fail(
                    start_time,
                    errors,
                    warnings,
                    meeting=meeting,
                    audio=audio,
                    transcript=transcript,
                    metadata=metadata,
                )

            # Step 7: Generate embeddings ------------------------------------
            try:
                logger.info("Generating embeddings for %d chunks...", len(chunks))
                chunks = self.embedding_service.embed_chunks(chunks)
                logger.info("Finished embedding generation.")
            except Exception as exc:
                logger.exception("Embedding generation failed")
                errors.append(f"Embedding error: {exc}")
                return self._fail(
                    start_time,
                    errors,
                    warnings,
                    meeting=meeting,
                    audio=audio,
                    transcript=transcript,
                    metadata=metadata,
                    chunks=chunks,
                )

            # Step 8: Upload to Qdrant -----------------------------------------
            try:
                logger.info("Uploading vectors...")
                self.vector_store_service.upload_chunks(chunks)
                logger.info("Finished upload.")
            except Exception as exc:
                logger.exception("Vector store upload failed")
                errors.append(f"Vector upload error: {exc}")
                return self._fail(
                    start_time,
                    errors,
                    warnings,
                    meeting=meeting,
                    audio=audio,
                    transcript=transcript,
                    metadata=metadata,
                    chunks=chunks,
                )

            # Step 9: Build result ------------------------------------------
            elapsed = time.perf_counter() - start_time
            logger.info("Pipeline completed successfully in %.2fs", elapsed)
            return PipelineResult(
                success=True,
                meeting=meeting,
                audio=audio,
                transcript=transcript,
                metadata=metadata,
                chunks=chunks,
                total_chunks=len(chunks),
                elapsed_time=elapsed,
                errors=errors,
                warnings=warnings,
            )

        except Exception as exc:  # pragma: no cover - safety net
            # Catches anything truly unexpected that escaped the staged
            # handlers above (e.g. failure while constructing the Meeting
            # model itself).
            logger.exception("Unexpected pipeline failure")
            errors.append(f"Unexpected error: {exc}")
            return self._fail(start_time, errors, warnings)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_video(video_path: Path) -> None:
        """
        Validate that the given path points to a readable, supported
        video file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the path is not a file or has an unsupported
                extension.
            PermissionError: If the file is not readable.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not video_path.is_file():
            raise ValueError(f"Path is not a file: {video_path}")
        if video_path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
            raise ValueError(
                f"Unsupported video extension '{video_path.suffix}'. "
                f"Supported extensions: {sorted(SUPPORTED_VIDEO_EXTENSIONS)}"
            )
        if not os.access(video_path, os.R_OK):
            raise PermissionError(f"Video file is not readable: {video_path}")

    @staticmethod
    def _build_meeting(
        video_path: Path,
        title: Optional[str],
        uploaded_by: Optional[str],
        workspace: Optional[str],
        project: Optional[str],
    ) -> Meeting:
        """Construct the initial Meeting model for a new pipeline run."""
        return Meeting(
            meeting_id=str(uuid.uuid4()),
            title=title or video_path.stem,
            video_path=video_path,
            created_at=datetime.now(timezone.utc),
            uploaded_by=uploaded_by,
            workspace=workspace,
            project=project,
            status="processing",
        )

    @staticmethod
    def _fail(
        start_time: float,
        errors: List[str],
        warnings: List[str],
        meeting: Optional[Meeting] = None,
        audio: Optional[Audio] = None,
        transcript: Optional[Transcript] = None,
        metadata=None,
        chunks: Optional[List[Chunk]] = None,
    ) -> PipelineResult:
        """Build a failed PipelineResult with whatever artifacts exist so far."""
        chunks = chunks or []
        return PipelineResult(
            success=False,
            meeting=meeting,
            audio=audio,
            transcript=transcript,
            metadata=metadata,
            chunks=chunks,
            total_chunks=len(chunks),
            elapsed_time=time.perf_counter() - start_time,
            errors=errors,
            warnings=warnings,
        )


# ---------------------------------------------------------------------------
# Convenience module-level function
# ---------------------------------------------------------------------------
def run_video_pipeline(video_path: Path | str, **kwargs) -> PipelineResult:
    """
    Convenience wrapper that constructs a `VideoPipeline` with default,
    real service implementations and runs it once.

    Args:
        video_path: Path to the source video file.
        **kwargs: Forwarded to `VideoPipeline.run` (title, uploaded_by,
            workspace, project).

    Returns:
        The resulting `PipelineResult`.
    """
    pipeline = VideoPipeline()
    return pipeline.run(video_path, **kwargs)
