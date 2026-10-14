# File: test_ui_status_labels.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_ui_status_labels.py
# Purpose: Isolated checks for row-82 status LEDs, exact labels and pane layout; no Qt app or real saves.
import ast  # Execute actual controller/helper code without importing PyQt or app initialization.
import copy  # Keep synthetic source/model fixtures independent.
import hashlib  # Exercise the actual model-baseline fingerprint logic.
import json  # Serialize only synthetic model data in fingerprint checks.
import unittest  # Report real isolated test execution results.
from pathlib import Path  # Resolve the actual project sources.
from types import SimpleNamespace  # Provide explicitly synthetic widget/signal interfaces.

ROOT = Path(__file__).resolve().parent  # All source reads stay inside this project.
GREEN = "fixture-green"  # A synthetic color token tests decisions without pretending to render Qt.


class Signal:  # Record subscriptions without running a Qt event loop.
    # __init__: Start with no connected callbacks.
    def __init__(self):
        self.callbacks = []  # Connections are observable in the isolated host.

    # connect: Match the Qt signal interface used by actual controller initialization.
    def connect(self, callback):
        self.callbacks.append(callback)  # No signal emission or background operation is started.


class Widget:  # Store only widget properties needed by the actual status/helper methods.
    # __init__: Accept QLabel/QWidget constructor forms and initialize fake edit signals.
    def __init__(self, *args):
        self.text = args[0] if args and isinstance(args[0], str) else ""  # Preserve requested literal label text.
        self.style, self.tooltip, self.alignment = "", "", None  # No actual GUI rendering occurs.
        self.textChanged, self.itemChanged = Signal(), Signal()  # Match the four-tab observer interface.

    # setFixedSize: Store the requested LED dimensions.
    def setFixedSize(self, width, height):
        self.size = (width, height)  # Verify both LED widgets use the existing dimensions.

    # setStyleSheet: Capture actual state-dependent color output.
    def setStyleSheet(self, style):
        self.style = style  # Tests inspect the real controller's chosen color.

    # setToolTip: Capture explanatory status text without showing a window.
    def setToolTip(self, text):
        self.tooltip = text  # Tooltips must identify the existing baseline, not promise disk polling.

    # setText: Capture the retained source identity label.
    def setText(self, text):
        self.text = text  # Verify slot, filename and selected context remain visible.

    def font(self):
        return SimpleNamespace(setBold=lambda value: setattr(self, "bold", value))  # Synthetic font property.

    def setFont(self, font):
        self.heading_font = font  # Capture the real helper's applied font.

    def repaint(self):
        pass  # No Qt app or event dispatch in isolated tests.

    # setAlignment: Capture the pane heading's requested left alignment.
    def setAlignment(self, alignment):
        self.alignment = alignment  # Do not simulate pixel geometry or claim visual acceptance.


class Timer:  # Supply the observer interface without scheduling any work.
    # __init__: Create only a synthetic timeout signal.
    def __init__(self, parent):
        self.timeout = Signal()  # Real timer callback binding can be checked safely.

    # start: Record the actual requested interval without starting a background task.
    def start(self, interval):
        self.interval = interval  # No polling of files or real app state occurs.


# host: Compile the real controller class against synthetic widget dependencies and initialize its status fields.
def host():
    tree = ast.parse((ROOT / "NmsLoadController.py").read_text(encoding="utf-8"))  # Actual project controller source.
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "NmsLoadController")  # Exclude imports.
    env = {"QWidget": Widget, "QLabel": Widget, "QTimer": Timer, "GREEN_LED_COLOR": GREEN, "copy": copy, "json": json, "hashlib": hashlib, "slot_ops": SimpleNamespace(trace=lambda *args, **kwargs: None)}  # Isolated interfaces.
    exec(compile(ast.Module(body=[node], type_ignores=[]), "status-fixture", "exec"), env)  # Execute the actual methods.
    controller = env["NmsLoadController"]()  # No MainWindow or PyQt app is constructed.
    controller.model = SimpleNamespace(modelChanged=Signal(), get_data=lambda: {"fixture": True})  # Synthetic editable data.
    for name in ("tab1", "tab2", "tab3", "tab4"):
        setattr(controller, name, SimpleNamespace(text_edit=Widget(), tree_widget=Widget()))  # Four synthetic tab interfaces.
    controller.init_nms_load_state()  # Execute actual widget/state/observer initialization.
    return controller  # Ready for real state-method execution in isolated tests.


