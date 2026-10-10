# File: save_file.py
# Purpose: Self-contained NMS save file class - decodes .hg files to JSON dicts and encodes them back.
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\save_file.py

from __future__ import annotations

import json
import os
import struct

from .hashed_ids import escape_hashed_ids, restore_hashed_ids
from .mapping import KeyMapping
from .platforms import get_platform
from .slots import guess_kind_from_filename, guess_slot_from_filename, is_account_filename
from .streaming import compress_save, decompress_save
from .xxtea import decrypt_meta, encrypt_meta

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/save_file]"
# Non-error debug stays behind this flag; errors always raise.
DEBUG_ENABLED = False

# Byte offset of DECOMPRESSED SIZE inside a decrypted Steam/GOG meta file (all eras).
META_OFFSET_SIZE_DECOMPRESSED = 0x38
# Byte offset of COMPRESSED SIZE, used since Worlds Part I (meta format 3+).
META_OFFSET_SIZE_DISK = 0x3C
# Meta length of the first era that stores COMPRESSED SIZE (Worlds Part I = 0x180).
META_LENGTH_WORLDS_PART_I = 0x180
# Embedded Unix-seconds timestamp in supported Worlds metadata; row-50 updates only the selected sibling.
META_OFFSET_TIMESTAMP = 0x164
# Steam meta files start with this dword once decrypted successfully.
META_HEADER = 0xEEEEEEBE


