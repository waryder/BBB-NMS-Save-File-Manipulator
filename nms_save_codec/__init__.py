# File: __init__.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\__init__.py
# Purpose: Public package surface for the first-cut Steam/GOG NMS save codec.

from .codec import decrypt_bytes, decrypt_file, encrypt_bytes, encrypt_file
from .constants import META_HEADER, SAVE_STREAMING_HEADER
from .hashed_ids import escape_hashed_ids, restore_hashed_ids
from .mapping import KeyMapping
from .platforms import PLATFORMS, get_platform
from .save_file import NmsSaveFile
from .slots import guess_kind_from_filename, guess_slot_from_filename
from .streaming import compress_save, decompress_save
from .xxtea import decrypt_meta, encrypt_meta

# Re-export the functions the CLI uses plus the class the manipulator GUI will use.
__all__ = [
    "META_HEADER",
    "SAVE_STREAMING_HEADER",
    "PLATFORMS",
    "KeyMapping",
    "NmsSaveFile",
    "compress_save",
    "decompress_save",
    "decrypt_bytes",
    "decrypt_file",
    "decrypt_meta",
    "encrypt_bytes",
    "encrypt_file",
    "encrypt_meta",
    "escape_hashed_ids",
    "get_platform",
    "guess_kind_from_filename",
    "guess_slot_from_filename",
    "restore_hashed_ids",
]
