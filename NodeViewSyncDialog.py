# File: NodeViewSyncDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\NodeViewSyncDialog.py
# Purpose: Display a text-only node-sync processing notice; no data operations.
from imports import *  # Reuse the application's Qt and drawing namespaces.
from contextlib import contextmanager  # Express popup ownership with an explicit with-block.


# node_view_sync_progress: The outermost operation owns one popup; nested sync calls only reuse it.
@contextmanager
def node_view_sync_progress(window):
    if getattr(window, '_node_view_sync_progress', None) is not None:  # Another enclosing operation already owns the notice.
        yield  # Run the nested operation without opening or closing another popup.
        return  # Only the original owner may dismiss it.
    progress = NodeViewSyncDialog(window)  # Create one notice for the whole operation, shared across tabs.
    window._node_view_sync_progress = progress  # Publish ownership before any Qt events are processed.
    try:
        progress.show()  # No nested modal exec loop.
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)  # Paint immediately before the caller begins work.
        yield  # Keep the notice visible until all work inside the outer with-block returns.
    finally:
        try:
            progress.finish()  # Normal completion and exceptions share one dismissal path.
        finally:
            window._node_view_sync_progress = None  # Release ownership even if dismissal fails.


class NodeViewSyncDialog(QDialog):
    # __init__: Show the exact requested status text without an animation.
    def __init__(self, parent=None):
        super().__init__(parent)  # Associate modality with the main application window.
        self.setWindowTitle('Processing')  # Keep the title short.
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)  # No close/cancel control during sync.
        self.setWindowModality(Qt.WindowModal)  # Prevent user edits while existing event processing runs.
        layout = QHBoxLayout(self)  # One horizontal row.
        layout.setContentsMargins(20, 16, 20, 16)  # Give the processing text comfortable space.
        layout.setSpacing(14)  # Retain the existing layout spacing.
        message = QLabel('Processing the Node View synch. This can take a few seconds\nafter the Node View appears to update...', self)  # Break after seconds, as requested.
        message.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Keep both lines left aligned.
        layout.addWidget(message, 0, Qt.AlignVCenter)  # Retain the existing vertical placement.
        self.setFixedSize(self.sizeHint())  # No resize handle for this small status popup.

    # reject: Ignore Escape; the sync operation owns dismissal through its finally block.
    def reject(self):
        return  # Never imply cancellation while processing continues.

    # finish: Dismiss only when the synchronous operation has returned or raised.
    def finish(self):
        self.accept()  # End the processing popup without any data action.
        self.deleteLater()  # Let Qt dispose of the dialog safely.
