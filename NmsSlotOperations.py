# File: NmsSlotOperations.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\NmsSlotOperations.py
# Purpose: Read-only live-slot snapshots, metadata selection and selected-context decoding.
from __future__ import annotations  # Keep type annotations independent of import order.

import copy  # Isolate the application's editable selected context from the full codec tree.
import hashlib  # Identify original save and metadata bytes without disclosing contents.
import os  # Resolve retained live-save identity paths.
import struct  # Read metadata fields at their established offsets.
from nms_save_codec import meta_info  # Reuse the authoritative metadata offsets.
from nms_save_codec.constants import KNOWN_META_LENGTHS, META_HEADER, SAVE_STREAMING_HEADER, SAVE_STREAMING_HEADER_LENGTH, SAVE_STREAMING_CHUNK_LENGTH_MAX  # Validate metadata and bounded chunk declarations.
from nms_save_codec.save_file import NmsSaveFile  # Use the existing save decoding pipeline.
from nms_save_codec.slots import guess_slot_from_filename  # Resolve metadata storage-key hints.
from nms_save_codec.xxtea import decrypt_meta  # Decrypt supplied metadata bytes without disk access.

DEBUG_ENABLED = True  # Global switch for every non-error trace issued by this module/API.
DEBUG_PREFIX = "[BBB-NMS-SFM/{file_name}]"  # Include project and extension-free source identity in stdout.
TIE_MESSAGE = 'the auto and manual save files appear to have the same timestamp; Hit Ok to load the manual save or Cancel to abandon this load'  # Preserve the required confirmation text exactly.
MAX_FILE_BYTES = 64 * 1024 * 1024  # Bound each original live member.
MAX_TOTAL_BYTES = 128 * 1024 * 1024  # Bound aggregate uncompressed original bytes.


# Function: trace; Purpose: Print structured non-error events behind the shared switch.
def trace(file_name: str, event: str, /, **fields) -> None:  # Positional-only source/event names cannot collide with diagnostic fields.
    if DEBUG_ENABLED:  # Suppress all normal tracing when the caller disables the global switch.
        source = os.path.splitext(os.path.basename(file_name))[0]  # Normalize a source label without its extension.
        details = " ".join(f"{key}={value!r}" for key, value in sorted(fields.items()))  # Print provided fields deterministically.
        print(f"{DEBUG_PREFIX.format(file_name=source)} {event}" + (f" {details}" if details else ""), flush=True)  # Emit a stdout trace.


# Function: error; Purpose: Print error events without suppressing them with the debug switch.
def error(file_name: str, event: str, **fields) -> None:
    source = os.path.splitext(os.path.basename(file_name))[0]  # Keep source identity consistent with trace.
    details = " ".join(f"{key}={value!r}" for key, value in sorted(fields.items()))  # Render only caller-provided error details.
    print(f"{DEBUG_PREFIX.format(file_name=source)} ERROR {event} {details}", flush=True)  # Always emit errors.


# Function: slot_filenames; Purpose: Return canonical Auto and Manual data names for game slots 1..15.
def slot_filenames(slot: int) -> tuple[str, str]:
    if type(slot) is not int or not 1 <= slot <= 15:  # Reject booleans, coercions, and out-of-range slots.
        raise ValueError("slot must be an integer from 1 through 15")  # Fail before accessing anything.
    auto_index = slot * 2 - 1  # Map the game slot to its odd-numbered Auto file.
    return ("save.hg" if slot == 1 else f"save{auto_index}.hg", f"save{slot * 2}.hg")  # Return Auto before Manual.


# Function: _member_names; Purpose: Describe exactly four canonical originals for a slot.
def _member_names(slot: int) -> tuple[str, ...]:
    auto, manual = slot_filenames(slot)  # Validate the game slot and derive data filenames.
    return auto, manual, "mf_" + auto, "mf_" + manual  # Require both data files and both metadata siblings.


# Function: _bounded_read; Purpose: Read at most one accepted file's bytes and reject overflow.
def _bounded_read(handle) -> bytes:
    blob = handle.read(MAX_FILE_BYTES + 1)  # Read one overflow byte to detect oversized streams.
    if not blob or len(blob) > MAX_FILE_BYTES:  # Reject missing content or content exceeding the member limit.
        raise ValueError("save member is empty or exceeds the 64 MiB limit")  # Fail safely with a bounded allocation.
    return blob  # Keep original binary content unchanged.


