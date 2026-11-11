# File: TabLeaveGuard.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\TabLeaveGuard.py
# Purpose: Row 450. When the user leaves a tab (mouse or keyboard) whose Raw JSON is not synced to Node View,
#          ask Sync / Abandon / Cancel so unsynced text is never discarded silently by another tab's refresh.

from imports import *  # Shared Qt names used across the application.

DEBUG_ENABLED = False  # Global switch for this module's non-error traces.
DEBUG_PREFIX = '[BBB-NMS-SFM/TabLeaveGuard]'  # Project/file prefix for every trace line.
POPUP_TITLE = 'Unsynced Raw JSON'  # Capitalized popup title; wording pending Bill's approval.


# trace: Print a gated diagnostic line with the project/file prefix.
def trace(message):
    if DEBUG_ENABLED:  # Non-error traces stay silent unless enabled.
        print(f'{DEBUG_PREFIX} {message}')  # Matches the existing stdout tracing style.


# install_tab_leave_guard: Remember the current tab and check every later tab change.
def install_tab_leave_guard(window):
    window._guard_previous_index = window.tabs.currentIndex()  # The tab the user is on now.
    window._guard_reverting = False  # True only while the guard moves the user back.
    window.tabs.currentChanged.connect(lambda index: on_tab_changed(window, index))  # Fires for mouse and keyboard.


# on_tab_changed: After Qt switches tabs, resolve any unsynced Raw JSON left on the previous tab.
def on_tab_changed(window, index):
    if window._guard_reverting:  # Ignore the guard's own move back.
        return
    previous_index = window._guard_previous_index  # The tab the user just left.
    previous_tab = window.tabs.widget(previous_index)  # None if that tab no longer exists.
    if previous_tab is None or getattr(previous_tab, 'tree_synced', True):  # Nothing pending there.
        window._guard_previous_index = index  # Accept the switch.
        return
    if resolve_unsynced_tab(window, previous_tab, window.tabs.tabText(previous_index)):  # Synced or abandoned.
        window._guard_previous_index = index  # Accept the switch.
    else:
        revert_to_tab(window, previous_index)  # Cancel or failed sync: stay on the previous tab.


# resolve_unsynced_tab: Ask the user and act; True only when the user may leave the tab.
def resolve_unsynced_tab(window, tab, tab_name):
    choice = ask_sync_abandon_cancel(window, tab_name)  # Sync, Abandon or Cancel.
    trace(f'leaving {tab_name}: choice={choice}')  # Gated decision trace; never dumps JSON.
    if choice == 'sync':  # Run that tab's existing sync.
        return tab.sync_tree_from_text_window() is True  # Switch only if the edits really reached the data.
    if choice == 'abandon':  # Discard this tab's pending text only.
        abandon_raw_json_edits(tab)  # Reload Raw JSON from the app data.
        return True  # The tab is consistent again.
    return False  # Cancel, Escape or closing the popup keeps the user on the tab.


# ask_sync_abandon_cancel: Show the three-choice popup; returns 'sync', 'abandon' or 'cancel'.
def ask_sync_abandon_cancel(window, tab_name):
    box = QMessageBox(window)  # Modal to the main window.
    box.setIcon(QMessageBox.Warning)  # Pending edits are at risk.
    box.setWindowTitle(POPUP_TITLE)  # Capitalized title.
    box.setText(f'The Raw JSON on the {tab_name} tab has edits that are not synced to Node View.')
    box.setInformativeText('Sync: apply the edits now. You stay on the tab if they cannot be applied.\n'
                           'Abandon: discard the edits and reload the Raw JSON from the app data.\n'
                           'Cancel: stay on the tab.')  # Explain each button.
    sync_button = box.addButton('Sync', QMessageBox.AcceptRole)  # Apply the pending edits.
    abandon_button = box.addButton('Abandon', QMessageBox.DestructiveRole)  # Discard the pending edits.
    cancel_button = box.addButton('Cancel', QMessageBox.RejectRole)  # Stay on the tab.
    box.setDefaultButton(cancel_button)  # Enter never discards or applies by accident.
    box.setEscapeButton(cancel_button)  # Escape and closing the popup mean Cancel.
    box.exec_()  # Wait for the user's choice.
    clicked = box.clickedButton()  # The button actually pressed.
    return 'sync' if clicked is sync_button else 'abandon' if clicked is abandon_button else 'cancel'


# abandon_raw_json_edits: Reload only this tab's Raw JSON from the app data and set its light green.
def abandon_raw_json_edits(tab):
    tab.blockSignals()  # Stop the reload from marking the text as edited again.
    try:
        tab.update_text_widget_from_model()  # Existing per-tab reload from the app data.
    finally:
        tab.unblockSignals()  # Always restore normal signal handling.
    tab.update_tree_synced_indicator(True)  # Text and Node View now match the app data.


# revert_to_tab: Move the user back to the tab they tried to leave, without re-running the guard.
def revert_to_tab(window, index):
    window._guard_reverting = True  # Suppress the guard for this programmatic change.
    try:
        window.tabs.setCurrentIndex(index)  # Back to the tab that still holds the pending edits.
    finally:
        window._guard_reverting = False  # Resume guarding real user tab changes.
