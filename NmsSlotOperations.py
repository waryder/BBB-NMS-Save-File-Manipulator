# File: NmsSlotOperations.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\NmsSlotOperations.py
# Purpose: Read-only slot snapshots, memory-only ZIP loading/decoding, and explicitly confirmed backups.
from __future__ import annotations  # Keep type annotations independent of import order.

import copy  # Isolate the application's editable selected context from the full codec tree.
import datetime  # Name backups using local wall-clock time only.
import hashlib  # Identify original save and metadata bytes without disclosing contents.
import io  # Construct and inspect ZIP archives entirely in memory.
import os  # Resolve identity paths and commit explicitly approved backups.
import re  # Sanitize backup names for Windows.
import stat  # Reject ZIP members representing directories or symbolic links.
import struct  # Read metadata fields at their established offsets.
import tempfile  # Stage backups in a unique sibling file.
import zipfile  # Validate and create exact four-member slot archives.
from nms_save_codec import meta_info  # Reuse the authoritative metadata offsets.
from nms_save_codec.constants import KNOWN_META_LENGTHS, META_HEADER, SAVE_STREAMING_HEADER, SAVE_STREAMING_HEADER_LENGTH, SAVE_STREAMING_CHUNK_LENGTH_MAX  # Validate metadata and bounded chunk declarations.
from nms_save_codec.save_file import NmsSaveFile  # Use the existing save decoding pipeline.
from nms_save_codec.slots import guess_slot_from_filename  # Resolve metadata storage-key hints.
from nms_save_codec.xxtea import decrypt_meta  # Decrypt supplied metadata bytes without disk access.

DEBUG_ENABLED = True  # Global switch for every non-error trace issued by this module/API.
DEBUG_PREFIX = "[BBB-NMS-SFM/{file_name}]"  # Include project and extension-free source identity in stdout.
TIE_MESSAGE = 'the auto and manual save files appear to have the same timestamp; Hit Ok to load the manual save or Cancel to abandon this load'  # Preserve the required confirmation text exactly.
MAX_FILE_BYTES = 64 * 1024 * 1024  # Bound each original archive/live member.
MAX_TOTAL_BYTES = 128 * 1024 * 1024  # Bound aggregate uncompressed original bytes.
MAX_ARCHIVE_BYTES = MAX_TOTAL_BYTES + 1024 * 1024  # Bound archive input including ZIP headers.


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


# Function: _slot_from_names; Purpose: Infer a slot solely from an exact canonical four-member filename set.
def _slot_from_names(names) -> int:
    names = list(names)  # Preserve duplicates for rejection rather than silently collapsing them.
    if len(names) != 4 or len(set(names)) != 4:  # Reject extras, missing members, and duplicate names.
        raise ValueError("a slot archive must contain exactly four distinct root files")  # Explain the required shape.
    for slot in range(1, 16):  # Compare against every supported canonical game slot.
        if set(names) == set(_member_names(slot)):  # Exact matching rejects paths, case variants, aliases, and mixed slots.
            return slot  # The canonical filenames alone establish identity.
    raise ValueError("members must be the four canonical root files of one slot")  # Never infer identity from archive titles.


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
    folder = os.path.abspath(os.fspath(folder))  # Retain an absolute live-folder identity for future decode/backup safety.
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


# Function: _zip_members; Purpose: Validate and read exactly four original ZIP members without extracting them.
def _zip_members(archive: zipfile.ZipFile) -> tuple[int, dict[str, bytes]]:
    entries = archive.infolist()  # Preserve duplicate entries and their header sizes.
    slot = _slot_from_names(entry.filename for entry in entries)  # Reject extras, paths, missing files, and mixed slots.
    total = 0  # Bound aggregate declared uncompressed size.
    for entry in entries:  # Validate every header before reading compressed contents.
        mode = entry.external_attr >> 16  # Inspect Unix file type if it was recorded.
        if entry.flag_bits & 1 or entry.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG):  # Reject encryption, directories, and links.
            raise ValueError("ZIP members must be unencrypted regular root files")  # Refuse unsafe member identities.
        if not 0 < entry.file_size <= MAX_FILE_BYTES:  # Enforce the per-member declared-size limit.
            raise ValueError("ZIP member is empty or exceeds the 64 MiB limit")  # Stop decompression before oversized allocations.
        total += entry.file_size  # Add declared uncompressed bytes.
    if total > MAX_TOTAL_BYTES:  # Enforce the aggregate declared-size limit before decompression.
        raise ValueError("ZIP originals exceed the 128 MiB total limit")  # Refuse ZIP bombs by total size.
    members = {}  # Collect exact decompressed member bytes in memory only.
    for entry in entries:  # Reading to EOF causes zipfile to validate each member's CRC.
        with archive.open(entry, "r") as handle:  # Never call extract or create files from archive contents.
            members[entry.filename] = _bounded_read(handle)  # Independently bound actual decompressed content.
        if len(members[entry.filename]) != entry.file_size:  # Verify actual bytes agree with the member header.
            raise ValueError("ZIP member length disagrees with its header")  # Reject corrupt/inconsistent content.
    return slot, members  # Return canonical identity and originals, never archive-title identity.


