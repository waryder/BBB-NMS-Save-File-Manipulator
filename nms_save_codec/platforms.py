# File: platforms.py
# Purpose: Platform seam for the NMS save codec. Steam and GOG are implemented; others are stubs.
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\platforms.py

from __future__ import annotations

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/platforms]"
# Non-error debug stays behind this flag.
DEBUG_ENABLED = False


# Class: PlatformProfile
# Purpose: Holds exactly the facts that differ between save platforms.
class PlatformProfile:
    # Function: __init__
    # Purpose: Store the per-platform facts the codec needs.
    def __init__(self, name: str, data_pattern: str, meta_prefix: str, meta_encrypted: bool, hashed_ids: bool):
        # Human-readable platform name used in messages.
        self.name = name
        # Data file naming pattern (Steam/GOG: save.hg, save2.hg, accountdata.hg).
        self.data_pattern = data_pattern
        # Meta file naming prefix (Steam/GOG: mf_save.hg).
        self.meta_prefix = meta_prefix
        # Whether meta files are XXTEA encrypted (Steam/GOG: yes; Switch: no).
        self.meta_encrypted = meta_encrypted
        # Whether data files contain hashed technology IDs needing escape handling.
        self.hashed_ids = hashed_ids


# Implemented profiles. GOG inherits the Steam format wholesale; only save location differs
# (GOG saves live in DefaultUser instead of st_<steamid3>), which does not affect a
# file-based API because the caller supplies the path.
PLATFORMS = {
    # Steam: .hg data files with LZ4 streaming chunks and XXTEA-encrypted mf_ meta files.
    "steam": PlatformProfile("Steam", "save*.hg", "mf_", True, True),
    # GOG: byte-identical format to Steam (libNOM.io PlatformGog inherits PlatformSteam).
    "gog": PlatformProfile("GOG", "save*.hg", "mf_", True, True),
}

# Platforms that libNOM.io supports but this package does not yet, listed with the reason.
# Adding one later means adding a PlatformProfile plus its read/write specifics - the
# NmsSaveFile class already routes every platform decision through this registry.
STUB_PLATFORMS = {
    # Switch: unencrypted, but different file names (savedataNN.hg / manifestNN.hg) and meta layout.
    "switch": "Switch is not implemented yet: needs savedataNN.hg/manifestNN.hg meta-layout handling and test fixtures.",
    # PlayStation: saves must be exported (memory.dat via USB or SaveWizard) before any tool can read them.
    "playstation": "PlayStation is not implemented yet: requires memory.dat / SaveWizard export fixtures to build against.",
    # Microsoft: saves live inside Windows package containers with a container index to maintain.
    "microsoft": "Microsoft (Game Pass) is not implemented yet: requires WNC container-index handling and test fixtures.",
}


# Function: get_platform
# Purpose: Resolve a platform name to its profile, with a clear error for stubs and typos.
def get_platform(name: str) -> PlatformProfile:
    # Case-insensitive lookup keeps user input forgiving.
    key = (name or "steam").lower()
    # Implemented platforms return their profile directly.
    if key in PLATFORMS:
        # Implemented: hand back the profile.
        return PLATFORMS[key]
    # Stub platforms explain what is missing instead of pretending to work.
    if key in STUB_PLATFORMS:
        # Loud, actionable failure - never a silent no-op.
        raise NotImplementedError(f"{DEBUG_PREFIX} get_platform: {STUB_PLATFORMS[key]}")
    # Anything else is a caller typo, so list the valid names.
    known = ", ".join(list(PLATFORMS) + list(STUB_PLATFORMS))
    # Raise with the valid options spelled out.
    raise ValueError(f"{DEBUG_PREFIX} get_platform: unknown platform {name!r}; valid: {known}")