# Function: _parse_meta; Purpose: Strictly decrypt current metadata and require an available positive timestamp.
def _parse_meta(blob: bytes, name: str) -> dict:
    if len(blob) not in KNOWN_META_LENGTHS or len(blob) < meta_info.META_MIN_LENGTH_TIMESTAMP:  # Reject older/unknown formats.
        raise ValueError(f"{name}: metadata lacks a supported timestamp format")  # Never fall back to filesystem dates.
    plain, storage_slot = decrypt_meta(blob, guess_slot_from_filename(name), is_account=False)  # Decrypt from encrypted originals.
    if struct.unpack_from("<I", plain, 0)[0] != META_HEADER:  # Validate the successful cipher result explicitly.
        raise ValueError(f"{name}: invalid decrypted metadata header")  # Refuse corrupt metadata.
    timestamp = struct.unpack_from("<I", plain, meta_info.META_OFFSET_TIMESTAMP)[0]  # Read the embedded Unix timestamp.
    if timestamp <= 0:  # A missing timestamp is not a valid tie or sortable date.
        raise ValueError(f"{name}: metadata timestamp must be positive")  # Require genuine available metadata time.
    return {  # Match the existing metadata summary field names and retain the winning storage key.
        "name": _meta_text(plain, meta_info.META_OFFSET_SAVE_NAME),  # Decode the fixed save-name field.
        "summary": _meta_text(plain, meta_info.META_OFFSET_SAVE_SUMMARY),  # Decode the fixed summary field.
        "timestamp": timestamp,  # Use only this timestamp when choosing the latest record.
        "game_mode": struct.unpack_from("<H", plain, meta_info.META_OFFSET_GAME_MODE)[0],  # Preserve mode metadata.
        "storage_slot": storage_slot,  # Retain cipher identity for diagnostics without replacing filename identity.
    }  # Finish the validated metadata record.


# Function: _meta_text; Purpose: Decode a fixed-width metadata string without exposing raw bytes in traces.
def _meta_text(plain: bytes, offset: int) -> str:
    return plain[offset:offset + meta_info.META_TEXT_LENGTH].split(b"\x00", 1)[0].decode("utf-8", "replace")  # Match the established text parser.


# Function: _validate_data_bounds; Purpose: Reject oversized LZ4 declarations before codec decompression allocates memory.
def _validate_data_bounds(blob: bytes) -> None:
    if not blob.startswith(SAVE_STREAMING_HEADER):  # Old uncompressed saves remain bounded by their file size.
        return  # Let the codec parse and validate their JSON content.
    offset, total = 0, 0  # Walk headers without decompressing or modifying original data.
    while offset < len(blob):  # Every chunk must fit inside the supplied file.
        if offset + SAVE_STREAMING_HEADER_LENGTH > len(blob):  # Reject an incomplete header.
            raise ValueError("save streaming header is truncated")  # Stop before codec allocation.
        magic, compressed, plain, reserved = struct.unpack_from("<4sIII", blob, offset)  # Read declared lengths.
        if magic != SAVE_STREAMING_HEADER or not 0 < plain <= SAVE_STREAMING_CHUNK_LENGTH_MAX or compressed <= 0:  # Validate chunk sizes.
            raise ValueError("save contains an invalid or oversized streaming chunk")  # Refuse malformed LZ4 input.
        offset += SAVE_STREAMING_HEADER_LENGTH + compressed  # Advance to the next bounded chunk.
        total += plain  # Count declared decoded payload bytes across all chunks.
        if offset > len(blob) or total > MAX_FILE_BYTES:  # Do not trust a small ZIP to imply a small decoded save.
            raise ValueError("save payload is truncated or exceeds the decoded 64 MiB limit")  # Fail without decompression.


