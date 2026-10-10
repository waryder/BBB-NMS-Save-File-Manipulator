# File: NmsLiveSaveOperations.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\NmsLiveSaveOperations.py
# Purpose: Row-50 whole-context encoding and confirmed same-file data/meta writes; no Backup/Restore operations.
from __future__ import annotations  # Keep helper annotations independent of import order.

import copy  # Prepare an independent codec/tree so a failed save cannot damage retained app state.
import hashlib  # Refresh live-source identities only after verified writes.
import os  # Retain exact targets and atomically replace each staged member.
import tempfile  # Stage and verify bytes beside their targets before replacement.
import time  # Set the selected metadata timestamp to the current Unix second.
import NmsSlotOperations as slot_ops  # Reuse validation and the existing global trace switch, not backup behavior.

DEBUG_PREFIX = "[BBB-NMS-SFM/NmsLiveSaveOperations]"  # Identify errors without exposing save content.


# Class: LiveSaveRecoveryError; Purpose: Distinguish uncertain disk recovery from an ordinary failed/cancelled save.
class LiveSaveRecoveryError(RuntimeError):  # The controller must keep the LED dirty when disk recovery fails.
    pass  # Carry a clear error message through the standard controller error popup.


# Function: retained_live_paths; Purpose: Validate exact loaded file/slot/folder identity without accessing disk.
def retained_live_paths(source: dict) -> tuple[str, str]:
    name, slot = source["file_name"], source["slot"]  # Use loaded identity, never a currently browsed slot.
    if name not in slot_ops.slot_filenames(slot) or source["meta_name"] != "mf_" + name:  # Require the canonical selected pair.
        raise ValueError("loaded data/meta filename identity does not match its slot")  # Refuse target redirection.
    folder = os.path.abspath(os.fspath(source["live_folder"]))  # Preserve the loaded live folder.
    expected = (os.path.join(folder, name), os.path.join(folder, "mf_" + name))  # Derive only the retained pair.
    actual = (os.path.abspath(source["data_path"]), os.path.abspath(source["meta_path"]))  # Normalize supplied identity fields.
    if tuple(map(os.path.normcase, actual)) != tuple(map(os.path.normcase, expected)):  # Detect mismatched retained paths.
        raise ValueError("loaded live paths disagree with the retained file/slot/folder identity")  # Never silently repair them.
    return actual  # No filesystem read or write is needed for this check.


# Function: prepare_live_save; Purpose: Merge the edited whole context into a cloned full-save codec and verify its round trip.
def prepare_live_save(source: dict, edited_context: dict) -> dict:
    retained_live_paths(source)  # Reject inconsistent target identity before serialization.
    key = source["context_key"]  # Use the key remembered at successful load; do not detect the marker again.
    if key not in ("BaseContext", "ExpeditionContext"):  # Reject unsupported retained context identity.
        raise ValueError("loaded context key must be BaseContext or ExpeditionContext")  # Never guess a destination node.
    slot_ops._validate_tree(source["tree"], key)  # Validate the retained selected branch using existing list requirements.
    slot_ops._validate_tree({key: edited_context}, key)  # Validate the edited context without resolving a different branch.
    merged = copy.deepcopy(source["tree"])  # Retain every inactive context and unrelated root field independently.
    merged[key] = copy.deepcopy(edited_context)  # Copy the whole context, including GameMode and SpawnStateData.
    codec = copy.deepcopy(source["codec"])  # Encoding mutates codec state, so never encode the retained instance directly.
    tree = codec.decode()  # Use the existing loaded mapping, metadata and platform.
    tree.clear()  # Replace the clone's full decoded tree without changing the original codec/tree.
    tree.update(copy.deepcopy(merged))  # Encode the complete merged save, not a context alone.
    timestamp = int(time.time())  # Use now without forcing a sibling-selection timestamp increment.
    data = codec.encode()  # Produce actual mapped/LZ4 save bytes entirely in memory.
    meta = codec.encode_meta(timestamp=timestamp)  # Patch data sizes and the same metadata's current timestamp.
    verified_codec = copy.deepcopy(codec).load_bytes(data, source["data_path"], meta)  # Reload the exact bytes using the retained platform and mapping objects.
    decoded = verified_codec.decode()  # Retain updated original bytes and metadata for subsequent edits/saves.
    if decoded != merged:  # Any unintended semantic change must stop before disk writes.
        raise ValueError("encoded full save does not match the edited context plus unchanged other fields")  # Do not print JSON diffs.
    updated = {**source, "codec": verified_codec, "tree": decoded, "base_context": copy.deepcopy(edited_context), "source_kind": "live", "data_hash": hashlib.sha256(data).hexdigest(), "meta_hash": hashlib.sha256(meta).hexdigest()}  # Keep targeting while refreshing saved state.
    slot_ops.trace("NmsLiveSaveOperations", "prepare_live_save", slot=source["slot"], file_name=source["file_name"], context_key=key, timestamp=timestamp, roundtrip=True)  # Shared switch; no save JSON.
    return {"source": updated, "data_bytes": data, "meta_bytes": meta, "timestamp": timestamp}  # No filesystem side effects.


# Function: _stage_bytes; Purpose: Write, flush and read-verify one unique sibling temporary file.
def _stage_bytes(target: str, blob: bytes, staged: list[str]) -> str:
    with tempfile.NamedTemporaryFile(prefix=".nms-write-", suffix=".tmp", dir=os.path.dirname(target), delete=False) as handle:  # Same filesystem as target.
        path = handle.name  # Preserve the path even when staging raises.
        staged.append(path)  # Caller owns cleanup on both success and failure.
        handle.write(blob)  # Write only explicitly confirmed bytes.
        handle.flush()  # Flush buffered output before verification.
        os.fsync(handle.fileno())  # Request persistence before replacement.
    with open(path, "rb") as handle:  # Read back the exact staged target, not a presumed copy.
        if handle.read(len(blob) + 1) != blob:  # Reject partial or corrupted staging.
            raise OSError("staged save member failed byte verification")  # Never replace a target with unverified content.
    return path  # Caller replaces this verified sibling atomically.


