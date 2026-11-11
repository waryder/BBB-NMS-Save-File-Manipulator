# File: AppPersistentStorage.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\AppPersistentStorage.py
# Purpose: Own the selected application data tree and its executable-adjacent path locator.
import os  # Resolve the current user's proposed parent directory.
import re  # Convert game-provided labels into safe filename suggestions.
import tempfile  # Verify actual writes and atomically persist the locator.
from pathlib import Path  # Keep absolute native paths independent of the working directory.

DATA_NAME = 'BBB NMS SFM Data'  # Preserve the same root name at every location.
LOCATOR_NAME = DATA_NAME + '.path'  # Store only the selected absolute path in this file.
SUBDIRECTORIES = ('Settings', 'Backups/Full NMS Save Backups', 'Backups/Bases',
                  'Backups/Inventories', 'Backups/Contexts', 'Backups/Starships',
                  'Backups/Teleport Endpoints', 'Reference Data', 'Reports', 'Logs', 'Temporary')
_data_root = None  # Never guess a root before startup has validated it.


# is_within: Check containment without requiring Python 3.9's Path.is_relative_to.
def is_within(path, root):
    try:
        path.resolve().relative_to(root.resolve())  # Resolve links before comparing directory boundaries.
        return True  # Equality is also permitted for the data root itself.
    except ValueError:
        return False  # The requested path points outside the selected tree.


# suggested_backup_path: Make a single-component filename from an untrusted in-game label.
def suggested_backup_path(category, label):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(label or 'default'))  # Replace Windows-invalid characters.
    name = name.strip().rstrip('. ')[:120].rstrip('. ') or 'default'  # Bound length and reject dot/blank-only names.
    if re.fullmatch(r'(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', name.split('.')[0]):
        name = '_' + name  # Reserved Windows device names are not ordinary files, even with extensions.
    return data_path('Backups', category, name)  # Only the dialog's default is constrained; users still choose the output.


# application_root: Use the existing executable/source policy without a circular module import.
def application_root():
    from FullLiveSaveBackup import application_root as resolve  # Delay this import until called.
    return resolve()  # Never use the one-file extraction or current working directory.


# data_path: Return a category beneath the validated root, refusing traversal or absolute children.
def data_path(*parts):
    if _data_root is None:  # Fail closed instead of falling back to an old destination.
        raise RuntimeError('Application persistent storage has not been initialized.')
    target = _data_root.joinpath(*parts)  # Resolve only explicitly requested relative categories.
    if not is_within(target, _data_root):  # Reject escaping links and paths.
        raise ValueError('Application data path must stay inside BBB NMS SFM Data.')
    return target  # The root itself is valid when no category was requested.


# check_writable: Verify directory access using a unique disposable sibling, not access flags alone.
def check_writable(directory):
    with os.scandir(directory) as entries:  # Verify listing permission without reading user files.
        next(entries, None)  # Force the directory access while leaving contents untouched.
    with tempfile.TemporaryFile(dir=directory) as probe:  # Automatically remove the probe on close.
        probe.write(b'NMS SFM storage check')  # Exercise actual file creation and writing.
        probe.flush()  # Surface buffered write failures before accepting the directory.


# validate_root: Require an existing correctly named root and complete its writable category tree.
def validate_root(value):
    root = Path(value)  # Interpret the recorded absolute path, never an environment expansion.
    if not root.is_absolute() or root.name != DATA_NAME or not root.is_dir():
        raise ValueError('The saved root must be an existing absolute BBB NMS SFM Data directory.')
    check_writable(root)  # Refuse an inaccessible root before making missing categories.
    for relative in SUBDIRECTORIES:  # Repair missing categories, but never recreate a missing root silently.
        child = root / relative  # Preserve the approved category spelling.
        if not is_within(child, root):  # Do not follow an escaping category junction.
            raise ValueError('A storage subdirectory points outside the selected data root: ' + str(child))
        child.mkdir(parents=True, exist_ok=True)  # Existing files cause an explicit failure.
        check_writable(child)  # A writable root alone does not prove its children are writable.
    return root.absolute()  # Persist a full path without replacing the chosen root with a default.


# read_locator: Read exactly one path value; missing or malformed locator data requires selection.
def read_locator(app_root):
    value = (Path(app_root) / LOCATOR_NAME).read_text(encoding='utf-8-sig').rstrip('\r\n')
    if not value or '\n' in value or '\r' in value:  # Reject extra records rather than guessing.
        raise ValueError('The storage locator must contain one absolute directory path.')
    return validate_root(value)  # Existence, structure and actual access are checked every startup.


# save_locator: Atomically replace and read back the one-value executable-adjacent locator.
def save_locator(app_root, root):
    target = Path(app_root) / LOCATOR_NAME  # The locator never goes into the selected data tree.
    temporary = None  # Retain ownership for cleanup after any failure.
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=app_root,
                                         prefix='.nms-storage-', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)  # The sibling keeps replacement on the same filesystem.
            handle.write(str(root))  # The entire file is one absolute path, with no metadata.
            handle.flush()  # Flush Python's buffer before replacing the current locator.
            os.fsync(handle.fileno())  # Request persistence before reporting the path remembered.
        os.replace(temporary, target)  # Never truncate a previously valid locator on a failed write.
        if target.read_text(encoding='utf-8') != str(root):  # Verify the exact file users will reopen.
            raise OSError('The saved storage locator failed readback verification.')
    finally:
        if temporary is not None and temporary.exists():  # Clean up only this attempt's sibling.
            temporary.unlink()  # Never remove the existing locator on an unsuccessful replacement.