# Function: _snapshot; Purpose: Build records from a complete, bounded set of original bytes.
def _snapshot(slot: int, members: dict[str, bytes], **identity) -> dict:
    if set(members) != set(_member_names(slot)):  # Require all originals before exposing a usable snapshot.
        raise ValueError("snapshot members do not match the requested slot")  # Reject partial or mismatched snapshots.
    if any(type(blob) is not bytes or not blob or len(blob) > MAX_FILE_BYTES for blob in members.values()):  # Check byte types and member bounds.
        raise ValueError("snapshot contains invalid or oversized original bytes")  # Refuse malformed caller snapshots.
    if sum(map(len, members.values())) > MAX_TOTAL_BYTES:  # Apply the aggregate memory limit.
        raise ValueError("slot originals exceed the 128 MiB total limit")  # Fail before decoding metadata.
    records = []  # Keep Auto then Manual ordering for deterministic UI behavior.
    for name, save_type in zip(slot_filenames(slot), ("Auto", "Manual")):  # Associate each canonical filename with its type.
        data, meta = members[name], members["mf_" + name]  # Preserve the exact encrypted originals.
        _validate_data_bounds(data)  # Refuse excessive decoded sizes before exposing a loadable snapshot.
        record = {"slot": slot, "file_name": name, "save_type": save_type, "meta": _parse_meta(meta, name), "data_bytes": data, "meta_bytes": meta}  # Construct the integration record.
        record.update(data_hash=hashlib.sha256(data).hexdigest(), meta_hash=hashlib.sha256(meta).hexdigest())  # Attach original-byte identities.
        records.append(record)  # Expose only records with validated metadata.
        trace("NmsSlotOperations", "snapshot_record", slot=slot, file_name=name, timestamp=record["meta"]["timestamp"], data_hash=record["data_hash"], meta_hash=record["meta_hash"])  # Trace identities, not contents.
    return {"slot": slot, "files": records, "members": dict(members), **identity}  # Retain optional source identity alongside complete originals.


# Function: read_live_slot; Purpose: Read only four canonical files into an independent in-memory snapshot.
def read_live_slot(folder: str, slot: int) -> dict:
    names = _member_names(slot)  # Validate before any file I/O.
    folder = os.path.abspath(os.fspath(folder))  # Retain an absolute live-folder identity for future decode/save safety.
    members = {}  # Collect all four originals without modifying their sources.
    total = 0  # Track aggregate allocation as each member arrives.
    for name in names:  # Read exactly the four requested slot members.
        with open(os.path.join(folder, name), "rb") as handle:  # Read-only mode never creates or truncates a live save.
            members[name] = _bounded_read(handle)  # Fail on empty, missing, unreadable, or oversized members.
        total += len(members[name])  # Count original bytes, not filesystem timestamps.
        if total > MAX_TOTAL_BYTES:  # Stop before allocating the remaining files.
            raise ValueError("slot originals exceed the 128 MiB total limit")  # Refuse an oversized snapshot.
    for name in names:  # Detect game/editor writes during the non-atomic four-file read.
        with open(os.path.join(folder, name), "rb") as handle:  # Second read is still strictly read-only.
            if _bounded_read(handle) != members[name]:  # Byte comparison ignores filesystem timestamps entirely.
                raise ValueError("live save files changed while being read; retry when the game is not saving")  # Avoid a mixed snapshot.
    trace("NmsSlotOperations", "read_live_slot", slot=slot, folder=folder, bytes=total, stable_double_read=True)  # Report read-only completion.
    return _snapshot(slot, members, live_folder=folder)  # Require both valid metadata timestamps before returning.


# Function: select_slot_file; Purpose: Choose the latest embedded metadata time or explicitly confirm Manual on a tie.
def select_slot_file(snapshot: dict, confirm_manual) -> dict | None:
    checked = _snapshot(snapshot["slot"], snapshot["members"])  # Revalidate originals instead of trusting supplied timestamps.
    auto, manual = checked["files"]  # Use deterministic canonical Auto/Manual ordering.
    auto_time, manual_time = auto["meta"]["timestamp"], manual["meta"]["timestamp"]  # Compare only embedded metadata timestamps.
    if auto_time == manual_time:  # Ties require exactly the user-specified confirmation.
        selected = manual if bool(confirm_manual(TIE_MESSAGE)) else None  # OK selects Manual; Cancel abandons this load.
    else:  # Unequal timestamps never ask for confirmation.
        selected = auto if auto_time > manual_time else manual  # Choose the genuinely newer metadata record.
    trace("NmsSlotOperations", "select_slot_file", slot=snapshot["slot"], selected=selected["file_name"] if selected else None, tied=auto_time == manual_time)  # Report selection without reading saves again.
    return selected  # Return the selected validated record or None without trusting mutable summary records.


