# File: FullLiveSaveBackup.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\FullLiveSaveBackup.py
# Purpose: Plan and verify full NMS directory copies; no writes before explicit Save consent.
import datetime  # Name each independent backup using local time.
import hashlib  # Verify copied file contents rather than trusting copy completion.
import os  # Inspect directories without following links.
import re  # Build Windows-safe source-derived backup names.
import shutil  # Copy ordinary files and query destination free space.
import stat  # Reject links, junctions and nonordinary filesystem entries.
import sys  # Distinguish source execution from a packaged executable.
from dataclasses import dataclass, replace  # Keep the reviewed proposal immutable; derive internal I/O paths.
from pathlib import Path  # Resolve native Windows paths on the machine running the app.


@dataclass(frozen=True)
class BackupEntry:  # A source entry and its preflight identity, never save JSON.
    relative: str  # Preserve the original relative directory structure.
    directory: bool  # Empty directories are copied too.
    size: int  # Logical file bytes for the estimated MB calculation.
    modified: int  # Detect source changes during confirmation or copying.
    device: int  # Detect file replacement even when size/time happen to match.
    inode: int  # Retain the filesystem file identity where available.


@dataclass(frozen=True)
class BackupPlan:  # The exact source, destination and inventory approved by Save.
    source: Path  # Complete NMS root, not just the selected game slot.
    destination: Path  # Fresh timestamp-named directory under the application root.
    entries: tuple  # Immutable inventory containing directories and ordinary files.
    total_bytes: int  # Logical payload size, not a guarantee of physical allocation.
    free_bytes: int  # Destination-volume free space at confirmation time.


# _io_path: Use extended-length Windows paths internally without changing displayed backup paths.
def _io_path(path):
    if os.name != 'nt':  # Other platforms retain their native filesystem paths.
        return Path(path)  # No Windows prefix outside Windows.
    text = os.fspath(path)  # Windows filesystem APIs require a Unicode path string.
    if text.startswith('\\\\?\\'):  # Preserve an already extended path without doubling the prefix.
        return Path(text)  # UNC and drive-letter extended forms are both already usable.
    text = os.path.abspath(text)  # Normalize relative components before disabling Windows path parsing.
    if text.startswith('\\\\'):  # Network paths require the extended UNC namespace.
        return Path('\\\\?\\UNC\\' + text[2:])  # Preserve the server, share and remaining components.
    return Path('\\\\?\\' + text)  # Request extended-length handling for an absolute drive path.


# application_root: Keep persistent backups beside the source app or packaged executable.
def application_root():
    if getattr(sys, 'frozen', False):  # Never write into PyInstaller's extraction directory.
        return Path(sys.executable).resolve().parent  # Packaged application root.
    return Path(__file__).resolve().parent  # Source application root, independent of working directory.


# source_root: Expand the Open dialog's account folder to its containing live NMS root.
def source_root(selected_folder):
    if not selected_folder:  # Never interpret an empty selection as the current directory.
        raise ValueError('No NMS save folder is available. Use File > Open NMS Save File to select it.')
    selected = Path(selected_folder).absolute()  # Keep the full native path in confirmation.
    source = selected.parent if selected.name.lower().startswith('st_') else selected  # Include every account.
    if source.name.lower() != 'nms' or not _io_path(source).is_dir():  # Do not unexpectedly copy an arbitrary parent.
        raise ValueError('Select the live st_* folder inside HelloGames\\NMS in File > Open NMS Save File.')
    return source  # The copied contents include st_* directories and any root files.


# _checked_stat: Refuse reparse points/links instead of following them outside the chosen source.
def _checked_stat(path):
    info = path.lstat()  # Inspect the entry itself, not its link target.
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:  # Windows reparse flag.
        raise ValueError(f'Linked or reparse-point entries cannot be backed up safely: {path}')
    if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):  # Only normal files/directories.
        raise ValueError(f'Unsupported filesystem entry: {path}')
    return info  # Fail rather than silently omit data.