# Function: read_zip_slot; Purpose: Load a bounded ZIP file into memory and return a strictly validated slot snapshot.
def read_zip_slot(path: str) -> dict:
    path = os.path.abspath(os.fspath(path))  # Preserve the archive source for trace and UI identity.
    with open(path, "rb") as handle:  # Read only the selected archive; never extract to the save folder.
        blob = handle.read(MAX_ARCHIVE_BYTES + 1)  # Bound the whole archive, including central-directory overhead.
    if len(blob) > MAX_ARCHIVE_BYTES:  # Refuse oversized compressed/container input.
        raise ValueError("ZIP archive exceeds the input-size limit")  # Fail before parsing its directory.
    with zipfile.ZipFile(io.BytesIO(blob), "r") as archive:  # Parse from memory, allowing zipfile corruption errors to propagate.
        slot, members = _zip_members(archive)  # Derive the slot exclusively from canonical root member names.
    trace("NmsSlotOperations", "read_zip_slot", slot=slot, path=path, archive_hash=hashlib.sha256(blob).hexdigest())  # Trace archive identity only.
    return _snapshot(slot, members, zip_path=path)  # Preserve both original data/meta pairs exactly.


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
        marker = tree["ActiveContext"]  # Use selected decoded data, never metadata game mode or archive identity.
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


# Function: backup_name; Purpose: Suggest a Windows-safe backup name using the longer original summary and local datetime.
def backup_name(snapshot: dict) -> str:
    checked = _snapshot(snapshot["slot"], snapshot["members"])  # Base naming on the original metadata, not arbitrary UI labels.
    summary = max((record["meta"]["summary"] for record in checked["files"]), key=len)  # Choose the longer of Auto and Manual summaries.
    fragment = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", summary[:10]).rstrip(" .") or "save"  # Sanitize the first ten summary characters for Windows.
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Use local time for naming, never for file selection.
    return f"slot{snapshot['slot']}_{fragment}_{timestamp}.zip"  # Do not create a backup or directory merely to suggest a name.


# Function: zip_bytes; Purpose: Build an in-memory backup containing only the exact four original encrypted/data members.
def zip_bytes(snapshot: dict) -> bytes:
    checked = _snapshot(snapshot["slot"], snapshot["members"])  # Require a complete validated snapshot before archiving it.
    buffer = io.BytesIO()  # Keep all archive construction in memory.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:  # Preserve original content without recompression complexity.
        for name in _member_names(checked["slot"]):  # Use the canonical four-member order with no extra manifest.
            archive.writestr(name, checked["members"][name])  # Store byte-identical originals under their exact canonical names.
    blob = buffer.getvalue()  # Obtain the finished archive without any disk side effects.
    trace("NmsSlotOperations", "zip_bytes", slot=checked["slot"], bytes=len(blob), archive_hash=hashlib.sha256(blob).hexdigest())  # Trace archive size and identity.
    return blob  # Caller decides whether and where an explicitly approved backup is written.


# Function: _backup_target; Purpose: Reject any destination resolving inside a known live-save directory.
def _backup_target(path: str, snapshot: dict) -> str:
    target = os.path.abspath(os.fspath(path))  # Return an absolute identity while checking resolved paths separately.
    if snapshot.get("live_folder"):  # Live snapshots carry the protected source folder.
        live = os.path.normcase(os.path.realpath(snapshot["live_folder"]))  # Resolve aliases and Windows case differences.
        resolved = os.path.normcase(os.path.realpath(target))  # Resolve destination parent links before comparing directories.
        try:  # Different drives do not have a common path.
            inside = os.path.commonpath((live, resolved)) == live  # Include the folder itself and every descendant.
        except ValueError:  # A destination on another drive cannot be inside the live folder.
            inside = False  # Permit only the genuinely separate destination.
        if inside:  # Never place backup files, staging files, or directories inside live saves.
            raise ValueError("backup destination must be outside the live save folder")  # Refuse before creating anything.
    return target  # Preserve the caller's absolute selected target path.


