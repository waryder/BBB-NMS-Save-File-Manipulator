# File: streaming.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\streaming.py
# Purpose: LZ4 chunked encode/decode for Steam/GOG save??.hg payloads.

from __future__ import annotations

import struct

from .constants import (
    DEBUG_PREFIX,
    SAVE_STREAMING_CHUNK_LENGTH_MAX,
    SAVE_STREAMING_HEADER,
    SAVE_STREAMING_HEADER_LENGTH,
)

# Non-error debug stays behind this flag.
DEBUG_ENABLED = False


# Function: _require_lz4
# Purpose: Import lz4.block lazily and explain how to install it if missing.
def _require_lz4():
    # Import inside the helper so the package can load without lz4 for meta-only use.
    try:
        # lz4.block is the raw-block API that matches K4os.Compression.LZ4.
        from lz4 import block as lz4_block
    except ImportError as exc:
        # Tell the user the exact extra they need instead of a bare ImportError.
        raise ImportError(
            f"{DEBUG_PREFIX} _require_lz4: install the lz4 package (pip install lz4)"
        ) from exc
    # Hand the module back to the caller.
    return lz4_block


# Function: is_streaming_save
# Purpose: True when the buffer starts with the Frontiers+ streaming magic.
def is_streaming_save(blob: bytes) -> bool:
    # Need at least the 4-byte magic to decide.
    if len(blob) < 4:
        return False
    # Compare against E5 A1 ED FE.
    return blob.startswith(SAVE_STREAMING_HEADER)


# Function: looks_like_json
# Purpose: Cheap check for uncompressed account / pre-Frontiers JSON.
def looks_like_json(blob: bytes) -> bool:
    # Skip a UTF-8 BOM if one is present.
    sample = blob.lstrip(b"\xef\xbb\xbf")
    # Real NMS JSON always opens with '{' (often '{"F2P":' or '{"Version":').
    return bool(sample) and sample[:1] == b"{"


# Function: _decode_one_chunk
# Purpose: Parse one 16-byte header plus its compressed payload.
def _decode_one_chunk(blob: bytes, offset: int) -> tuple[bytes, int]:
    # Need a full 16-byte header before we can read sizes.
    if offset + SAVE_STREAMING_HEADER_LENGTH > len(blob):
        raise ValueError(f"{DEBUG_PREFIX} _decode_one_chunk: truncated header at {offset}")
    # First four bytes of every chunk must be the streaming magic.
    magic = blob[offset : offset + 4]
    if magic != SAVE_STREAMING_HEADER:
        raise ValueError(f"{DEBUG_PREFIX} _decode_one_chunk: bad magic at {offset}: {magic!r}")
    # Live 2004 files store [compressed, decompressed, 0] after the magic.
    _magic_u32, size_compressed, size_decompressed, _reserved = struct.unpack_from(
        "<IIII", blob, offset
    )
    # Advance past the 16-byte header.
    data_start = offset + SAVE_STREAMING_HEADER_LENGTH
    # The compressed payload must fit in the remaining buffer.
    data_end = data_start + size_compressed
    if data_end > len(blob):
        raise ValueError(f"{DEBUG_PREFIX} _decode_one_chunk: truncated payload at {offset}")
    # Hand the raw LZ4 block to lz4.block (no frame wrapper, no stored size).
    lz4_block = _require_lz4()
    # uncompressed_size is the third header field on disk (524288 for full chunks).
    plain = lz4_block.decompress(blob[data_start:data_end], uncompressed_size=size_decompressed)
    # Return the chunk text and the next offset.
    return plain, data_end


# Function: decompress_save
# Purpose: Walk every streaming chunk and concatenate the JSON bytes.
def decompress_save(blob: bytes) -> bytes:
    # Account data and pre-Frontiers saves have no streaming header.
    if not is_streaming_save(blob):
        return blob
    # Accumulate decompressed chunk bytes in order.
    pieces: list[bytes] = []
    # Start at the first byte of the file.
    offset = 0
    # Walk until the buffer is consumed.
    while offset < len(blob):
        # Decode one chunk and learn where the next one starts.
        piece, offset = _decode_one_chunk(blob, offset)
        # Keep the piece for the final join.
        pieces.append(piece)
    # Join is cheaper than repeated bytes concatenation.
    return b"".join(pieces)


# Function: _encode_one_chunk
# Purpose: LZ4-compress one source slice and prefix the 16-byte header.
def _encode_one_chunk(source: bytes) -> bytes:
    # Pull the raw-block compressor.
    lz4_block = _require_lz4()
    # store_size=False matches K4os (no 4-byte length prefix inside the block).
    compressed = lz4_block.compress(source, store_size=False)
    # Live files write [compressed_len, decompressed_len, 0] after the magic.
    header = SAVE_STREAMING_HEADER + struct.pack("<III", len(compressed), len(source), 0)
    # Header plus compressed bytes is one on-disk chunk.
    return header + compressed


# Function: compress_save
# Purpose: Split JSON bytes into 0x80000 chunks and LZ4-encode each one.
def compress_save(plain: bytes) -> bytes:
    # Empty input stays empty; nothing to chunk.
    if not plain:
        return b""
    # Collect encoded chunks for a single join at the end.
    pieces: list[bytes] = []
    # Walk the plaintext in SAVE_STREAMING_CHUNK_LENGTH_MAX slices.
    position = 0
    # Loop until every plaintext byte has been consumed.
    while position < len(plain):
        # Last chunk may be shorter than the 512 KiB maximum.
        end = min(position + SAVE_STREAMING_CHUNK_LENGTH_MAX, len(plain))
        # Encode this slice as one streaming chunk.
        pieces.append(_encode_one_chunk(plain[position:end]))
        # Advance to the next slice.
        position = end
    # Concatenate every chunk into the on-disk .hg payload.
    return b"".join(pieces)
