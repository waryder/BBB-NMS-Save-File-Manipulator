# File: xxtea.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\xxtea.py
# Purpose: Steam/GOG meta-file XXTEA (encrypt + decrypt) ported from libNOM.io.

from __future__ import annotations

import struct

from .constants import (
    DEBUG_PREFIX,
    KNOWN_META_LENGTHS,
    META_HEADER,
    META_KEY_ASCII,
    META_LENGTH_VANILLA,
    SLOT_ACCOUNT_DATA,
    SLOT_KEY_ADD,
    SLOT_KEY_MUL,
    SLOT_KEY_ROTATE,
    SLOT_KEY_XOR,
    SLOT_PLAYER_STATE_1,
    SLOT_PLAYER_STATE_30,
    SLOT_USER_SETTINGS,
    XXTEA_DECREMENT,
    XXTEA_DELTA,
    XXTEA_ROUNDS_LATER,
    XXTEA_ROUNDS_VANILLA,
)

# Class-level debug prefix required by Bill's logging rules.
# Non-error debug stays behind this flag; errors always print.
DEBUG_ENABLED = False


# Function: _mask32
# Purpose: Keep every mix step inside unsigned 32-bit wrap, matching C# uint.
def _mask32(value: int) -> int:
    # C# uint arithmetic wraps at 2^32; Python ints do not.
    return value & 0xFFFFFFFF


# Function: _rotate_left
# Purpose: Port of IntegerExtensions.RotateLeft used in the slot key mix.
def _rotate_left(value: int, bits: int) -> int:
    # Shift the low bits off the top and wrap them onto the bottom.
    value = _mask32(value)
    # 32 - bits is the complementary right shift.
    return _mask32((value << bits) | (value >> (32 - bits)))


# Function: _base_key_dwords
# Purpose: Interpret META_KEY_ASCII as four little-endian uint32 words.
def _base_key_dwords() -> tuple[int, int, int, int]:
    # Exactly how PlatformSteam casts "NAESEVADNAYRTNRG" to uint[].
    return struct.unpack("<IIII", META_KEY_ASCII)


# Function: build_slot_key
# Purpose: Replace dword 0 of the base key with the per-slot mixed value.
def build_slot_key(storage_slot: int) -> tuple[int, int, int, int]:
    # Pull the three unchanging dwords from the ASCII key material.
    _dword0, dword1, dword2, dword3 = _base_key_dwords()
    # Mix the enum ordinal the same way DecryptMetaStorageEntry does.
    mixed = _rotate_left(storage_slot ^ SLOT_KEY_XOR, SLOT_KEY_ROTATE)
    # Multiply and add with 32-bit wrap to finish dword 0.
    dword0 = _mask32(mixed * SLOT_KEY_MUL + SLOT_KEY_ADD)
    # Return a 4-word key ready for XXTEA.
    return (dword0, dword1, dword2, dword3)


# Function: rounds_for_meta_length
# Purpose: Choose 8 rounds (vanilla) or 6 rounds (Waypoint+).
def rounds_for_meta_length(length_bytes: int) -> int:
    # Vanilla meta is 0x68 bytes and uses the original 8-round count.
    if length_bytes == META_LENGTH_VANILLA:
        return XXTEA_ROUNDS_VANILLA
    # Every later known length uses 6 rounds.
    return XXTEA_ROUNDS_LATER


# Function: bytes_to_uints
# Purpose: Cast a little-endian byte buffer to a mutable list of uint32.
def bytes_to_uints(blob: bytes) -> list[int]:
    # Meta files are always a whole number of 32-bit words.
    if len(blob) % 4 != 0:
        # Refuse a buffer that cannot be a Steam meta payload.
        raise ValueError(f"{DEBUG_PREFIX} bytes_to_uints: length {len(blob)} is not a multiple of 4")
    # '<' is little-endian, matching C# BitConverter / Span.Cast on x86.
    count = len(blob) // 4
    # Unpack into a list so later in-place XXTEA can mutate it.
    return list(struct.unpack("<" + "I" * count, blob))