# Function: _resolve_context_key; Purpose: Resolve the selected save's marker without guessing another branch.
def _resolve_context_key(tree) -> str:
    if not isinstance(tree, dict):  # Require the full decoded save wrapper before examining its marker.
        raise ValueError("decoded save must be a dictionary")  # Reject partial/non-object input clearly.
    if "ActiveContext" not in tree:  # Only an absent marker permits the legacy Main-only rule.
        if "ExpeditionContext" in tree:  # Branch presence with no marker is ambiguous, even if malformed.
            raise ValueError("ActiveContext is missing with ExpeditionContext present; context is ambiguous")  # Never guess Main.
        key, marker, decision = "BaseContext", "absent", "legacy Main-only"  # Preserve old BaseContext-only saves.
    else:  # Explicit markers must select exactly one supported branch.
        marker = tree["ActiveContext"]  # Use selected decoded data, never metadata game mode.
        if type(marker) is not str or marker not in ("Main", "Season"):  # Reject null, empty, compound and unknown markers.
            raise ValueError("ActiveContext must be exactly Main or Season; explicit context is unsupported or ambiguous")  # Do not log raw malformed data.
        key = "ExpeditionContext" if marker == "Season" else "BaseContext"  # Main wins even when expedition data remains.
        decision = "explicit marker"  # Explain the choice without claiming a game selection rule.
    trace("NmsSlotOperations", "resolve_context", marker=marker, context_key=key, decision=decision)  # Shared switch; no save JSON.
    return key  # Retain this exact node as part of successful source identity.


# Function: _validate_tree; Purpose: Require the selected whole context and existing essential player lists.
def _validate_tree(tree, context_key=None) -> dict:
    key = _resolve_context_key(tree) if context_key is None else context_key  # Preserve the helper's one-argument interface.
    if not isinstance(tree.get(key), dict):  # Validate the selected branch only; never fall back to the inactive one.
        raise ValueError(f"decoded save must contain a dictionary {key}")  # Identify the missing/malformed selected branch.
    context = tree[key]  # Keep the whole context, including GameMode, SpawnStateData and unknown fields.
    if not isinstance(context.get("PlayerStateData"), dict):  # Require the existing player data container.
        raise ValueError(f"{key} must contain dictionary PlayerStateData")  # Reject unsupported structure explicitly.
    player = context["PlayerStateData"]  # Validate unchanged relative tab paths against the selected context.
    for name in ("PersistentPlayerBases", "ShipOwnership", "TeleportEndpoints"):  # Inventory remains optional as before.
        if not isinstance(player.get(name), list):  # Missing/non-list sections cannot be safely handed to the UI.
            raise ValueError(f"{key}.PlayerStateData.{name} must be a list")  # Report structure, never contents.
    return context  # Leave the entire retained codec tree untouched.


# Function: decode_record; Purpose: Decode original bytes with canonical identity and an isolated editable whole context.
def decode_record(record: dict, live_folder: str) -> dict:
    slot = record["slot"]  # Require filename-derived game-slot identity retained in snapshot records.
    name = record["file_name"]  # Preserve the canonical selected filename.
    if name not in slot_filenames(slot):  # Prevent caller-supplied path traversal or mixed-slot identity.
        raise ValueError("selected record filename does not match its slot")  # Fail before assigning output identity.
    _parse_meta(record["meta_bytes"], name)  # Require valid encrypted metadata even for standalone records.
    _validate_data_bounds(record["data_bytes"])  # Standalone callers receive the same pre-decompression size checks.
    folder = os.path.abspath(os.fspath(live_folder))  # Normalize identity without accessing any live save file.
    data_path, meta_path = os.path.join(folder, name), os.path.join(folder, "mf_" + name)  # Retain future-save destination identities.
    codec = NmsSaveFile().load_bytes(record["data_bytes"], data_path, record["meta_bytes"])  # Load entirely from bytes with correct path and decrypted metadata.
    tree = codec.decode()  # Deobfuscate the complete save and preserve every other top-level field.
    context_key = _resolve_context_key(tree)  # Remember the selected decoded marker's exact destination node.
    base = _validate_tree(tree, context_key)  # Validate required lists in that branch without falling back.
    data_hash = hashlib.sha256(record["data_bytes"]).hexdigest()  # Fingerprint the original selected data bytes.
    meta_hash = hashlib.sha256(record["meta_bytes"]).hexdigest()  # Fingerprint the original encrypted metadata bytes.
    trace("NmsSlotOperations", "decode_record", slot=slot, file_name=name, context_key=context_key, unknown_keys=len(codec.unknown_keys), data_hash=data_hash, meta_hash=meta_hash)  # Trace selected identity and counts, never JSON.
    return {"codec": codec, "tree": tree, "context_key": context_key, "base_context": copy.deepcopy(base), "file_name": name, "meta_name": "mf_" + name, "slot": slot, "live_folder": folder, "data_path": data_path, "meta_path": meta_path, "data_hash": data_hash, "meta_hash": meta_hash}  # base_context is a compatibility field for the selected whole context, not necessarily Main.