# default_selection: Propose LOCALAPPDATA only when it exists and is actually usable.
def default_selection(app_root):
    value = os.environ.get('LOCALAPPDATA', '')  # Missing environment data must not become the working directory.
    if value and Path(value).is_absolute() and Path(value).is_dir():
        try:
            check_writable(Path(value))  # An existing but protected parent is not a useful default.
            return Path(value) / DATA_NAME  # The picker can still choose a different parent.
        except OSError:
            pass  # Use the application directory as Bill's specified fallback.
    return Path(app_root) / DATA_NAME  # Persistence failure here is reported explicitly, not hidden.


# select_directory: Offer a new-directory name using Qt's file-dialog surface, not create a data file.
def select_directory(initial):
    from PyQt5.QtWidgets import QFileDialog, QDialog  # Only import widgets after QApplication exists.

    class StorageDialog(QFileDialog):  # Permit confirming an existing or not-yet-created named directory.
        # accept: Accept the fixed root name directly; retain ordinary navigation for other directories.
        def accept(self):
            selected = self.selectedFiles()  # Qt supplies the currently typed absolute path.
            if selected and Path(selected[0]).name == DATA_NAME:
                QDialog.accept(self)  # Avoid treating an existing data root as a folder to navigate into.
            else:
                super().accept()  # The caller validates and explains any different typed filename.

    dialog = StorageDialog(None, 'Set App Persistent Storage Directory')  # Bill's exact title.
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Preserve editable prefill and directory acceptance.
    dialog.setOption(QFileDialog.DontConfirmOverwrite, True)  # This operation creates no ordinary file.
    dialog.setAcceptMode(QFileDialog.AcceptSave)  # Provide the requested New File-style name entry.
    dialog.setFileMode(QFileDialog.AnyFile)  # Allow typing a root directory that does not exist yet.
    dialog.setDirectory(str(initial.parent))  # Show the proposed parent rather than an unrelated working directory.
    dialog.selectFile(DATA_NAME)  # Prefill the invariant root directory name.
    dialog.setLabelText(QFileDialog.FileName, 'Directory Name:')  # Explain that no data file is being selected.
    dialog.setLabelText(QFileDialog.Accept, 'Set Directory')  # Use a clear directory action label.
    return dialog.selectedFiles()[0] if dialog.exec_() == QDialog.Accepted else None  # Cancel closes startup.


# locator_failure_text: Explain the actual error and practical remedies, with Bill's exact final line.
def locator_failure_text(app_root, error):
    return ('The app could not save its persistent storage location file:\n' +
            str(Path(app_root) / LOCATOR_NAME) + '\n\n' + str(error) +
            '\n\nRecommended solutions:\n1. Move the app EXE to a user-writable folder, such as a folder in Documents.\n'
            '2. Check folder/file permissions and any read-only or security restrictions.\n'
            '3. Check that the drive is available and has free space, then try again.\n\n'
            'Hit OK to Close the App...')  # Keep the required closing wording exact.


# initialize_storage: Resolve only the locator, offer recovery selection, and publish after persistence succeeds.
def initialize_storage():
    global _data_root  # Share one selected root with all app writers.
    from PyQt5.QtWidgets import QMessageBox  # QApplication has already been created by main().
    _data_root = None  # A failed or cancelled reinitialization must not retain a previous root.
    app_root = application_root()  # Keep the locator beside the delivered executable or source app.
    try:
        root = read_locator(app_root)  # Do not search either default root for existing user data.
    except (OSError, ValueError) as error:
        if (app_root / LOCATOR_NAME).exists():  # Missing locator is normal first use, not an error alert.
            QMessageBox.warning(None, 'Persistent Storage Unavailable', str(error))  # Explain why reselection is needed.
        root = None  # Default paths only prefill the picker; they never silently select storage.
    while root is None:  # Permit correcting a rejected selection without starting the editor.
        selected = select_directory(default_selection(app_root))  # Use the exact approved proposal rules.
        if selected is None:  # Cancel means no editor startup and no locator update.
            return False
        try:
            candidate = Path(selected)  # Never reinterpret an arbitrary filename as a different root.
            if not candidate.is_absolute() or candidate.name != DATA_NAME:
                raise ValueError('Choose a directory named exactly ' + DATA_NAME + '.')
            candidate.mkdir(parents=True, exist_ok=True)  # Explicit user selection authorizes creating this root.
            root = validate_root(candidate)  # Require usable categories before recording it.
        except (OSError, ValueError) as error:
            QMessageBox.warning(None, 'Persistent Storage Unavailable', str(error))  # Let the user choose another parent.
    try:
        save_locator(app_root, root)  # Also verify the executable directory can persist the locator on subsequent runs.
    except (OSError, ValueError) as error:
        QMessageBox.critical(None, 'Cannot Save Persistent Storage Location',
                             locator_failure_text(app_root, error), QMessageBox.Ok)  # OK dismisses then startup exits.
        return False  # Never claim the root was remembered when locator writing failed.
    _data_root = root  # Publish only after directory and locator verification both succeeded.
    return True  # The settings manager may now safely initialize inside the selected tree.
