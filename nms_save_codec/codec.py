# File: codec.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\codec.py
# Purpose: Public decrypt / encrypt entry points for Steam/GOG NMS save files.

from __future__ import annotations

from .constants import BINARY_TERMINATOR, DEBUG_PREFIX
from .slots import guess_kind_from_filename, guess_slot_from_filename, is_account_filename
from .streaming import compress_save, decompress_save, is_streaming_save, looks_like_json
from .xxtea import decrypt_meta, encrypt_meta

# Non-error debug stays behind this flag.
DEBUG_ENABLED = False


# Function: _strip_json_terminator
# Purpose: Drop the trailing 0x00 libNOM writes after the JSON text.
def _strip_json_terminator(blob: bytes) -> bytes:
    # CreateData appends a single NUL; keep any interior NULs untouched.
    if blob.endswith(bytes([BINARY_TERMINATOR])):
        return blob[:-1]
    return blob


# Function: _ensure_json_terminator
# Purpose: Re-append the trailing 0x00 so a re-encoded file matches libNOM.
def _ensure_json_terminator(blob: bytes) -> bytes:
    # Do not double-append if the caller already included the terminator.
    if blob.endswith(bytes([BINARY_TERMINATOR])):
        return blob
    return blob + bytes([BINARY_TERMINATOR])


# Function: decrypt_bytes
# Purpose: Decode a data .hg (LZ4) or a meta mf_*.hg (XXTEA) buffer.
def decrypt_bytes(
    blob: bytes,
    kind: str,
    hint_slot: int | None = None,
    is_account: bool = False,
    source_name: str = "",
) -> bytes:
    # Auto-detect kind from the filename when the caller did not force one.
    if kind == "auto":
        kind = guess_kind_from_filename(source_name) if source_name else "data"
        # A nameless buffer that starts with JSON or the streaming magic is data.
        if kind == "unknown":
            kind = "meta" if not (is_streaming_save(blob) or looks_like_json(blob)) else "data"
    # Meta path is the XXTEA cipher; data path is LZ4 / identity.
    if kind == "meta":
        # Fall back to filename slot guess, then to PlayerState1 (slot 2).
        slot = hint_slot if hint_slot is not None else (
            guess_slot_from_filename(source_name) if source_name else 2
        )
        # Account meta only tries UserSettings / AccountData.
        account = is_account or (bool(source_name) and is_account_filename(source_name))
        # decrypt_meta returns (plaintext, winning_slot); we only need bytes here.
        plain, _winning_slot = decrypt_meta(blob, slot, is_account=account)
        return plain
    if kind == "data":
        # Decompress streaming chunks, then drop the trailing JSON NUL.
        return _strip_json_terminator(decompress_save(blob))
    # Anything else is a caller error, not a silent no-op.
    raise ValueError(f"{DEBUG_PREFIX} decrypt_bytes: unknown kind {kind!r}")


# Function: encrypt_bytes
# Purpose: Encode JSON (or already-plain meta) back to on-disk Steam bytes.
def encrypt_bytes(
    blob: bytes,
    kind: str,
    hint_slot: int | None = None,
    is_account: bool = False,
    source_name: str = "",
    compress: bool = True,
) -> bytes:
    # Same auto-detect rule as decrypt_bytes.
    if kind == "auto":
        kind = guess_kind_from_filename(source_name) if source_name else "data"
        if kind == "unknown":
            kind = "meta" if not looks_like_json(blob) else "data"
    if kind == "meta":
        # Encrypt requires an explicit slot; guessing from a .json name will fail.
        slot = hint_slot if hint_slot is not None else (
            guess_slot_from_filename(source_name) if source_name else None
        )
        if slot is None:
            raise ValueError(f"{DEBUG_PREFIX} encrypt_bytes: --slot is required for meta encrypt")
        return encrypt_meta(blob, slot)
    if kind == "data":
        # Account data is stored uncompressed in libNOM (no streaming header).
        account = is_account or (bool(source_name) and is_account_filename(source_name))
        # Restore the trailing NUL that CreateData writes.
        terminated = _ensure_json_terminator(blob)
        # Skip LZ4 when the caller asked for identity or this is account data.
        if not compress or account:
            return terminated
        return compress_save(terminated)
    raise ValueError(f"{DEBUG_PREFIX} encrypt_bytes: unknown kind {kind!r}")


# Function: decrypt_file
# Purpose: Read a path and decrypt it using filename-based defaults.
def decrypt_file(path: str, kind: str = "auto", hint_slot: int | None = None) -> bytes:
    # Binary read; these files are not text even when they contain JSON.
    with open(path, "rb") as handle:
        blob = handle.read()
    # Delegate to the buffer API so CLI and library share one code path.
    return decrypt_bytes(blob, kind, hint_slot=hint_slot, source_name=path)


# Function: encrypt_file
# Purpose: Read a path and encrypt it using filename-based defaults.
def encrypt_file(
    path: str,
    kind: str = "auto",
    hint_slot: int | None = None,
    compress: bool = True,
) -> bytes:
    # Binary read of the source (JSON text or plaintext meta).
    with open(path, "rb") as handle:
        blob = handle.read()
    # Delegate to the buffer API.
    return encrypt_bytes(blob, kind, hint_slot=hint_slot, source_name=path, compress=compress)