# Function: _read_pair; Purpose: Read current target bytes for verification or caught-error recovery, not conflict detection.
def _read_pair(paths: tuple[str, str]) -> tuple[bytes, bytes]:
    blobs = []  # Keep both member identities in their data/meta order.
    for path in paths:  # Read only the exact selected pair, not the other Auto/Manual pair.
        with open(path, "rb") as handle:  # No target creation or truncation.
            blobs.append(slot_ops._bounded_read(handle))  # Bound allocation and reject empty members.
    return tuple(blobs)  # Original bytes stay in memory; this does not create a backup/archive.


# Function: _restore_pair; Purpose: Restore current pre-write bytes after a caught replacement/readback failure.
def _restore_pair(paths: tuple[str, str], original: tuple[bytes, bytes], staged: list[str]) -> None:
    temporary = [_stage_bytes(path, blob, staged) for path, blob in zip(paths, original)]  # Verify both recovery members first.
    for path, pending in zip(paths, temporary):  # Restore the pair captured immediately before this attempted write.
        os.replace(pending, path)  # Atomically restore each member rather than truncating it in place.
    if _read_pair(paths) != original:  # Verify the actual restored pair before reporting recovery.
        raise OSError("restored save pair failed byte verification")  # Recovery cannot be claimed from a successful replace alone.


# Function: write_live_save; Purpose: Replace only the warning-confirmed selected data/meta pair and verify both final files.
def write_live_save(source: dict, prepared: dict, *, confirmed: bool = False) -> dict:
    if confirmed is not True:  # This guard precedes all disk reads, temporary files and writes.
        raise PermissionError("live-save writing requires confirmed=True")  # A selected filename is not approval.
    paths = retained_live_paths(source)  # Use only the original loaded identity.
    if retained_live_paths(prepared["source"]) != paths or prepared["source"]["context_key"] != source["context_key"]:  # Reject staging for a different target/context.
        raise ValueError("prepared save identity differs from the loaded source")  # Do not redirect live writes.
    blobs = (prepared["data_bytes"], prepared["meta_bytes"])  # Preserve the prepared selected data/meta order.
    if any(type(blob) is not bytes or not blob or len(blob) > slot_ops.MAX_FILE_BYTES for blob in blobs):  # Validate output bounds.
        raise ValueError("prepared save members are invalid or oversized")  # Fail before staging or replacement.
    if not all(os.path.isfile(path) and not os.path.islink(path) for path in paths):  # Never create a missing pair or follow member symlinks.
        raise ValueError("the loaded live data/meta pair must still exist as regular files")  # Recover by loading a valid target.
    original = _read_pair(paths)  # Retain current disk bytes for recovery; intentionally do not compare old hashes.
    staged, replacing = [], False  # Track cleanup and whether disk recovery may be required.
    try:  # Stage both members before touching either live target.
        temporary = [_stage_bytes(path, blob, staged) for path, blob in zip(paths, blobs)]  # Read-verified sibling staging.
        replacing = True  # A failed replacement can require restoring the pair.
        for path, pending in zip(paths, temporary):  # Replace data then its matching metadata, never the sibling save.
            os.replace(pending, path)  # Each member replacement is atomic; the two-file pair is not power-loss atomic.
        if _read_pair(paths) != blobs:  # Verify exact bytes at both real targets before clearing the LED.
            raise OSError("written live data/meta pair failed byte verification")  # Recovery handles corruption/partial writes.
    except Exception as exc:  # Recover caught failures while leaving model/source state uncommitted.
        if replacing:  # Pure staging failures leave original targets untouched.
            try:  # Recovery itself can fail due to filesystem/permission faults.
                _restore_pair(paths, original, staged)  # Restore and verify the pre-write pair held in memory.
                slot_ops.trace("NmsLiveSaveOperations", "write_rolled_back", slot=source["slot"], file_name=source["file_name"])  # No JSON or byte dumps.
            except Exception as recovery:  # Never pretend a two-file write is safe after failed recovery.
                raise LiveSaveRecoveryError("live save failed and recovery failed; data/meta may be inconsistent. Keep NMS closed and restore your independent save-folder copy.") from recovery  # Visible safety instruction.
        raise exc  # Surface the original failed write after verified recovery or untouched staging.
    finally:  # Unique staging files are temporary, not a backup feature.
        for path in staged:  # Consumed paths no longer exist after successful replacement.
            if os.path.exists(path):  # Remove only the files this attempt created.
                try:  # Cleanup faults must not obscure the write/recovery outcome.
                    os.unlink(path)  # Do not touch unrelated files.
                except OSError:  # Preserve the primary outcome and reveal leftover temporary files.
                    slot_ops.error("NmsLiveSaveOperations", "temporary_cleanup_failed", path=path)  # Errors remain visible with debugging off.
    slot_ops.trace("NmsLiveSaveOperations", "live_save_verified", slot=source["slot"], file_name=source["file_name"], context_key=source["context_key"], data_hash=prepared["source"]["data_hash"], meta_hash=prepared["source"]["meta_hash"])  # Emit only verified identities.
    return prepared["source"]  # Controller commits updated source/baseline/LED only after success.
