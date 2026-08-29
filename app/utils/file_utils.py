"""
Generic file utilities.

These helper functions should never contain business logic.

This module contains:
1. LEGACY / EXISTING FILE UTILITIES
   - Existing helpers used throughout the application.
   - Keep these functions stable to avoid breaking existing callers.

2. UPLOAD UTILITIES
   - New upload-specific helpers.
   - Handles extension validation, safe filenames, chunked writes,
     and optional maximum upload size.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Optional, Set
import shutil
import uuid


# =============================================================================
# EXISTING / LEGACY FILE UTILITIES
# =============================================================================
# These functions are preserved from the original implementation.
# Do not change their behavior unless you intentionally want to update
# every existing caller in the application.
# =============================================================================


def create_directory(directory: Path) -> None:
    """
    Create directory if it does not exist.
    """
    directory.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """
    Check if file exists.
    """
    return path.exists()


def delete_file(path: Path) -> None:
    """
    Delete a file if it exists.
    """
    if path.exists():
        path.unlink()


def move_file(source: Path, destination: Path) -> Path:
    """
    Move file to destination.
    """
    create_directory(destination.parent)

    shutil.move(str(source), str(destination))

    return destination


def copy_file(source: Path, destination: Path) -> Path:
    """
    Copy file.
    """
    create_directory(destination.parent)

    shutil.copy2(source, destination)

    return destination


def get_extension(path: Path) -> str:
    """
    Return file extension.
    """
    return path.suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename while preserving extension.
    """
    extension = Path(original_filename).suffix

    unique_id = uuid.uuid4().hex

    return f"{unique_id}{extension}"


def list_files(directory: Path):
    """
    Return all files inside directory.
    """
    if not directory.exists():
        return []

    return [file for file in directory.iterdir() if file.is_file()]


# =============================================================================
# NEW / UPLOAD-SPECIFIC UTILITIES
# =============================================================================
# These functions provide safer handling for uploaded files.
#
# Features:
#   - Extension validation
#   - Random collision-safe filenames
#   - Path traversal protection
#   - Chunked file writing
#   - Optional maximum upload size
#
# Existing functions above remain unchanged.
# =============================================================================


# 1 MB chunks prevent us from loading the entire upload into memory.
_CHUNK_SIZE = 1024 * 1024


class UnsupportedFileTypeError(ValueError):
    """
    Raised when the uploaded file's extension is not permitted.
    """

    pass


class UploadTooLargeError(ValueError):
    """
    Raised when the uploaded file exceeds the configured size cap.
    """

    pass


def save_upload(
    file_obj: BinaryIO,
    original_filename: str,
    upload_dir: Path,
    allowed_extensions: Set[str],
    max_size_bytes: Optional[int] = None,
) -> Path:
    """
    Save an uploaded file safely to `upload_dir`.

    The original client-supplied filename is NEVER used as the destination
    filename. Only its validated extension is preserved.

    The upload is written in chunks so that large files do not need to be
    loaded completely into memory.

    Args:
        file_obj:
            Binary file-like object, for example `UploadFile.file`.

        original_filename:
            Client-supplied filename. It is used only to determine the
            extension.

        upload_dir:
            Destination directory.

        allowed_extensions:
            Set of permitted lowercase extensions including the leading dot.

            Example:
                {".mp4", ".mov", ".avi"}

        max_size_bytes:
            Optional maximum allowed upload size.

            If provided, the file is written in chunks and the upload is
            rejected as soon as the size exceeds this value.

    Returns:
        Path to the saved uploaded file.

    Raises:
        UnsupportedFileTypeError:
            If the filename has no extension or the extension is not allowed.

        UploadTooLargeError:
            If max_size_bytes is provided and the upload exceeds it.
    """

    # -------------------------------------------------------------------------
    # Validate extension
    # -------------------------------------------------------------------------

    suffix = Path(original_filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise UnsupportedFileTypeError(
            f"Unsupported file extension "
            f"'{suffix or '(none)'}' for '{original_filename}'. "
            f"Supported extensions: {sorted(allowed_extensions)}"
        )

    # -------------------------------------------------------------------------
    # Create upload directory
    # -------------------------------------------------------------------------

    create_directory(upload_dir)

    # -------------------------------------------------------------------------
    # Generate a safe random filename.
    #
    # This deliberately does NOT use original_filename as a filesystem path.
    # Therefore values such as:
    #
    #     ../../evil.exe
    #     ../../../somewhere/file.mp4
    #
    # cannot control where the upload is written.
    # -------------------------------------------------------------------------

    safe_name = f"{uuid.uuid4().hex}{suffix}"
    destination = upload_dir / safe_name

    # -------------------------------------------------------------------------
    # Stream upload to disk in chunks
    # -------------------------------------------------------------------------

    total_written = 0

    try:
        with destination.open("wb") as out_file:
            while True:
                chunk = file_obj.read(_CHUNK_SIZE)

                if not chunk:
                    break

                total_written += len(chunk)

                # -------------------------------------------------------------
                # Enforce optional upload size limit.
                # -------------------------------------------------------------

                if (
                    max_size_bytes is not None
                    and total_written > max_size_bytes
                ):
                    raise UploadTooLargeError(
                        f"'{original_filename}' exceeds the maximum "
                        f"allowed upload size of {max_size_bytes} bytes."
                    )

                out_file.write(chunk)

    except Exception:
        # ---------------------------------------------------------------------
        # If anything goes wrong while saving the upload, remove the partial
        # file so that an incomplete/corrupt upload is not left behind.
        # ---------------------------------------------------------------------

        destination.unlink(missing_ok=True)
        raise

    return destination