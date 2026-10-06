# File: slots.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\slots.py
# Purpose: Map Steam save / mf_ filenames onto StoragePersistentSlotEnum values.

from __future__ import annotations

import os
import re

from .constants import DEBUG_PREFIX, OFFSET_INDEX, SLOT_ACCOUNT_DATA

# Non-error debug stays behind this flag.
DEBUG_ENABLED = False

# save.hg / save2.hg / mf_save10.hg — digits are optional (save.hg has none).
_SAVE_NAME_RE = re.compile(r"^(?:mf_)?save(\d*)\.hg$", re.IGNORECASE)
# accountdata.hg / mf_accountdata.hg
_ACCOUNT_NAME_RE = re.compile(r"^(?:mf_)?accountdata\.hg$", re.IGNORECASE)


# Function: strip_mf_prefix
# Purpose: Treat mf_save2.hg the same as save2.hg for slot guessing.
def strip_mf_prefix(filename: str) -> str:
    # Compare case-insensitively so MF_SAVE2.HG still matches.
    if filename.lower().startswith("mf_"):
        return filename[3:]
    return filename


# Function: is_meta_filename
# Purpose: True when the name is a Steam meta/manifest file (mf_*).
def is_meta_filename(filename: str) -> bool:
    # Steam meta files are the mf_ siblings of save / accountdata.
    return filename.lower().startswith("mf_")


# Function: is_account_filename
# Purpose: True for accountdata.hg or mf_accountdata.hg.
def is_account_filename(filename: str) -> bool:
    # Account uses a different key family than PlayerStateN.
    return _ACCOUNT_NAME_RE.match(os.path.basename(filename)) is not None


# Function: guess_slot_from_filename
# Purpose: Return the PersistentStorageSlot enum ordinal for a Steam filename.
def guess_slot_from_filename(filename: str) -> int:
    # Only the basename participates in the mapping.
    name = os.path.basename(filename)
    # Account files always use slot AccountData (1).
    if is_account_filename(name):
        return SLOT_ACCOUNT_DATA
    # save.hg / saveN.hg / mf_saveN.hg share the same slot formula.
    match = _SAVE_NAME_RE.match(name)
    if match is None:
        raise ValueError(f"{DEBUG_PREFIX} guess_slot_from_filename: unrecognized name {name!r}")
    # The optional digit group is empty for save.hg.
    digits = match.group(1)
    # CreateContainer: save.hg is metaIndex 2; saveN.hg is metaIndex N+1.
    if digits == "":
        meta_index = OFFSET_INDEX
    else:
        meta_index = int(digits) + 1
    # PersistentStorageSlot = MetaIndex for every save (Container.cs).
    return meta_index


# Function: guess_kind_from_filename
# Purpose: Decide whether a path is meta, data, or unknown.
def guess_kind_from_filename(filename: str) -> str:
    # Basename only; directories do not affect kind.
    name = os.path.basename(filename)
    # mf_* is always the XXTEA meta sibling.
    if is_meta_filename(name):
        return "meta"
    # accountdata.hg and save*.hg are the LZ4 / JSON data files.
    if is_account_filename(name) or _SAVE_NAME_RE.match(name):
        return "data"
    # Caller must pass --kind when the name is not a known Steam file.
    return "unknown"
