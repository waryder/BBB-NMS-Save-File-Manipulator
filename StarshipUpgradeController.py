# File: StarshipUpgradeController.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\StarshipUpgradeController.py
# Purpose: Share upgrade selection, memory-only commit and result reporting between entry points.
import copy  # Preserve the whole editable context and reject stale dialog selections.
import json  # Read the current integrated reference files without writing app data to disk.
from html import escape  # Ship names and rejection reasons must never become HTML markup.
from PyQt5.QtCore import QEventLoop, Qt  # Explicit Qt constants keep this controller independent of app globals.
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QMessageBox, QTextBrowser, QVBoxLayout  # Existing Qt toolkit.
from WhichStarshipsToUpgradeDialog import WhichStarshipsToUpgradeDialog  # Preserve the existing selection dialog.
from StarshipUpgrade import plan_upgrades, ship_label  # Use one field allowlist and exact-ID counting routine.
from NmsLoadController import NmsLoadingDialog  # Reuse the non-cancellable text-only progress dialog.


# results_html: Render full success, tech-skipped partial success and red whole-ship rejections.
def results_html(results):
    rows, notes = [], []  # Keep the selected-ship list separate from brief rejection explanations.
    labels = {"upgraded": "Upgraded", "unchanged": "Already up to date", "rejected": "Rejected", "partial": "Stats/class applied; tech skipped"}  # Honest status text.
    for result in results:  # Include every selected ship in selection order.
        name = escape(result["name"])  # Escape even names containing angle brackets or quotation marks.
        status = result["status"]  # Do not imply that a refused or unchanged ship was changed.
        if status == "unoccupied":  # Red empty-slot label, without a rejected/unnamed suffix or note.
            rows.append(f'<li><span style="color: red;">{name}</span></li>')  # Exact Slot X - (unoccupied) text.
            continue  # Empty slots never contribute rejection notes.
        if status == "rejected":  # Apply red font to the refused ship name only.
            name = f'<span style="color: red;">{name}</span>'  # Explicit user-requested visual distinction.
            notes.append(f'<li>Ship {result["index"] + 1}: {escape(result["name"])} — {escape(result["reason"])}</li>')  # Brief reason.
        if status == "partial":  # Explain technology-only failures without labeling the entire ship rejected.
            notes.append(f'<li>Ship {result["index"] + 1}: {escape(result["name"])} — Tech skipped: {escape(result["tech_reason"])}</li>')  # Safe brief note.
        rows.append(f'<li>Ship {result["index"] + 1}: {name} — {labels[status]}</li>')  # Identify duplicate or unnamed names by slot.
    body = "<p>Selected starships:</p><ol>" + "".join(rows) + "</ol>"  # One readable results list.
    if notes:  # Successful-only runs must not display an empty Notes heading.
        body += "<p><b>Upgrade notes:</b></p><ul>" + "".join(notes) + "</ul>"  # Put reasons below the ship list.
    return body + "<p>Changes are in the currently loaded app data; saving to game files is separate.</p>"  # No automatic saving.


class StarshipUpgradeResultsDialog(QDialog):  # Scrollable results support up to twelve ships and brief rejection notes.
    # __init__: Build a read-only result report and an ordinary close button.
    def __init__(self, results, parent=None):
        super().__init__(parent)  # Parent the report to the existing main window.
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Match other application dialogs.
        self.setWindowTitle("Starship Upgrade Results")  # Cover successes, unchanged ships and refusals.
        self.resize(620, 430)  # Allow the list and bottom reasons to fit or scroll.
        layout = QVBoxLayout(self)  # Keep the results above the close action.
        self.report = QTextBrowser(self)  # Read-only rich text renders the red rejected ship names.
        self.report.setOpenExternalLinks(False)  # Results must not launch outside content.
        self.report.setHtml(results_html(results))  # Names and reasons are escaped by the shared formatter.
        layout.addWidget(self.report)  # Give the report the available vertical space.
        buttons = QDialogButtonBox(QDialogButtonBox.Ok, self)  # No second upgrade/save action belongs here.
        buttons.accepted.connect(self.accept)  # Close without changing the selected context.
        layout.addWidget(buttons)  # Keep the close action beneath the scrollable notes.


# _load_reference: Read the current upgrade bundle through IniFileManager's source/frozen resource resolver.
def _load_reference(manager, filename):
    path = manager.get_starship_upgrade_reference_path(filename)  # Do not reuse stale persistent legacy reference copies.
    try:  # Keep reference I/O failures brief and ship-specific in the bottom notes.
        with open(path, "r", encoding="utf-8-sig") as handle:  # Read only; no copying or disk-save side effects.
            return json.load(handle)  # The planner validates schema, stat values, classes and item records.
    except OSError as exc:  # Do not dump long operating-system path errors into the result report.
        raise ValueError(f"Reference unavailable: {filename}.") from exc  # Leave the affected ship unchanged.
    except (ValueError, UnicodeError) as exc:  # Corrupt JSON or encoding is an unavailable usable donor.
        raise ValueError(f"Malformed reference: {filename}.") from exc  # Brief per-ship refusal note.