# Class: NmsSaveFile
# Purpose: One No Man's Sky save file: load, decode, edit, encode, and write back out.
class NmsSaveFile:
    # Debug prefix required by Bill's code standards (class-level constant).
    DEBUG_PREFIX = "[BBB-NMS-SFM/NmsSaveFile]"

    # Function: __init__
    # Purpose: Configure the platform and key mapping without touching any file yet.
    def __init__(self, platform: str = "steam", mapping_path: str | None = None):
        # Resolve the platform through the registry so stubs fail with a clear message.
        self.platform = get_platform(platform)
        # Load the key mapping once per instance; an external file overrides the bundled pin.
        self.mapping = KeyMapping(mapping_path=mapping_path)
        # No file loaded yet; every load_* sets the fields below.
        self._reset()

    # Function: _reset
    # Purpose: Clear all per-file state so one instance can load a series of files.
    def _reset(self) -> None:
        # Original on-disk bytes of the data file.
        self._disk_bytes = None
        # Decrypted plaintext bytes of the meta file, when one was loaded.
        self._meta_plain = None
        # Slot that successfully decrypted the meta file.
        self._meta_slot = None
        # Parsed JSON tree in its current (obfuscated or plaintext) state.
        self._json = None
        # True when the file on disk used obfuscated keys at all.
        self._uses_mapping = False
        # True when the current tree is in plaintext (deobfuscated) form.
        self._deobfuscated = False
        # Keys the mapping table did not recognize, filled during decode().
        self.unknown_keys = set()
        # Source path and basename, used by write_to() for output naming.
        self.source_path = None
        # Account flag (accountdata.hg vs save*.hg) decided from the filename.
        self.is_account = False
        # Pre-compression payload length from the last encode() call, used by encode_meta().
        self._last_plain_payload = None

    # Function: load_file
    # Purpose: Read and decode one save data file, auto-loading its meta sibling when present.
    def load_file(self, data_path: str, meta_path: str | None = None) -> "NmsSaveFile":
        # Start from a clean state in case a previous file was loaded on this instance.
        self._reset()
        # Remember the source for write_to() naming.
        self.source_path = os.path.abspath(data_path)
        # Read the whole file as bytes; .hg files are binary even when they hold JSON.
        with open(data_path, "rb") as handle:
            self._disk_bytes = handle.read()
        # Account files (accountdata.hg) use a different key family and no compression.
        self.is_account = is_account_filename(os.path.basename(data_path))
        # Decode the payload into a parsed JSON tree.
        self._decode_disk_bytes(os.path.basename(data_path))
        # Load the meta sibling when the caller named one or the default mf_ file exists.
        guessed = meta_path or self._guess_meta_path()
        # Only attempt a meta load when a candidate file actually exists.
        if guessed and os.path.isfile(guessed):
            # Decrypt and keep the plaintext meta for encode_meta() later.
            self._load_meta(guessed)
        # Chaining is convenient: NmsSaveFile().load_file(p).decode().
        return self

    # Function: load_bytes
    # Purpose: Decode supplied bytes and retain source identity and decrypted meta without file I/O.
    def load_bytes(self, data_bytes: bytes, source_name: str, meta_bytes: bytes | None = None) -> "NmsSaveFile":
        self._reset()  # Clear any previously loaded save state.
        self.source_path = os.path.abspath(os.fspath(source_name))  # Preserve the supplied source path for future writes.
        self._disk_bytes = bytes(data_bytes)  # Keep an immutable copy of the original payload.
        name = os.path.basename(self.source_path)  # Use only the canonical basename for codec identity.
        self.is_account = is_account_filename(name)  # Select the correct account/save decode family.
        self._decode_disk_bytes(name)  # Parse the in-memory payload through the existing codec pipeline.
        if meta_bytes is not None:  # Load supplied metadata only, never a disk sibling.
            hint = guess_slot_from_filename(name)  # Obtain the storage-key hint from the filename.
            plain, slot = decrypt_meta(bytes(meta_bytes), hint, is_account=self.is_account)  # Decrypt the supplied metadata.
            if len(plain) < 4 or struct.unpack_from("<I", plain, 0)[0] != META_HEADER:  # Reject invalid metadata headers.
                raise ValueError(f"{self.DEBUG_PREFIX} load_bytes: invalid decrypted metadata header")  # Fail without writing anything.
            self._meta_plain, self._meta_slot = plain, slot  # Preserve metadata and its winning encryption key for encode_meta.
        return self  # Support the existing chained load/decode API.

    # Function: _guess_meta_path
    # Purpose: Build the default mf_ meta path next to the loaded data file.
    def _guess_meta_path(self) -> str:
        # Without a data path there is nothing to guess from.
        if not self.source_path:
            # No source means no guess.
            return None
        # Steam/GOG meta files are the mf_ siblings in the same directory.
        folder = os.path.dirname(self.source_path)
        # mf_save.hg / mf_save2.hg / mf_accountdata.hg per the platform's prefix.
        return os.path.join(folder, f"{self.platform.meta_prefix}{os.path.basename(self.source_path)}")

    # Function: _decode_disk_bytes
    # Purpose: Turn raw .hg bytes into a parsed JSON tree following libNOM.io's read pipeline.
    def _decode_disk_bytes(self, source_name: str) -> None:
        # 1. Decompress the streaming LZ4 chunks (account and pre-Frontiers data pass through).
        decompressed = decompress_save(self._disk_bytes)
        # 2. Escape raw hashed technology IDs before any NUL handling, like libNOM.io GetJson.
        if self.platform.hashed_ids and not self.is_account:
            # Raw (^<bytes>#) becomes JSON-safe (^<HEX>#).
            decompressed = escape_hashed_ids(decompressed)
        # 3. Cut at the first NUL, which is the JSON terminator written by the game.
        terminator = decompressed.find(b"\x00")
        # A missing terminator means the whole buffer is JSON text (defensive).
        text_bytes = decompressed if terminator < 0 else decompressed[:terminator]
        # 4. Decode UTF-8; the game writes raw UTF-8, not escaped ASCII.
        text = text_bytes.decode("utf-8")
        # 5. Repair Hello Games' broken escapes: backslash + raw control char becomes \t/\n/\r.
        text = text.replace("\x09", "t").replace("\x0a", "n").replace("\x0d", "r")
        # 6. Parse the repaired JSON text into the current tree state.
        self._json = json.loads(text)
        # 7. Record whether the file uses obfuscated keys so encode() knows its target state.
        self._uses_mapping = self.mapping.input_uses_obfuscated_keys(self._json, self.is_account)
        # Debug output behind the flag per code standards.
        if DEBUG_ENABLED:
            # One line summarizing the load.
            print(f"{DEBUG_PREFIX} _decode_disk_bytes: {source_name} account={self.is_account} obfuscated={self._uses_mapping}")

    # Function: _load_meta
    # Purpose: Read and decrypt a Steam/GOG meta (mf_*) file.
    def _load_meta(self, meta_path: str) -> None:
        # Read the whole encrypted meta file as bytes.
        with open(meta_path, "rb") as handle:
            # Small files (432 bytes) so a full read is fine.
            encrypted = handle.read()
        # Start with the slot the filename implies; decrypt_meta walks the family on failure.
        hint = guess_slot_from_filename(os.path.basename(self.source_path))
        # Steam/GOG meta files are XXTEA encrypted; the winning slot is returned too.
        self._meta_plain, self._meta_slot = decrypt_meta(encrypted, hint, is_account=self.is_account)
        # Sanity check the header dword so a wrong-slot decrypt can never pass silently.
        header = struct.unpack_from("<I", self._meta_plain, 0)[0]
        # A valid decrypt always starts with 0xEEEEEEBE.
        if header != META_HEADER:
            # Loud failure instead of returning garbage.
            raise ValueError(f"{DEBUG_PREFIX} _load_meta: decrypted header 0x{header:08X} != 0x{META_HEADER:08X} ({meta_path})")

    # Function: decode
    # Purpose: Return the JSON tree, deobfuscated into readable key names by default.
    def decode(self, deobfuscate_keys: bool = True) -> dict:
        # Nothing loaded means the caller forgot load_file().
        if self._json is None:
            # Loud failure with the exact fix.
            raise RuntimeError(f"{DEBUG_PREFIX} decode: no file loaded; call load_file() first")
        # Only run the rename pass when the file was obfuscated and is not plaintext already.
        if deobfuscate_keys and self._uses_mapping and not self._deobfuscated:
            # Rename every known key and collect the ones the table does not know.
            self._json, self.unknown_keys = self.mapping.deobfuscate(self._json, self.is_account)
            # The tree is now in plaintext form.
            self._deobfuscated = True
            # Debug output behind the flag per code standards.
            if DEBUG_ENABLED:
                # One line summarizing the rename pass.
                print(f"{DEBUG_PREFIX} decode: deobfuscated, unknown keys: {len(self.unknown_keys)}")
        # Hand the current tree to the caller for editing.
        return self._json

    # Function: encode
    # Purpose: Serialize the (possibly edited) tree back into on-disk .hg bytes.
    def encode(self) -> bytes:
        # Nothing loaded means the caller forgot load_file().
        if self._json is None:
            # Loud failure with the exact fix.
            raise RuntimeError(f"{DEBUG_PREFIX} encode: no file loaded; call load_file() first")
        # Re-obfuscate first when the tree is currently in plaintext form.
        if self._deobfuscated:
            # Reverse the rename pass so the game sees its obfuscated keys again.
            self._json = self.mapping.obfuscate(self._json, self.is_account)
            # The tree is back in on-disk (obfuscated) form.
            self._deobfuscated = False
        # Compact serialization matches the game writer: no spaces between separators.
        text = json.dumps(self._json, separators=(",", ":"), ensure_ascii=False)
        # libNOM.io escapes every forward slash the same way the game expects.
        text = text.replace("/", "\\/")
        # UTF-8 bytes plus the NUL terminator the game writer appends.
        blob = text.encode("utf-8") + b"\x00"
        # Put the raw hashed technology IDs back into the stream, like libNOM.io CreateData.
        blob = restore_hashed_ids(blob)
        # Remember the pre-compression payload so encode_meta() can patch its size field.
        self._last_plain_payload = blob
        # Account data is stored uncompressed; save data gets the LZ4 streaming chunks.
        return blob if self.is_account else compress_save(blob)

    # Function: encode_meta
    # Purpose: Patch sizes and an optional explicit timestamp, then re-encrypt the same loaded metadata.
    def encode_meta(self, *, timestamp: int | None = None) -> bytes:
        # A meta file must have been loaded for this to work.
        if self._meta_plain is None:
            # Loud failure explaining what is missing.
            raise RuntimeError(f"{DEBUG_PREFIX} encode_meta: no meta file loaded; load_file() needs its mf_ sibling")
        # Validate an explicitly requested current timestamp before encoding or touching metadata.
        if timestamp is not None:
            # Old callers omit timestamp and retain their existing behavior.
            if type(timestamp) is not int or not 0 < timestamp <= 0xFFFFFFFF or len(self._meta_plain) < META_LENGTH_WORLDS_PART_I:
                # Refuse unsupported metadata or values instead of silently writing an invalid timestamp.
                raise ValueError(f"{DEBUG_PREFIX} encode_meta: timestamp needs supported metadata and positive u32 seconds")
        # Encode the data first so both size fields have real numbers to store.
        data = self.encode()
        # The decompressed size is the pre-compression payload length (JSON + terminator + raw IDs).
        decompressed_size = len(self._last_plain_payload)
        # Work on a copy so repeated calls stay deterministic.
        meta = bytearray(self._meta_plain)
        # Patch DECOMPRESSED SIZE at 0x38, present in every meta era.
        struct.pack_into("<I", meta, META_OFFSET_SIZE_DECOMPRESSED, decompressed_size)
        # COMPRESSED SIZE exists since Worlds Part I (meta length >= 0x180).
        if len(meta) >= META_LENGTH_WORLDS_PART_I:
            # Patch the on-disk (compressed) size at 0x3C.
            struct.pack_into("<I", meta, META_OFFSET_SIZE_DISK, len(data))
        # Change time only for the caller that explicitly requests row-50 saving.
        if timestamp is not None:
            # Keep save name/summary and all unrelated metadata bytes intact.
            struct.pack_into("<I", meta, META_OFFSET_TIMESTAMP, timestamp)
        # Re-encrypt with the slot that decrypted the original, keeping the file in its slot.
        return encrypt_meta(bytes(meta), self._meta_slot)

    # Function: write_to
    # Purpose: Write the re-encoded data (and meta) into an output directory.
    def write_to(self, out_dir: str, include_meta: bool = True) -> dict:
        # Create the output directory when it does not exist yet.
        os.makedirs(out_dir, exist_ok=True)
        # Encode the data file bytes once.
        data = self.encode()
        # Data file keeps the source basename so the game recognizes it.
        data_path = os.path.join(out_dir, os.path.basename(self.source_path))
        # Write the bytes exactly as encoded; no newline translation on Windows.
        with open(data_path, "wb") as handle:
            # One write, no buffering games.
            handle.write(data)
        # Track the written paths for the report.
        written = {"data": data_path}
        # Meta is only written when one was loaded and the caller wants it.
        if include_meta and self._meta_plain is not None:
            # Patch and re-encrypt the meta.
            meta = self.encode_meta()
            # Meta keeps the mf_ naming of its source.
            meta_path = os.path.join(out_dir, f"{self.platform.meta_prefix}{os.path.basename(self.source_path)}")
            # Write the encrypted meta bytes.
            with open(meta_path, "wb") as handle:
                # One write, no newline translation on Windows.
                handle.write(meta)
            # Record the meta path too.
            written["meta"] = meta_path
        # Report what was written so callers can verify.
        return written
