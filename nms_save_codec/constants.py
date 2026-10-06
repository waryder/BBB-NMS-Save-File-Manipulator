# File: constants.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\constants.py
# Purpose: Steam/GOG NMS save-codec constants ported from libNOM.io (GPLv3).

# Project/file debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/constants]"

# ASCII key material from PlatformSteam.META_ENCRYPTION_KEY ("NAESEVADNAYRTNRG").
META_KEY_ASCII = b"NAESEVADNAYRTNRG"

# Success marker written as dword 0 of a valid decrypted Steam/GOG meta file.
META_HEADER = 0xEEEEEEBE

# XXTEA delta constant (same value TEA uses).
XXTEA_DELTA = 0x9E3779B9

# XXTEA decrypt decrement; equals -DELTA modulo 2^32.
XXTEA_DECREMENT = 0x61C88647

# Constants used when mixing the first key dword with the storage slot.
SLOT_KEY_XOR = 0x1422CB8C
SLOT_KEY_ROTATE = 13
SLOT_KEY_MUL = 5
SLOT_KEY_ADD = 0xE6546B64

# Known Steam/GOG meta file lengths in bytes (vanilla / Waypoint / Worlds I / Worlds II).
META_LENGTH_VANILLA = 0x68
META_LENGTH_WAYPOINT = 0x168
META_LENGTH_WORLDS_I = 0x180
META_LENGTH_WORLDS_II = 0x1B0
KNOWN_META_LENGTHS = (
    META_LENGTH_VANILLA,
    META_LENGTH_WAYPOINT,
    META_LENGTH_WORLDS_I,
    META_LENGTH_WORLDS_II,
)

# XXTEA round counts: 8 for vanilla-sized meta, 6 for later formats.
XXTEA_ROUNDS_VANILLA = 8
XXTEA_ROUNDS_LATER = 6

# Save-data streaming magic: bytes E5 A1 ED FE (little-endian 0xFEEDA1E5).
SAVE_STREAMING_HEADER = b"\xE5\xA1\xED\xFE"

# Full on-disk chunk header is 16 bytes: magic + 3 little-endian uint32 fields.
SAVE_STREAMING_HEADER_LENGTH = 0x10

# Maximum uncompressed bytes per LZ4 chunk (libNOM SAVE_STREAMING_CHUNK_LENGTH_MAX).
SAVE_STREAMING_CHUNK_LENGTH_MAX = 0x80000

# JSON / account payloads are terminated with a single 0x00 byte in libNOM CreateData.
BINARY_TERMINATOR = 0

# StoragePersistentSlotEnum values from libNOM.io (cTkStoragePersistent::Slot).
SLOT_USER_SETTINGS = 0
SLOT_ACCOUNT_DATA = 1
SLOT_PLAYER_STATE_1 = 2
SLOT_PLAYER_STATE_30 = 31

# metaIndex of the first save file (save.hg). Account uses 0; 1 is unused.
OFFSET_INDEX = 2