# _selected_indices: Preserve the existing checkbox picker and return no selection on Cancel.
def _selected_indices(ships):
    dialog = WhichStarshipsToUpgradeDialog([ship_label(ship, index) for index, ship in enumerate(ships)])  # Current ownership.
    if dialog.exec_() != QDialog.Accepted:  # Cancel must leave model, dirty state and result UI untouched.
        return []  # No reference read or candidate planning is needed.
    return [checkbox.property("starshipListIdx") for checkbox in dialog.get_selected_items()]  # Existing index contract.


# _checked_context: Refuse pending text edits instead of silently replacing unsynchronized user work.
def _checked_context(window):
    tabs = getattr(window, "_nms_tabs", ())  # The current application exposes all four editing tabs.
    if any(not tab.tree_synced for tab in tabs):  # Any model publication would refresh and overwrite pending raw text.
        raise ValueError("Use Sync from Text Window in each changed tab before upgrading.")  # No silent synchronization.
    context = window.model.get_data()  # This is the active editable Main or Expedition context, not the full codec tree.
    player = context.get("PlayerStateData") if isinstance(context, dict) else None  # Require a shared context.
    ships = player.get("ShipOwnership") if isinstance(player, dict) else None  # Never use the teleport tab's view.
    if not isinstance(ships, list):  # Refuse placeholder/invalid loaded data before showing the picker.
        raise ValueError("No valid ship ownership list is loaded.")  # No model or live-save mutation.
    return copy.deepcopy(context)  # Snapshot the whole context for stale-selection checks and preservation.


# _upgrade_selected: Plan independently and publish one model update only when at least one ship changed.
def _upgrade_selected(window, context, indices):
    ships = context["PlayerStateData"]["ShipOwnership"]  # Read ownership in the currently loaded editable branch.
    manager = window.ini_file_manager  # Follow the application's existing resource resolver object.
    candidate, results = plan_upgrades(ships, indices, lambda filename: _load_reference(manager, filename))  # Per-ship refusal.
    if window.model.get_data() != context:  # A modal event must not apply a selection to a different context/list.
        raise ValueError("Loaded data changed during selection; review it and try again.")  # Leave newer data untouched.
    if candidate != ships:  # All-rejected and already-complete requests are true model/dirty-state no-ops.
        updated = copy.deepcopy(context)  # Retain customisation, build bases, primary ship, cargo and unknown fields.
        updated["PlayerStateData"]["ShipOwnership"] = candidate  # Only the allowlisted ownership changes are new.
        window.model.set_data(updated)  # Existing model signals refresh tabs and mark actual edits dirty.
    return results  # Display actual selected outcomes even when nothing changed.


# run_starship_upgrade: Share selection and result behavior across both historical upgrade entry points.
def run_starship_upgrade(tab):
    window = tab.main_window  # Both entry points refer to the same selected editable whole context.
    if getattr(window, "_nms_loading", False) or getattr(window, "_starship_upgrade_running", False):  # Reentrancy guard.
        return  # Loading/saving and nested selection must not overlap an upgrade transaction.
    window._starship_upgrade_running = True  # Hold the guard across modal picker and result events.
    try:  # Any preflight error produces a warning without a partial model change.
        context = _checked_context(window)  # Never read or write a real save here.
        indices = _selected_indices(context["PlayerStateData"]["ShipOwnership"])  # Preserve existing confirmation.
        if not indices:  # Cancel and empty selection are complete no-ops.
            return  # No popup, reference read, dirty transition or automatic saving.
        was_enabled = window.isEnabled()  # Preserve interaction state before the synchronous upgrade begins.
        progress = None  # Dialog setup errors must also restore the main window.
        window.setEnabled(False)  # Model-refresh event processing must not admit edits during upgrading.
        try:  # Keep progress visible until the results dialog has been prepared.
            progress = NmsLoadingDialog("Upgrading starships, please wait…", window)  # Submit starts the upgrade-progress lifetime.
            progress.setEnabled(True)  # The disabled main window must not prevent child painting.
            progress.show()  # Paint before planning/reference reads and model publication.
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)  # No fixed delay or thread-count guess.
            results = _upgrade_selected(window, context, indices)  # Publish only validated changed candidates.
            window.repaint()  # Include the resulting editor refresh in the progress lifetime.
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)  # Finish layout/paint work before showing results.
            report = StarshipUpgradeResultsDialog(results, window)  # Construct the results before hiding progress.
        finally:  # Errors must not strand progress or disable the main window.
            try:
                if progress is not None:
                    progress.accept()  # Transaction owns completion; user close requests remain ignored.
                    progress.deleteLater()  # Release the temporary QObject when Qt resumes.
            finally:
                window.setEnabled(was_enabled)  # Restore the state for the results or existing error warning.
        report.exec_()  # Progress hands off directly to the existing selected-ship result list.
    except (ValueError, TypeError, KeyError, OSError) as exc:  # Report invalid context/selection/reference I/O.
        QMessageBox.warning(window, "Starship upgrade failed", str(exc))  # Keep current data on planning failures.
    finally:  # Do not leave the upgrade action blocked after cancellation or a reported error.
        window._starship_upgrade_running = False  # Resume normal interactions.
