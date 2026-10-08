# File: meta_info.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\meta_info.py
# Purpose: READ-ONLY helpers that scan a Steam/GOG save folder, group save*.hg files into
#          game slots (Auto + Manual), and read save name / summary / timestamp / game mode
#          out of each file's decrypted mf_ meta sibling. Never writes anything.

from __future__ import annotations

import os
import re
import struct

from .slots import guess_slot_from_filename
from .xxtea import decrypt_meta

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/meta_info]"
# Non-error debug stays behind this flag.
DEBUG_ENABLED = False

# Decrypted Steam meta offsets (libNOM.io PlatformSteam.cs / Platform.cs / Platform_Write.cs).
META_OFFSET_GAME_MODE = 0x48
# Save name: 128 bytes, NUL-terminated UTF-8 (present since Waypoint).
META_OFFSET_SAVE_NAME = 0x58
# Save summary: 128 bytes, NUL-terminated UTF-8 (present since Waypoint).
META_OFFSET_SAVE_SUMMARY = 0xD8
# Length of each text field in the meta.
META_TEXT_LENGTH = 128
# Unix timestamp (u32) of the last write (present since Worlds Part I).
META_OFFSET_TIMESTAMP = 0x164
# Shortest meta that carries the name/summary fields (Waypoint = 0x168).
META_MIN_LENGTH_TEXT = 0x168
# Shortest meta that carries the timestamp field (Worlds Part I = 0x180).
META_MIN_LENGTH_TIMESTAMP = 0x180

# Data files only: save.hg, save2.hg ... save30.hg (no mf_ prefix).
_DATA_NAME_RE = re.compile(r"^save(\d*)\.hg$", re.IGNORECASE)


# Function: _read_cstring
# Purpose: Decode a fixed-size, NUL-terminated UTF-8 text field from the meta buffer.
def _read_cstring(buffer: bytes, offset: int) -> str:
    # Slice exactly the fixed field width.
    raw = buffer[offset:offset + META_TEXT_LENGTH]
    # Everything after the first NUL is padding.
    raw = raw.split(b"\x00", 1)[0]
    # Replace bad bytes rather than failing the whole dialog.
    return raw.decode("utf-8", "replace")


# Function: read_meta_info
# Purpose: Decrypt one mf_ file (read-only) and return its name/summary/timestamp/game mode.
def read_meta_info(meta_path: str, data_file_name: str) -> dict:
    # Read the small encrypted meta file; "rb" never modifies it.
    with open(meta_path, "rb") as handle:
        encrypted = handle.read()
    # The data file name tells decrypt_meta which slot key to try first.
    plain, _slot = decrypt_meta(encrypted, guess_slot_from_filename(data_file_name), is_account=False)
    # Older meta formats lack the text fields; report blanks instead of garbage.
    has_text = len(plain) >= META_MIN_LENGTH_TEXT
    # Timestamp only exists from Worlds Part I onward.
    has_time = len(plain) >= META_MIN_LENGTH_TIMESTAMP
    # Assemble the summary dict the dialog consumes.
    return {
        "name": _read_cstring(plain, META_OFFSET_SAVE_NAME) if has_text else "",
        "summary": _read_cstring(plain, META_OFFSET_SAVE_SUMMARY) if has_text else "",
        "timestamp": struct.unpack_from("<I", plain, META_OFFSET_TIMESTAMP)[0] if has_time else 0,
        "game_mode": struct.unpack_from("<H", plain, META_OFFSET_GAME_MODE)[0],
    }


# Function: _describe_data_file
# Purpose: Build the per-file record (slot number, Auto/Manual, meta info or error) for one save*.hg.
def _describe_data_file(folder: str, file_name: str) -> dict:
    # metaIndex: save.hg = 2, saveN.hg = N + 1 (slots.py).
    meta_index = guess_slot_from_filename(file_name)
    # Collection index 0,1 = slot 1; 2,3 = slot 2; even = Auto, odd = Manual (libNOM Container.cs).
    collection_index = meta_index - 2
    # Start the record with what the file name alone tells us.
    record = {
        "slot": collection_index // 2 + 1,
        "save_type": "Auto" if collection_index % 2 == 0 else "Manual",
        "file_name": file_name,
        "data_path": os.path.join(folder, file_name),
        "meta": None,
        "error": None,
    }
    # Try to read the mf_ sibling; a failure is recorded, not raised.
    try:
        record["meta"] = read_meta_info(os.path.join(folder, "mf_" + file_name), file_name)
    except Exception as exc:
        record["error"] = str(exc)
    # Hand the finished record back.
    return record


# Function: list_save_slots
# Purpose: Scan a save folder (read-only) and return slots sorted by number, each with its files.
def list_save_slots(folder: str) -> list[dict]:
    # Group file records by slot number.
    slots = {}
    # Only plain save*.hg data files participate; mf_ files are read via their data sibling.
    for file_name in sorted(os.listdir(folder)):
        # Skip anything that is not a data save file (accountdata, mf_, backups, json exports).
        if not _DATA_NAME_RE.match(file_name):
            continue
        # Describe the file and drop it into its slot's list.
        record = _describe_data_file(folder, file_name)
        slots.setdefault(record["slot"], []).append(record)
    # Optional trace of what was found.
    if DEBUG_ENABLED:
        print(f"{DEBUG_PREFIX} list_save_slots: {len(slots)} slots in {folder}")
    # Auto before Manual inside each slot, slots in ascending order.
    return [
        {"slot": number, "files": sorted(files, key=lambda r: r["save_type"] != "Auto")}
        for number, files in sorted(slots.items())
    ]