# _entry: Record the complete relative identity used for stale-source checks.
def _entry(path, source):
    info = _checked_stat(path)  # Reject unsafe or unsupported entries.
    directory = stat.S_ISDIR(info.st_mode)  # Preserve even empty directories.
    return BackupEntry(str(path.relative_to(source)), directory, 0 if directory else info.st_size,
                       0 if directory else info.st_mtime_ns, info.st_dev, info.st_ino)  # Ignore directory mtime only.


# inventory: Enumerate every ordinary source entry without decoding saves or writing files.
def inventory(source):
    source = _io_path(source)  # Traverse long source paths consistently, preserving relative entry names.
    _checked_stat(source)  # Refuse a linked root before traversal.
    entries, pending = [], [source]  # Explicit traversal makes errors propagate, never silent omissions.
    while pending:  # Visit every directory exactly once.
        folder = pending.pop()  # Directory links are rejected by _entry.
        with os.scandir(folder) as listing:  # Permission errors abort the proposal.
            paths = sorted((Path(item.path) for item in listing), key=lambda p: p.name)  # Stable order.
        for path in paths:  # Include hidden files and empty directories without filters.
            entry = _entry(path, source)  # Capture file metadata for later revalidation.
            entries.append(entry)  # Retain exact relative names.
            if entry.directory:
                pending.append(path)  # Enumerate its children separately.
    return tuple(sorted(entries, key=lambda entry: entry.relative))  # Immutable deterministic inventory.


# _separate_paths: Refuse recursive output or a destination alias into the live source.
def _separate_paths(source, destination):
    source, destination = _io_path(source).resolve(), _io_path(destination).resolve()  # Compare aliases in one namespace.
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Backup source and destination must be separate, nonoverlapping directories.')


# _free_space: Query the destination volume even before its backup directory exists.
def _free_space(destination):
    existing = _io_path(destination)  # Query long destinations through the same filesystem namespace.
    while not existing.exists():
        if existing.parent == existing:  # An unavailable drive must not look like writable free space.
            raise ValueError(f'Backup destination drive is unavailable: {destination}')
        existing = existing.parent  # No directories are created during preflight.
    return shutil.disk_usage(existing).free  # Query the volume actually containing the destination.


# _backup_prefix: Use the same generic backup label on every user's system.
def _backup_prefix(source):
    return 'NMS_SFM_Backup_AppData_Roaming_HelloGames_NMS'  # Keep usernames out of new backup directory names.


# plan_backup: Calculate the exact proposed paths and estimated disk usage without writes.
def plan_backup(selected_folder, app_root=None, now=None):
    source = source_root(selected_folder)  # The same chosen account expands to the full NMS tree.
    root = Path(app_root) if app_root is not None else application_root()  # Test injection never changes production roots.
    stamp = (now or datetime.datetime.now()).strftime('%Y_%m_%d_%H_%M_%S')  # Match the BAT timestamp.
    destination = root.absolute() / 'Full NMS Save Backups' / f'{_backup_prefix(source)}_{stamp}'  # Fresh sibling backups.
    _separate_paths(source, destination)  # Refuse output within the source before scanning it.
    if os.path.lexists(_io_path(destination)):  # Never merge into an existing backup or follow an existing link.
        raise FileExistsError(f'Backup destination already exists; retry in a moment: {destination}')
    entries = inventory(source)  # Read-only metadata inspection before Save/Cancel.
    total, free = sum(entry.size for entry in entries), _free_space(destination)  # Estimate bytes on destination volume.
    if total > free:  # Refuse a known space deficit before offering Save.
        raise OSError('Not enough free disk space for a full NMS backup.')
    return BackupPlan(source, destination, entries, total, free)  # No directories/files created.


# confirmation_text: Show actual Windows paths and decimal MB estimates in Bill's requested wording.
def confirmation_text(plan):
    used, remaining = plan.total_bytes / 1000000, (plan.free_bytes - plan.total_bytes) / 1000000  # Decimal MB.
    return (f'About to copy the entire directory from:\n{plan.source}\n\n'
            f'into new directory:\n{plan.destination}\n\n'
            f'This will result in {used:,.2f} MB new disk usage leaving you {remaining:,.2f} MB free. Proceed?')  # Runtime paths and decimal MB values.