# Function: _verify_backup; Purpose: Read back an on-disk backup and require exact membership and original-byte equality.
def _verify_backup(path: str, snapshot: dict) -> None:
    with zipfile.ZipFile(path, "r") as archive:  # Read the exact written file, never extract it.
        slot, members = _zip_members(archive)  # Validate membership, CRCs, sizes, and regular-file structure.
    if slot != snapshot["slot"] or members != snapshot["members"]:  # Verify every original byte, not just a digest.
        raise ValueError("written backup does not match the original slot snapshot")  # Do not report success after a partial/corrupt write.


# Function: _commit_backup; Purpose: Atomically replace an approved target or create a new target exclusively.
def _commit_backup(temporary: str, target: str, blob: bytes, overwrite: bool) -> None:
    if overwrite:  # Replacement is available only when explicitly requested with confirmation.
        os.replace(temporary, target)  # Atomically commit the verified sibling archive, including existing targets.
    else:  # Never silently overwrite a file created since the UI's existence check.
        created = False  # Distinguish our new output from a preexisting race winner.
        try:  # Clean up only a target successfully created by this operation.
            with open(target, "xb") as handle:  # Exclusive creation prevents race overwrites on Windows/network shares.
                created = True  # Record ownership only after exclusive creation succeeds.
                handle.write(blob)  # Write the archive already staged and verified in the sibling file.
                handle.flush()  # Flush Python buffers before validating the output.
                os.fsync(handle.fileno())  # Ask the filesystem to persist the committed bytes.
        except BaseException:  # Cleanup also applies to interrupted partial writes.
            if created:  # Never remove someone else's target on a FileExistsError.
                os.unlink(target)  # Remove our partial exclusive output.
            raise  # Preserve the original write failure.


# Function: write_backup; Purpose: Write and verify a backup only after explicit confirmation, outside any known live folder.
def write_backup(path: str, snapshot: dict, confirmed: bool = False, overwrite: bool = False) -> str:
    if confirmed is not True:  # Require actual True rather than a truthy flag/string.
        raise PermissionError("backup writing requires confirmed=True")  # Fail before directory creation, staging, or output.
    target = _backup_target(path, snapshot)  # Apply live-folder protection before any write.
    blob = zip_bytes(snapshot)  # Construct and validate originals in memory before disk side effects.
    if not overwrite and os.path.lexists(target):  # Quickly reject an already occupied target without staging.
        raise FileExistsError(target)  # Existing targets require explicit overwrite=True as well as confirmation.
    parent = os.path.dirname(target)  # Stage on the same filesystem as the chosen target.
    os.makedirs(parent, exist_ok=True)  # Create the selected backup directory only after explicit confirmation.
    temporary = None  # Track the sibling temporary file for guaranteed cleanup.
    committed = False  # Only remove failed output after this operation actually created/replaced it.
    try:  # Verify staging and final output before reporting success.
        with tempfile.NamedTemporaryFile(prefix=".nms-slot-", suffix=".tmp", dir=parent, delete=False) as handle:  # Allocate a unique sibling staging file.
            temporary = handle.name  # Retain its exact path for cleanup and atomic replacement.
            handle.write(blob)  # Stage the complete in-memory archive.
            handle.flush()  # Flush buffered writes before persistence and verification.
            os.fsync(handle.fileno())  # Persist the staged bytes before committing them.
        _verify_backup(temporary, snapshot)  # Read back the exact staged member contents.
        _commit_backup(temporary, target, blob, overwrite)  # Atomically replace or create the target exclusively.
        committed = True  # Track ownership of the successfully committed output.
        _verify_backup(target, snapshot)  # Read back the actual final target before claiming success.
    except BaseException:  # Clean failed staging and any newly committed invalid output.
        if committed and os.path.isfile(target):  # Do not touch a preexisting target when exclusive creation failed.
            os.unlink(target)  # Remove a committed archive that failed final verification.
        raise  # Surface errors rather than disguising failure as a successful backup.
    finally:  # Staging files never survive success or failure.
        if temporary is not None and os.path.exists(temporary):  # Atomic replacement may have already consumed staging.
            os.unlink(temporary)  # Remove the remaining sibling temporary file.
    trace("NmsSlotOperations", "write_backup_verified", slot=snapshot["slot"], path=target, overwrite=overwrite, archive_hash=hashlib.sha256(blob).hexdigest())  # Trace only fully verified output.
    return target  # Return the exact absolute final backup path.