# Function: uints_to_bytes
# Purpose: Pack a uint32 list back to little-endian bytes.
def uints_to_bytes(words: list[int]) -> bytes:
    # Mask each word so pack never sees a Python int larger than 32 bits.
    masked = [_mask32(word) for word in words]
    # Rebuild the exact on-disk / in-memory byte layout.
    return struct.pack("<" + "I" * len(masked), *masked)


# Function: encrypt_words
# Purpose: In-place XXTEA encrypt matching PlatformSteam_Write.EncryptMeta.
def encrypt_words(words: list[int], key: tuple[int, int, int, int], rounds: int) -> list[int]:
    # Work on a copy so the caller can keep the plaintext.
    result = list(words)
    # Encrypt starts with current = 0 and hash = 0.
    current = 0
    # Hash accumulates DELTA once per outer round.
    hash_value = 0
    # lastIndex is the last uint32 in the buffer.
    last_index = len(result) - 1
    # Outer loop is the XXTEA round count (6 or 8).
    for _round in range(rounds):
        # Add the TEA delta with 32-bit wrap.
        hash_value = _mask32(hash_value + XXTEA_DELTA)
        # keyIndex selects which of the 4 key words this round uses first.
        key_index = (hash_value >> 2) & 3
        # Walk forward from word 0 through last_index - 1.
        for j in range(last_index):
            # nxt is the word after the one being updated.
            nxt = result[j + 1]
            # Mix uses the same four sub-expressions as the C# comments.
            mixed = _mask32(
                (((nxt >> 3) ^ _mask32(current << 4)) + ((nxt * 4) ^ (current >> 5)))
                ^ ((current ^ key[(j & 3) ^ key_index]) + (nxt ^ hash_value))
            )
            # Add the mix into the current word.
            result[j] = _mask32(result[j] + mixed)
            # current tracks the word just written.
            current = result[j]
        # The last word wraps against result[0].
        mixed_last = _mask32(
            (((result[0] >> 3) ^ _mask32(current << 4)) + ((result[0] * 4) ^ (current >> 5)))
            ^ ((current ^ key[(last_index & 3) ^ key_index]) + (result[0] ^ hash_value))
        )
        # Store the wrapped last word.
        result[last_index] = _mask32(result[last_index] + mixed_last)
        # current becomes that last word for the next outer round.
        current = result[last_index]
    # Return the encrypted word list.
    return result


# Function: decrypt_words
# Purpose: In-place XXTEA decrypt matching DecryptMetaStorageEntry.
def decrypt_words(words: list[int], key: tuple[int, int, int, int], rounds: int) -> list[int]:
    # Deep-copy so a failed slot guess does not poison the next guess.
    result = list(words)
    # Preload hash = rounds * DELTA, as the C# loop does before decrypting.
    hash_value = 0
    # This preload is written as a loop in C# to land on 0xF1BBCDC8 for 8 rounds.
    for _preload in range(rounds):
        hash_value = _mask32(hash_value + XXTEA_DELTA)
    # lastIndex is the last uint32 in the buffer.
    last_index = len(result) - 1
    # Outer loop runs the same number of rounds as encrypt.
    for _round in range(rounds):
        # current starts at result[0] for the backward pass.
        current = result[0]
        # keyIndex is derived from the current hash, same as encrypt.
        key_index = (hash_value >> 2) & 3
        # Walk backward from last_index down to 1.
        for j in range(last_index, 0, -1):
            # prev is the word before the one being updated.
            prev = result[j - 1]
            # Inverse of the encrypt mix (subtract instead of add).
            mixed = _mask32(
                (((current >> 3) ^ _mask32(prev << 4)) + ((current * 4) ^ (prev >> 5)))
                ^ ((prev ^ key[(j & 3) ^ key_index]) + (current ^ hash_value))
            )
            # Subtract the mix from the current word.
            result[j] = _mask32(result[j] - mixed)
            # current tracks the word just written.
            current = result[j]
        # Word 0 wraps against the last word.
        mixed_first = _mask32(
            (((current >> 3) ^ _mask32(result[last_index] << 4)) + ((current * 4) ^ (result[last_index] >> 5)))
            ^ ((result[last_index] ^ key[key_index]) + (current ^ hash_value))
        )
        # Store the wrapped first word.
        result[0] = _mask32(result[0] - mixed_first)
        # Decrement hash by DELTA (add 0x61C88647) for the next round.
        hash_value = _mask32(hash_value + XXTEA_DECREMENT)
    # Return the decrypted word list.
    return result