# _digest: Stream file bytes without loading an entire save folder into memory.
def _digest(path):
    result = hashlib.sha256()  # Verify copied bytes independently of timestamps.
    with path.open('rb') as handle:  # Source and destination are read-only here.
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)  # Bounded memory even for large cache files.
    return result.digest()  # No save contents are logged or decoded.


# _copy_entry: Preserve relative structure and file metadata, verifying every copied file.
def _copy_entry(plan, entry):
    source, target = plan.source / entry.relative, plan.destination / entry.relative  # Exact reviewed relative paths.
    if entry.directory:  # Empty directories must exist in the resulting backup.
        target.mkdir(parents=True, exist_ok=True)  # Only inside the newly reserved destination.
        return  # Directory content is handled by separate inventory entries.
    if _entry(source, plan.source) != entry:  # Catch replacement, type or size/time changes before reading.
        raise ValueError(f'Source changed before copying: {source}')
    before = _digest(source)  # Snapshot the source content before its copy.
    target.parent.mkdir(parents=True, exist_ok=True)  # Preserve parent paths for file entries.
    shutil.copy2(source, target, follow_symlinks=False)  # No source writes, deletions or save re-encoding.
    _checked_stat(target)  # Do not accept a link copied after a concurrent source replacement.
    if _digest(target) != before or _digest(source) != before or _entry(source, plan.source) != entry:
        raise ValueError(f'File copy verification or source-stability check failed: {source}')  # No false success.


# _validate_plan: Recheck the approved source and destination before creating any output.
def _validate_plan(plan):
    _separate_paths(plan.source, plan.destination)  # Recheck aliases changed while confirmation was open.
    if os.path.lexists(_io_path(plan.destination)):  # Preserve any new backup created after preflight.
        raise FileExistsError(f'Backup destination already exists: {plan.destination}')
    if inventory(plan.source) != plan.entries:  # Do not copy stale contents after a long confirmation delay.
        raise ValueError('Source contents changed during confirmation. Retry Full Live Save Backup.')
    if _free_space(plan.destination) < plan.total_bytes:  # Other processes may consume disk space during confirmation.
        raise OSError('Not enough free disk space remains for the full backup.')


# execute_backup: Copy only after Save consent; clean up only our own incomplete destination on failure.
def execute_backup(plan, confirmed: object = False):
    if confirmed is not True:  # A truthy string is not explicit authorization.
        raise PermissionError('Full live backup requires explicit Save confirmation.')
    _validate_plan(plan)  # No mkdir or writes before all preflight checks pass.
    display_destination = str(plan.destination)  # Keep the reviewed ordinary path for success reporting.
    plan = replace(plan, source=_io_path(plan.source), destination=_io_path(plan.destination))  # Prefix all copy/verification/cleanup I/O.
    plan.destination.parent.mkdir(parents=True, exist_ok=True)  # Create Full NMS Save Backups only after Save.
    plan.destination.mkdir()  # Exclusive reservation; never merge into another backup.
    try:  # Own this exact new destination from this point onward.
        for entry in plan.entries:
            _copy_entry(plan, entry)  # Verify each copied file, including hidden/cache content.
        if inventory(plan.source) != plan.entries:  # Additions/deletions during copying must not go unnoticed.
            raise ValueError('Source changed during copying; no complete backup was retained.')
    except Exception as exc:
        try:
            shutil.rmtree(plan.destination)  # Remove only this operation's incomplete backup.
        except Exception as cleanup:
            raise OSError(f'Backup failed: {exc}. Incomplete backup remains at {plan.destination}: {cleanup}') from exc
        raise  # Keep existing backups and original live files untouched.
    return display_destination  # Report the ordinary path only after copy and stability checks pass.
