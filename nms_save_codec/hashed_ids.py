# File: hashed_ids.py
# Purpose: Convert raw hashed technology IDs (^<raw bytes>#) to the escaped text form (^<HEX>#) and back.
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\hashed_ids.py

from __future__ import annotations

import os

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/hashed_ids]"
# Non-error debug stays behind this flag.
DEBUG_ENABLED = False

# The NUL-separated table of hashed technology IDs shipped with the package.
BUNDLED_RESOURCE_FILE = "hashed_technology.bin"
# Prefix and suffix Hello Games wraps around every hashed ID.
ID_PREFIX = b"^"
ID_SUFFIX = b"#"


# Function: _load_binary_mapping
# Purpose: Build the (Raw, Escaped) pair list from the bundled hashed_technology.bin.
def _load_binary_mapping() -> list:
    # Resolve the resource relative to this module so any working directory works.
    base = os.path.dirname(os.path.abspath(__file__))
    # Full path to the bundled resource file.
    path = os.path.join(base, BUNDLED_RESOURCE_FILE)
    # Read the whole resource as bytes; it is binary data, not text.
    with open(path, "rb") as handle:
        # One blob of NUL-separated entries.
        resource = handle.read()
    # Collect the (Raw, Escaped) pairs in file order, like libNOM.io CreateBinaryMapping.
    pairs = []
    # Every NUL-separated run is one technology ID.
    for entry in resource.split(b"\x00"):
        # Skip empty runs produced by leading/trailing separators.
        if not entry:
            # Empty entry means no ID bytes, so nothing to register.
            continue
        # Raw form is the prefix + original bytes + suffix, as found inside save JSON.
        raw = ID_PREFIX + entry + ID_SUFFIX
        # Escaped form is prefix + uppercase hex + suffix, the JSON-safe stand-in.
        escaped = ID_PREFIX + entry.hex().upper().encode("ascii") + ID_SUFFIX
        # Register the pair for both directions.
        pairs.append((raw, escaped))
    # Hand the ordered pair list to the caller.
    return pairs


# Module-level pair list, built once per process (mirrors libNOM.io's lazy static).
BINARY_MAPPING = _load_binary_mapping()


# Function: escape_hashed_ids
# Purpose: Replace raw hashed IDs with the escaped text form so JSON parsing is safe.
def escape_hashed_ids(blob: bytes) -> bytes:
    # Work on the caller's bytes without mutating them.
    result = blob
    # Sequential replacement in table order, exactly like libNOM.io GetJson.
    for raw, escaped in BINARY_MAPPING:
        # Raw (^<bytes>#) becomes escaped (^<HEX>#).
        result = result.replace(raw, escaped)
    # Return the JSON-safe bytes.
    return result


# Function: restore_hashed_ids
# Purpose: Replace escaped hashed IDs with the raw on-disk form before compression.
def restore_hashed_ids(blob: bytes) -> bytes:
    # Work on the caller's bytes without mutating them.
    result = blob
    # Sequential replacement in table order, exactly like libNOM.io CreateData.
    for raw, escaped in BINARY_MAPPING:
        # Escaped (^<HEX>#) becomes raw (^<bytes>#) again.
        result = result.replace(escaped, raw)
    # Return the on-disk form.
    return result