# Function: _slot_try_order
# Purpose: Hinted slot first, then the rest of the matching family (account vs save).
def _slot_try_order(hint_slot: int, is_account: bool) -> list[int]:
    # Account files only try UserSettings / AccountData.
    if is_account:
        family = [SLOT_USER_SETTINGS, SLOT_ACCOUNT_DATA]
    else:
        # Save files try PlayerState1 through PlayerState30.
        family = list(range(SLOT_PLAYER_STATE_1, SLOT_PLAYER_STATE_30 + 1))
    # Put the hinted slot first when it belongs to that family.
    ordered = [hint_slot] if hint_slot in family else []
    # Then append every other family member, preserving enum order.
    ordered.extend(slot for slot in family if slot != hint_slot)
    # Return the try-order used by DecryptMeta.
    return ordered


# Function: decrypt_meta
# Purpose: Try slots until dword 0 equals META_HEADER (0xEEEEEEBE).
def decrypt_meta(blob: bytes, hint_slot: int, is_account: bool = False) -> tuple[bytes, int]:
    # Unknown lengths skip the cipher in C# and just recast the bytes.
    if len(blob) not in KNOWN_META_LENGTHS:
        # Surface that we did not touch an unrecognized buffer.
        if DEBUG_ENABLED:
            print(f"{DEBUG_PREFIX} decrypt_meta: unknown length {len(blob)}, returning raw")
        return blob, hint_slot
    # Cast once; every slot guess decrypts a fresh copy of these words.
    words = bytes_to_uints(blob)
    # Round count is a function of the on-disk length.
    rounds = rounds_for_meta_length(len(blob))
    # Walk the same try-order libNOM uses for hand-moved files.
    for slot in _slot_try_order(hint_slot, is_account):
        # Build the per-slot 4-word key.
        key = build_slot_key(slot)
        # Run the backward XXTEA pass.
        decrypted = decrypt_words(words, key, rounds)
        # Accept the first result whose header matches 0xEEEEEEBE.
        if decrypted[0] == META_HEADER:
            return uints_to_bytes(decrypted), slot
    # No slot produced a valid header; say so instead of returning garbage.
    raise ValueError(f"{DEBUG_PREFIX} decrypt_meta: no slot produced META_HEADER 0x{META_HEADER:08X}")


# Function: encrypt_meta
# Purpose: Encrypt an already-built plaintext meta buffer for one slot.
def encrypt_meta(blob: bytes, storage_slot: int) -> bytes:
    # Reject a buffer that is not a known Steam meta size.
    if len(blob) not in KNOWN_META_LENGTHS:
        raise ValueError(f"{DEBUG_PREFIX} encrypt_meta: unsupported meta length {len(blob)}")
    # Cast plaintext bytes to words.
    words = bytes_to_uints(blob)
    # Round count follows the same length rule as decrypt.
    rounds = rounds_for_meta_length(len(blob))
    # Build the key for the destination slot (no try-loop on write).
    key = build_slot_key(storage_slot)
    # Run the forward XXTEA pass.
    encrypted = encrypt_words(words, key, rounds)
    # Pack back to on-disk bytes.
    return uints_to_bytes(encrypted)