class StatusTests(unittest.TestCase):  # Cover state distinction and exact display requirements.
    # test_startup_has_two_red_leds_and_exact_labels: No source must not masquerade as loaded or saved.
    def test_startup_has_two_red_leds_and_exact_labels(self):
        controller = host()  # Actual controller initialization against synthetic widgets.
        self.assertIn("background-color: red", controller.live_save_loaded_indicator.style)  # Nothing loaded.
        self.assertIn("background-color: red", controller.file_changed_indicator.style)  # Nothing established saved.
        self.assertEqual(controller.live_save_loaded_label.text, "Live Save Loaded")  # Exact user wording.
        self.assertEqual(controller.data_has_been_saved_label.text, "Modified Data Saved")  # Exact user wording.
        self.assertEqual(controller.live_save_loaded_indicator.size, (10, 10))  # Existing LED dimensions.
        self.assertEqual(controller.file_changed_indicator.size, (10, 10))  # Same second LED dimensions.

    # test_live_load_edit_and_verified_save_states: Editing turns only Data Has Been Saved red.
    def test_live_load_edit_and_verified_save_states(self):
        controller = host()  # Synthetic initialized app-state interface.
        controller.nms_source = {"source_kind": "live", "context_key": "ExpeditionContext", "slot": 5, "file_name": "save10.hg"}  # Synthetic retained identity.
        controller.nms_data_changed = False  # Existing successful-load transition.
        controller._update_nms_led()  # Execute actual display-state logic.
        self.assertIn(GREEN, controller.live_save_loaded_indicator.style)  # Live context loaded.
        self.assertIn(GREEN, controller.file_changed_indicator.style)  # No edits since load.
        controller._mark_nms_changed("fixture_edit")  # Execute actual normal dirty transition.
        self.assertIn(GREEN, controller.live_save_loaded_indicator.style)  # Editing does not unload the source.
        self.assertIn("background-color: red", controller.file_changed_indicator.style)  # GUI changes are not saved.
        controller.nms_data_changed = False  # Existing verified-save transition; no disk save is performed by this test.
        controller._update_nms_led()  # Reflect that retained application state.
        self.assertIn(GREEN, controller.file_changed_indicator.style)  # Saved-state LED returns green.
        self.assertEqual(controller.nms_source, {"source_kind": "live", "context_key": "ExpeditionContext", "slot": 5, "file_name": "save10.hg"})  # Internal identity preserved without displaying trailing text.
        self.assertFalse(hasattr(controller, "file_changed_label"))  # No extra message label is created.

    # test_backup_state_remains_explicit: Memory-only backup data retains its target but is not called a live-file load.
    def test_backup_state_remains_explicit(self):
        controller = host()  # Synthetic initialized application status.
        controller.nms_source = {"source_kind": "zip", "context_key": "BaseContext", "slot": 1, "file_name": "save.hg"}  # Memory-only backup origin.
        controller.nms_data_changed = True  # Existing conservative backup divergence rule.
        controller._update_nms_led()  # Execute actual display-state logic only.
        self.assertIn("background-color: red", controller.live_save_loaded_indicator.style)  # Not loaded from live disk.
        self.assertIn("background-color: red", controller.file_changed_indicator.style)  # Not yet saved live.
        self.assertEqual(controller.nms_source, {"source_kind": "zip", "context_key": "BaseContext", "slot": 1, "file_name": "save.hg"})  # Future target retained internally.
        self.assertFalse(hasattr(controller, "file_changed_label"))  # No trailing backup/source text is displayed.

    # test_baseline_observer_still_marks_silent_edits: Existing model-change detection remains connected and functional.
    def test_baseline_observer_still_marks_silent_edits(self):
        controller = host()  # Actual controller initialization includes observer bindings.
        controller.nms_source = {"source_kind": "live", "context_key": "BaseContext", "slot": 1, "file_name": "save.hg"}  # Live fixture identity.
        controller.nms_data_changed = False  # Established loaded baseline.
        controller._nms_baseline = controller._nms_fingerprint()  # Actual synthetic-model baseline hash.
        controller._observe_nms_model()  # Matching model is not an edit.
        self.assertFalse(controller.nms_data_changed)  # No spurious dirty state.
        controller.model.get_data = lambda: {"fixture": False}  # Simulate a silent semantic model edit.
        controller._observe_nms_model()  # Execute existing fingerprint-based detection.
        self.assertTrue(controller.nms_data_changed)  # Silent edits remain detected.
        self.assertIn(GREEN, controller.live_save_loaded_indicator.style)  # Still loaded despite the edit.
        self.assertIn("background-color: red", controller.file_changed_indicator.style)  # Unsaved state is explicit.
        self.assertEqual(controller._nms_observer.interval, 1000)  # Existing observer interval is unchanged.

    # test_both_indicators_share_one_line_in_requested_order: Inspect actual main-window layout calls.
    def test_both_indicators_share_one_line_in_requested_order(self):
        tree = ast.parse((ROOT / "BBB_NMS_Save_File_Manipulator.py").read_text(encoding="utf-8"))  # Actual layout source.
        names = []  # Capture widgets added to the same horizontal status layout in source order.
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "file_state_layout" and node.func.attr == "addWidget":
                value = node.args[0]  # Inspect only the existing addWidget calls.
                if isinstance(value, ast.Attribute): names.append((node.lineno, value.attr))  # Preserve call position.
        self.assertEqual([name for line, name in sorted(names)], ["live_save_loaded_indicator", "live_save_loaded_label", "file_changed_indicator", "data_has_been_saved_label"])  # Same line, requested order.

    # test_exact_sync_label_and_left_aligned_pane_headings: Every tab must receive both headings above pane controls.
    def test_exact_sync_label_and_left_aligned_pane_headings(self):
        text = (ROOT / "BaseTabContent.py").read_text(encoding="utf-8")  # Shared label construction source.
        self.assertIn('QLabel("Raw JSON Synched to Node View", self)', text)  # Exact requested wording/spelling.
        self.assertIn('self.tree_synced_label.sizeHint().width()', text)  # Longer label is not kept in its old narrow width.
        tree = ast.parse(text)  # Extract actual heading helper for isolated execution.
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "make_pane_heading")  # No full tab construction.
        env = {"QLabel": Widget, "Qt": SimpleNamespace(AlignLeft="fixture-left")}  # Synthetic alignment constant.
        exec(compile(ast.Module(body=[method], type_ignores=[]), "heading-fixture", "exec"), env)  # Execute actual helper.
        for title in ["Node View", "Raw JSON"]:  # Each heading must use the exact text and explicit alignment.
            heading = env["make_pane_heading"](object(), title)  # Actual helper with synthetic parent.
            self.assertEqual((heading.text, heading.alignment), (title, "fixture-left"))  # No visual rendering claim.
            self.assertTrue(heading.bold)  # Both actual helper-created headings are bold.
        for filename in ["FirstTabContent.py", "SecondTabContent.py", "ThirdTabContent.py", "ForthTabContent.py"]:
            pane = (ROOT / filename).read_text(encoding="utf-8")  # Check actual integration in each tab.
            self.assertEqual(pane.count('left_pane_layout.addWidget(self.make_pane_heading("Node View"))'), 1)  # One left heading.
            self.assertEqual(pane.count('right_pane_layout.addWidget(self.make_pane_heading("Raw JSON"))'), 1)  # One right heading.
            self.assertLess(pane.index('left_pane_layout.addWidget(self.make_pane_heading("Node View"))'), pane.index('left_pane_layout.addLayout(left_buttons_lo)'))  # Heading above controls.
            self.assertLess(pane.index('right_pane_layout.addWidget(self.make_pane_heading("Raw JSON"))'), pane.index('right_pane_layout.addLayout(right_button_layout)'))  # Heading above controls.

    # test_all_other_leds_precede_labels: Background and four sync status pairs must also use LED-first ordering.
    def test_all_other_leds_precede_labels(self):
        specs = [("BBB_NMS_Save_File_Manipulator.py", "status_layout", ["current_task_label", "current_task_info"])]  # Task text has no LED.
        specs += [(filename, "tree_synced_indicator_layout", ["tree_synced_indicator", "tree_synced_label"]) for filename in ["FirstTabContent.py", "SecondTabContent.py", "ThirdTabContent.py", "ForthTabContent.py"]]  # Every tab sync pair.
        for filename, layout_name, expected in specs:  # Inspect actual layout calls rather than reconstructing the UI.
            tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))  # Scoped source-only read.
            calls = []  # Capture pair members in their actual source order.
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == layout_name and node.func.attr == "addWidget":
                    value = node.args[0]  # Each pair consists of named existing widgets.
                    if isinstance(value, ast.Attribute): calls.append((node.lineno, value.attr))  # Preserve call positions.
            self.assertEqual([name for line, name in sorted(calls)], expected, filename)  # LED must precede label.
        source = (ROOT / "NmsLoadController.py").read_text(encoding="utf-8")  # Confirm the trailing message widget is removed.
        self.assertNotIn("self.file_changed_label", source)  # No hidden or populated extra identity label remains.
        self.assertNotIn('identity = "No live save loaded"', source)  # Removed startup status string is not generated.

    def test_task_info_blank_and_explicit_progress(self):
        controller = host()
        controller.current_task_info = Widget()
        controller.set_current_task_info("Loading views…")
        self.assertEqual(controller.current_task_info.text, "Loading views…")
        controller.set_current_task_info()
        self.assertEqual(controller.current_task_info.text, "")
        main = (ROOT / "BBB_NMS_Save_File_Manipulator.py").read_text(encoding="utf-8")
        self.assertIn('QLabel("Current Task Info: ", self)', main)
        self.assertNotIn("self.status_indicator", main)
        self.assertNotIn("background_processing_signal.connect", main)
        base = (ROOT / "BaseTabContent.py").read_text(encoding="utf-8")
        self.assertNotIn("QTimer.singleShot(2000", base)
        controller_source = (ROOT / "NmsLoadController.py").read_text(encoding="utf-8")
        self.assertIn('self.set_current_task_info("Loading views…")', controller_source)
        self.assertIn('self.set_current_task_info("Saving and verifying…")', controller_source)

    # test_loaded_slot_default: Active messages override retained slot/title and clearing restores that exact identity.
    def test_loaded_slot_default(self):
        controller = host()  # Actual controller methods with synthetic widgets.
        controller.current_task_info = Widget()  # No GUI or live save.
        controller.set_current_task_info()  # No load means no default.
        self.assertEqual(controller.current_task_info.text, "")  # Initial field remains blank.
        controller.nms_source = {"slot": 1, "slot_title": "xyz1223"}  # Retained successfully loaded source metadata.
        controller.set_current_task_info()  # Idle displays the selected loaded slot.
        self.assertEqual(controller.current_task_info.text, "Save Loaded: Slot 1 - xyz1223")  # Exact requested format.
        controller.set_current_task_info("Saving and verifying…")  # Important current work takes precedence.
        self.assertEqual(controller.current_task_info.text, "Saving and verifying…")  # Default is temporarily replaced.
        controller.set_current_task_info()  # Work completion restores identity rather than blanks it.
        self.assertEqual(controller.current_task_info.text, "Save Loaded: Slot 1 - xyz1223")  # No history or stale task.
        controller.nms_source = {"slot": 2, "slot_title": ""}  # Empty metadata title is not invented.
        controller.set_current_task_info()  # Updated loaded source supplies the new identity.
        self.assertEqual(controller.current_task_info.text, "Save Loaded: Slot 2")  # Honest titleless default.

    # test_loading_popup_lifetime: Execute the real load method with synthetic services, never real saves or Qt.
    def test_loading_popup_lifetime(self):
        for mode in ("success", "decode_error", "render_error", "cancel", "dialog_error"):
            controller = host()  # Fresh actual controller methods per scenario.
            events, dialogs = [], []  # Observe lifetime order rather than pretend to render pixels.
            controller.enabled = True  # Synthetic window state.
            controller.isEnabled = lambda: controller.enabled  # Match actual window interface.
            controller.setEnabled = lambda value: setattr(controller, "enabled", value)  # Record restored state.
            controller.repaint = lambda: events.append("final-paint")  # Observe final UI refresh ordering.
            controller.set_current_task_info = lambda text="": events.append(text)  # Observe cleanup text.
            source = {"slot": 1, "file_name": "save.hg", "meta_name": "mf_save.hg", "context_key": "BaseContext", "data_path": "synthetic"}  # No file contents.
            owner = self  # Dialog and service callbacks share test assertions.

            class Dialog:  # Synthetic visual interface only, not a GUI acceptance test.
                def __init__(self, text, parent):
                    if mode == "dialog_error": raise ValueError("synthetic dialog failure")  # Exercise setup cleanup.
                    owner.assertEqual(text, "Loading data, please wait…")  # Exact progress text.
                    dialogs.append(self)  # Keep a lifecycle handle.
                    self.visible = False  # Starts hidden.
                def setEnabled(self, value): pass  # No Qt parent inheritance in fixture.
                def show(self): self.visible = True; events.append("show")  # Starts before decoding.
                def accept(self): self.visible = False; events.append("dismiss")  # Transaction completion only.
                def deleteLater(self): events.append("delete")  # No real QObject deletion.

            def decode(*args):  # Actual load method calls this synthetic codec service.
                owner.assertTrue(dialogs[0].visible)  # Popup must be visible during decoding.
                owner.assertTrue(controller._nms_loading)  # Reentrant operations blocked before event pumping.
                events.append("decode")  # Record ordering.
                if mode == "decode_error": raise ValueError("synthetic decode failure")  # No state commit.
                return dict(source)  # Synthetic identity only.

            def commit(value):  # Represents the existing transactional four-tab population boundary.
                owner.assertTrue(dialogs[0].visible)  # Must not dismiss before population.
                owner.assertTrue(controller._nms_loading)  # No early guard release.
                events.extend(["tab1", "tab2", "tab3", "tab4"])  # Record all four population stages.
                if mode == "render_error": raise ValueError("synthetic render failure")  # Exercise finally.
                controller.nms_source = value  # Synthetic successful source commit.

            def process_events(flags):  # Observe pre-decode and final event flushes.
                owner.assertEqual(flags, "exclude-input")  # No unrestricted input pumping added.
                owner.assertTrue(controller._nms_loading)  # Guard remains set through final refresh.
                owner.assertTrue(dialogs[0].visible)  # Progress stays open during both flushes.
                events.append("events")  # Record order.

            env = controller._load_nms_snapshot.__func__.__globals__  # Inject isolated dependencies into actual method.
            env.update({"os": SimpleNamespace(path=SimpleNamespace(isdir=lambda path: True)), "NmsLoadingDialog": Dialog, "QApplication": SimpleNamespace(processEvents=process_events), "QEventLoop": SimpleNamespace(ExcludeUserInputEvents="exclude-input")})  # No GUI import.
            env["slot_ops"] = SimpleNamespace(select_slot_file=lambda *args: None if mode == "cancel" else {"meta": {"name": "xyz1223"}}, decode_record=decode, trace=lambda *args, **kwargs: None)  # No save reads.
            controller._commit_nms_source = commit  # Keep rollback implementation independent from this lifecycle test.
            original_source = controller.nms_source  # Capture previous identity.
            if mode.endswith("error"):
                with self.assertRaises(ValueError): controller._load_nms_snapshot({"slot": 1}, "synthetic-folder", "live")  # Error propagates to existing warning handler.
                self.assertIs(controller.nms_source, original_source)  # Failed load does not commit new identity.
            else:
                result = controller._load_nms_snapshot({"slot": 1}, "synthetic-folder", "live", on_load_confirmed=lambda: events.append("picker-close"))  # Actual load boundary.
                self.assertEqual(result, mode == "success")  # Cancel remains False.
            self.assertTrue(controller.enabled)  # Always restore interaction.
            self.assertFalse(controller._nms_loading)  # Never strand the transaction guard.
            if dialogs:
                self.assertFalse(dialogs[0].visible)  # Success and errors always dismiss progress.
                self.assertLess(events.index("show"), events.index("decode"))  # Popup starts first.
            if mode == "success":
                self.assertEqual(controller.nms_source["slot_title"], "xyz1223")  # Successful load retains its selected metadata title.
                self.assertLess(events.index("picker-close"), events.index("show"))  # Confirmations/picker precede progress.
                self.assertLess(events.index("tab4"), events.index("final-paint"))  # All panes populated before final refresh.
                self.assertLess(events.index("final-paint"), events.index("dismiss"))  # Dismissal follows refresh.
            if mode == "cancel": self.assertEqual(events, [])  # No popup, callback or decode on cancel.

    # test_popup_user_close_is_ignored: Execute actual dialog overrides without importing Qt.
    def test_popup_user_close_is_ignored(self):
        tree = ast.parse((ROOT / "NmsLoadController.py").read_text(encoding="utf-8"))  # Actual popup class.
        node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "NmsLoadingDialog")  # Extract only the class.
        env = {"TextOnlyLoadingDialog": object}  # Synthetic base, no UI.
        exec(compile(ast.Module(body=[node], type_ignores=[]), "popup-fixture", "exec"), env)  # Execute real overrides.
        dialog = env["NmsLoadingDialog"]()  # Synthetic instance.
        ignored = []  # Observe Alt-F4/close request suppression.
        dialog.reject()  # Escape is intentionally a no-op.
        dialog.closeEvent(SimpleNamespace(ignore=lambda: ignored.append(True)))  # Window close is ignored.
        self.assertEqual(ignored, [True])  # Progress cannot be dismissed by the user mid-load.

    # test_python312_grammar_and_crlf: Verify all changed application files without importing the GUI.
    def test_python312_grammar_and_crlf(self):
        for filename in ["NmsLoadController.py", "BBB_NMS_Save_File_Manipulator.py", "BaseTabContent.py", "FirstTabContent.py", "SecondTabContent.py", "ThirdTabContent.py", "ForthTabContent.py", "test_ui_status_labels.py"]:
            payload = (ROOT / filename).read_bytes()  # Read actual scoped source bytes only.
            ast.parse(payload.decode("utf-8"), feature_version=(3, 12))  # Gaming-PC Python grammar.
            self.assertNotIn(b"\n", payload.replace(b"\r\n", b""))  # Preserve consistent Windows CRLF.


if __name__ == "__main__":  # Only explicit isolated fixture verification runs this suite.
    unittest.main(verbosity=2)  # Real execution supplies PASS/failure counts.
