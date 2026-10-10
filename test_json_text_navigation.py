# File: test_json_text_navigation.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_json_text_navigation.py
# Purpose: Offscreen regression tests using actual tree builders and Qt navigation.
import ast  # Extract production code without unrelated application startup side effects.
import copy  # Compare independent before/after fixtures.
import json  # Supply displayed JSON fixtures.
import os  # Force Qt to stay offscreen before importing it.
from pathlib import Path  # Read only the explicitly tested source files.
import unittest  # Run deterministic tests without additional packages.
from unittest.mock import patch  # Prevent dialogs and catch forbidden writes.
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Never create a visible desktop window.
from PyQt5 import QtCore, QtGui, QtWidgets  # Exercise real Qt widgets/cursors.
from CustomTextEdit import CustomTextEdit  # Preserve real current-line highlighting.

ROOT = Path(__file__).resolve().parent  # Locate the authoritative source beside this test.
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])  # Offscreen app only.

class QuietLogger:
    # __getattr__: suppress existing verbose save-data logging in isolated fixtures.
    def __getattr__(self, name):
        return lambda *args, **kwargs: None  # Never print fixture JSON.

# source_class: compile a production class with only its explicitly required dependencies.
def source_class(filename, classname, methods=None, extra=None):
    tree = ast.parse((ROOT / filename).read_text(encoding='utf-8'))  # Read the exact source.
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == classname)  # Find class.
    if methods is not None:
        cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in methods]  # Keep real methods.
        cls.bases = []  # Use fixture hosts instead of initializing the whole application.
    namespace = {}  # Isolate symbols from unrelated application imports.
    for module in (QtCore, QtGui, QtWidgets):
        namespace.update({name: getattr(module, name) for name in dir(module)})  # Real Qt APIs.
    namespace.update(json=json, copy=copy, logger=QuietLogger(), QT_DATA_SAVE_NODES_DATA_STRUCT=QtCore.Qt.UserRole,
                     QT_DATA_LINE_COUNT=QtCore.Qt.UserRole + 1, QT_DATA_IS_BASE=QtCore.Qt.UserRole + 2,
                     get_new_QTreeWidgetItem=QtWidgets.QTreeWidgetItem, GALAXIES={0: 'Euclid'},
                     GALAXY_FROM_GALACTIC_ADDR_IDX=0, SYSTEM_FROM_GALACTIC_ADDR_IDX=1,
                     get_galaxy_system_planet_from_full_addr=lambda value: ['00', '001', '0'])  # Fixture-only label helpers.
    if (ROOT / 'JsonTextNavigation.py').exists():
        import JsonTextNavigation  # Load the replacement once it exists.
        namespace.update({name: getattr(JsonTextNavigation, name) for name in dir(JsonTextNavigation) if not name.startswith('_')})  # Shared production helpers.
    namespace.update(extra or {})  # Inject any explicit host dependency.
    exec(compile(ast.Module(body=[cls], type_ignores=[]), filename, 'exec'), namespace)  # Compile unchanged production bodies.
    return namespace[classname]  # Return the actual tested class.

TREE_CLASS = source_class('CustomTreeWidget.py', 'CustomTreeWidget')  # Real shared tree/handler.

class Host(QtWidgets.QWidget):
    # __init__: supply a minimal tab host without model/disk startup.
    def __init__(self, tabname):
        super().__init__()  # Give the tree a valid Qt parent.
        cls = source_class(tabname + '.py', tabname, {'populate_tree_from_json'})  # Actual builder.
        self.populate_tree_from_json = cls.populate_tree_from_json.__get__(self)  # Bind to fixture host.
        self.view = type('View', (), {'get_storage_label_name_deep_copy': lambda *a, **k: 'Fixture',
                                    'get_teleport_endpoint_label_name_deep_copy': lambda *a, **k: 'Fixture'})()  # Labels only.
        self.tree_widget = TREE_CLASS(self)  # Real shared tree widget.
        self.text_edit = CustomTextEdit(self)  # Real editor/current-line highlight.
        self.bottom_left_label = QtWidgets.QLabel()  # Builder count destination.
        self.tree_synced = True  # Formatting edits must not rely on this flag.

    # load: build tree and display the same fixture with caller-controlled layout.
    def load(self, data, text=None):
        self.tree_widget.clear()  # Exercise real tree replacement.
        self.populate_tree_from_json(data)  # Run production builder.
        self.text_edit.setPlainText(text if text is not None else json.dumps(data, indent=4))  # Test setup only.

# find_property: identify a fixture property through stored structural data, never labels.
def find_property(host, key):
    pending = [host.tree_widget.topLevelItem(0)]  # Traverse the actual populated tree.
    while pending:
        node = pending.pop()  # Visit next node.
        if isinstance(node.data(0, QtCore.Qt.UserRole), tuple) and node.child(0).data(0, QtCore.Qt.UserRole) == key:
            return node  # Return exact tuple/property node.
        pending.extend(node.child(i) for i in range(node.childCount()))  # Visit children.
    raise AssertionError('Fixture property missing')  # Fail rather than infer a node.

class NavigationRegression(unittest.TestCase):
    # test_empty_container_drift: reproduce the actual wrong-line symptom in the Bases builder/handler.
    def test_empty_container_drift(self):
        host = Host('FirstTabContent')  # Use the actual Bases builder.
        data = {**{str(i): [] if i % 2 else {} for i in range(20)}, 'target': 42}  # Trigger cumulative drift.
        host.load(data)  # Build actual Qt nodes and text.
        host.tree_widget.highlight_in_text_box(find_property(host, 'target'))  # Invoke production navigation.
        self.assertEqual(host.text_edit.textCursor().selectedText().strip(), '"target": 42')  # Assert exact symptom.
        host.deleteLater()  # Release offscreen fixture.

from JsonTextNavigation import JsonNavigationError, JsonSourceMap, QT_DATA_JSON_LOCATION, same_json  # Shared production mapper.
import random  # Deterministic broad JSON fixtures.
import time  # Measure actual large-text navigation latency.
from unittest.mock import Mock  # Catch all forbidden synchronization/model calls.

TABS = ('FirstTabContent', 'SecondTabContent', 'ThirdTabContent', 'ForthTabContent')  # Every integration.

# annotated_text: independent serializer/oracle marks each emitted key/value token before appending it.
def annotated_text(data, compact=False):
    chunks, positions = [], {}  # Text pieces and independently expected code-point starts.
    offset = 0  # Count actual emitted characters.
    # emit: append an exact token and track its length.
    def emit(token):
        nonlocal offset  # Share emitted position with the oracle.
        chunks.append(token)  # Append only test source text.
        offset += len(token)  # Advance independent position.
    # value: render one standard JSON value and mark its precise position.
    def value(item, path):
        positions[(path, 'value')] = offset  # Oracle value start.
        if isinstance(item, dict):  # Objects include distinct key/value starts.
            emit('{')  # Emit opening token.
            for index, (key, child) in enumerate(item.items()):  # Preserve fixture member order.
                emit((',' if index else '') + ('' if compact else '\n\n  '))  # Deliberately irregular valid whitespace.
                positions[(path + (key,), 'key')] = offset  # Oracle key start.
                emit(json.dumps(key, ensure_ascii=False) + (':' if compact else ' \n : \n\t'))  # Put values on separate lines.
                value(child, path + (key,))  # Render exact property occurrence.
            emit('}')  # Emit object end.
        elif isinstance(item, list):  # Identical entries still receive distinct integer indexes.
            emit('[')  # Emit array opening.
            for index, child in enumerate(item):  # Visit in order.
                emit((',' if index else '') + ('' if compact else '\n\t'))  # Varied valid layout.
                value(child, path + (index,))  # Mark exact occurrence.
            emit(']')  # Emit array end.
        else:
            emit(json.dumps(item, ensure_ascii=False))  # Standard escaped scalar token.
    emit(' \n')  # Leading whitespace must not shift matching incorrectly.
    value(data, ())  # Render the actual root.
    emit('\n ')  # Trailing whitespace is valid.
    return ''.join(chunks), positions  # Return oracle with actual test document.

# all_nodes: traverse actual populated Qt nodes, including artificial property/key/value nodes.
def all_nodes(host):
    pending = [host.tree_widget.topLevelItem(0)]  # Start at root.
    while pending:
        node = pending.pop()  # Visit next occurrence.
        yield node  # Expose the actual Qt node.
        pending.extend(node.child(index) for index in range(node.childCount()))  # Include every representation.

class AllTabNavigation(unittest.TestCase):
    # setUp: isolate each test's real offscreen hosts.
    def setUp(self):
        self.hosts = []  # Retain widgets until test cleanup.

    # tearDown: dispose fixtures without ever showing them.
    def tearDown(self):
        for host in self.hosts:  # All test-created hosts only.
            host.deleteLater()  # Qt-managed deletion, not application shutdown.
        APP.processEvents()  # Deliver pending offscreen cleanup.

    # host: construct one isolated tab and populate it with synthetic data.
    def host(self, name, data, text=None):
        host = Host(name)  # Actual tab builder and shared tree handler.
        host.load(data, text)  # Populate without filesystem data.
        self.hosts.append(host)  # Retain Qt ownership.
        return host  # Return fixture host.

    # check_all: verify exact resolver offset, selected line, current-line background and zero mutation.
    def check_all(self, host, positions):
        text = host.text_edit.toPlainText()  # Actual displayed text is authoritative.
        state = host.tree_widget.json_navigation  # Production state, independent of model.
        before = copy.deepcopy(state.snapshot)  # Confirm navigation does not mutate its baseline.
        changed = Mock()  # Text changes must not occur from highlighting.
        host.text_edit.textChanged.connect(changed)  # Real signal monitoring.
        for node in all_nodes(host):  # Check tuple/key/scalar/container representations.
            location = node.data(0, QT_DATA_JSON_LOCATION)  # Explicit target metadata.
            path, kind = tuple(location['path']), location['kind']  # Preserve typed segments.
            start = positions[(path, kind)]  # Independent token-offset oracle.
            expected = len(text[:start].encode('utf-16-le')) // 2  # Qt coordinate from test source.
            self.assertEqual(state.resolve(host.tree_widget, node, text), expected)  # Exact occurrence.
            self.assertTrue(host.tree_widget.highlight_in_text_box(node))  # Exercise shared handler.
            block = host.text_edit.document().findBlock(expected)  # Independently expected displayed line.
            self.assertEqual(host.text_edit.textCursor().selectedText(), block.text())  # Familiar full-line selection.
            self.assertEqual(host.text_edit.extraSelections()[0].cursor.blockNumber(), block.blockNumber())  # Current-line background.
            self.assertEqual(host.text_edit.toPlainText(), text)  # Unsynchronized formatting retained byte-for-character.
        changed.assert_not_called()  # No textChanged emission from navigation.
        self.assertEqual(state.snapshot, before)  # No snapshot/model write-through.
        host.text_edit.textChanged.disconnect(changed)  # Remove fixture observer.

    # test_every_representation_all_tabs: check repeated objects, nested paths and escape-heavy strings.
    def test_every_representation_all_tabs(self):
        special = '😀 é 中文 "quoted" \\ path\n/w /w {} []'  # Include non-BMP and structural-looking string contents.
        entry = {'Name': 'Fixture', 'GalacticAddress': 0, 'Message': special, 'emptyList': [], 'emptyDict': {},
                 'nested': {'0': [False, None, 12.5, {'same': 42}, {'same': 42}]}}  # String key vs integer index.
        data = [entry, copy.deepcopy(entry)]  # Identical array entries must resolve to distinct occurrences.
        for name in TABS:  # Every production builder.
            for compact in (False, True):  # Multiline and compact same-line JSON.
                with self.subTest(tab=name, compact=compact):
                    text, positions = annotated_text(data, compact)  # Independent offset oracle.
                    host = self.host(name, data, text)  # Actual integration.
                    self.assertTrue(host.tree_widget.json_navigation.valid)  # Capture succeeded.
                    self.check_all(host, positions)  # Assert every node and exact source coordinate.

    # test_many_empty_containers_all_tabs: empty arrays/objects cannot accumulate any line drift.
    def test_many_empty_containers_all_tabs(self):
        for name in TABS:  # Exercise all four former counters.
            for count in (0, 2, 20, 100):  # Escalate preceding empty containers.
                with self.subTest(tab=name, count=count):
                    data = {**{str(index): [] if index % 2 else {} for index in range(count)}, 'target': 42}  # Regression fixture.
                    host = self.host(name, data)  # Actual builder and standard displayed layout.
                    self.assertTrue(host.tree_widget.highlight_in_text_box(find_property(host, 'target')))  # Navigate.
                    self.assertEqual(host.text_edit.textCursor().selectedText().strip(), '"target": 42')  # Exact late line.

    # test_formatting_and_repeated_invocations: changed formatting must recompute actual offsets even with blocked signals.
    def test_formatting_and_repeated_invocations(self):
        data = {'emoji': '😀', 'target': [[], {'key': 'same'}]}  # Non-BMP preceding later nodes.
        for name in TABS:  # Every tab.
            host = self.host(name, data)  # Initial capture.
            for compact in (False, True, False):  # Several text changes, not one fixed map.
                text, positions = annotated_text(dict(reversed(list(data.items()))), compact)  # Object order can change safely.
                host.text_edit.blockSignals(True)  # Caches cannot depend solely on emitted change events.
                host.text_edit.setPlainText(text)  # Test setup, not feature mutation.
                host.text_edit.blockSignals(False)  # Restore editor events.
                host.tree_synced = False  # Formatting alone does not require the sync flag.
                self.check_all(host, positions)  # Fresh actual-text offsets each time.

    # refuse: assert controlled explanation, no jump/selection change and no text mutation.
    def refuse(self, host, node):
        text = host.text_edit.toPlainText()  # Preserve unsynchronized edits verbatim.
        cursor = host.text_edit.textCursor()  # Preserve previous selection and cursor.
        before = (cursor.position(), cursor.anchor())  # Failure must not jump.
        with patch.object(QtWidgets.QMessageBox, 'information') as notice:  # Never display a visible/modal test dialog.
            self.assertFalse(host.tree_widget.highlight_in_text_box(node))  # Controlled handler failure.
            notice.assert_called_once()  # Real explanation path exercised.
        cursor = host.text_edit.textCursor()  # Read back exact cursor.
        self.assertEqual((cursor.position(), cursor.anchor()), before)  # No misleading jump.
        self.assertEqual(host.text_edit.toPlainText(), text)  # No automatic repair or replacement.

    # test_sub_float_precision_text_changes_are_refused: different JSON numbers must not match through float rounding.
    def test_sub_float_precision_text_changes_are_refused(self):
        for name in TABS:  # Protect every tab's correspondence rule.
            for baseline, changed in ((1.0, '1.0000000000000001'), (0.0, '1e-400'), (0.0, '2e-400')):  # Rounding and underflow.
                with self.subTest(tab=name, value=changed):
                    host = self.host(name, {'target': baseline})  # Float snapshot is the actual model representation.
                    node = find_property(host, 'target')  # Same path still exists in edited text.
                    host.text_edit.setPlainText('{"target":' + changed + '}')  # Valid unsynchronized numerical change.
                    self.refuse(host, node)  # Reject despite Python float rounding to the old value.
                    host.text_edit.setPlainText('{"target":' + ('1.00000e0' if baseline else '0.000e0') + '}')  # Numerically identical formatting.
                    self.assertTrue(host.tree_widget.highlight_in_text_box(node))  # Exact numerical equality remains allowed.

    # test_invalid_or_unsynchronized_text_all_tabs: refuse even when a path exists but its surrounding data changed.
    def test_invalid_or_unsynchronized_text_all_tabs(self):
        data = {'target': 42, 'others': [{'x': 1}, {'x': 2}]}  # Array order must remain significant.
        bad_texts = ('{', '{"target":42,"others":[{"x":2},{"x":1}]}', '{"target":42,"others":[]}',
                     '{"target":43,"others":[{"x":1},{"x":2}]}', '{"target":42,"target":42}',
                     '{"target":NaN}', '{"target":42} trailing', '{"others":[]}', '{"target":42,}',
                     '{"target":42,"others":[{"x":1},{"x":2}],"added":0}')  # Syntax, duplicates, missing and unrelated changes.
        for name in TABS:  # All integrations.
            host = self.host(name, data)  # Keep original tree.
            node = find_property(host, 'target')  # Valid original path is insufficient by itself.
            for text in bad_texts:  # Refuse each problematic source.
                with self.subTest(tab=name, text=text):
                    host.text_edit.setPlainText(text)  # Only test setup modifies text.
                    host.tree_synced = True  # Even a falsely green flag must not permit guessing.
                    self.refuse(host, node)  # Explain and leave text/selection unchanged.
            host.text_edit.setPlainText(json.dumps(data))  # Restoring equivalent text should recover safely.
            self.assertTrue(host.tree_widget.highlight_in_text_box(node))  # No permanent stale-offset error.

    # test_tree_reorder_delete_edit_and_rebuild: internal model signals invalidate even blocked widget signals.
    def test_tree_reorder_delete_edit_and_rebuild(self):
        data = {'entries': [42, 42, 43]}  # Include identical entries to expose occurrence staleness.
        for name in TABS:  # Each builder refreshes metadata.
            for operation in ('reorder', 'delete', 'edit', 'key', 'label'):
                with self.subTest(tab=name, operation=operation):
                    host = self.host(name, data)  # New valid tree.
                    root = find_property(host, 'entries').child(1)  # Actual array node.
                    item = root.child(0)  # Original first occurrence.
                    host.tree_widget.blockSignals(True)  # Existing application workflows block widget events.
                    if operation == 'reorder':
                        root.insertChild(1, root.takeChild(0))  # Move an identical occurrence.
                    elif operation == 'delete':
                        root.takeChild(1)  # Delete an identical neighbor.
                    elif operation == 'edit':
                        item.setData(0, QtCore.Qt.UserRole, 99)  # Change structural scalar data.
                    elif operation == 'key':
                        find_property(host, 'entries').child(0).setData(0, QtCore.Qt.UserRole, 'renamed')  # Rename key.
                    else:
                        item.setText(0, 'decorated label changed')  # Conservative invalidation includes labels.
                    host.tree_widget.blockSignals(False)  # Restore events.
                    host.tree_synced = True  # Stale flag cannot override internal-model invalidation.
                    self.refuse(host, item)  # Never target a different occurrence from stale paths.
                    host.load(data)  # Supported rebuild creates fresh nodes/paths.
                    self.assertTrue(host.tree_widget.highlight_in_text_box(find_property(host, 'entries').child(1).child(1)))  # Correct new occurrence.

    # test_missing_foreign_and_unsupported_locations: refuse missing metadata/path and unsupported hierarchy.
    def test_missing_foreign_and_unsupported_locations(self):
        host = self.host('FirstTabContent', {'target': 42})  # Valid source.
        node = find_property(host, 'target')  # Property target.
        self.refuse(host, None)  # Missing node.
        self.refuse(host, QtWidgets.QTreeWidgetItem())  # Detached node.
        other = self.host('SecondTabContent', {'target': 42})  # Foreign tree with the same data.
        self.refuse(host, find_property(other, 'target'))  # Same key does not establish ownership.
        for location in (None, {'path': ['missing'], 'kind': 'key'}, {'path': [True], 'kind': 'value'}, {'path': [], 'kind': 'unknown'}):
            node.setData(0, QT_DATA_JSON_LOCATION, location)  # Manufacture invalid metadata in test only.
            host.tree_widget.json_navigation.valid = True  # Exercise resolver validation rather than signal guard.
            self.refuse(host, node)  # Controlled explanation.
        host.load({'target': 42})  # Restore valid hierarchy.
        node = find_property(host, 'target')  # New tuple.
        node.takeChild(1)  # Unsupported incomplete property.
        host.tree_widget.record_json_locations({'target': 42})  # Capture must fail without crashing the builder.
        self.refuse(host, node)  # Never navigate unsupported tree structures.

    # test_actual_model_changed_rebuild_flow: exercise shared BaseTabContent lifecycle with each real builder.
    def test_actual_model_changed_rebuild_flow(self):
        methods = {'model_changed', 'blockSignals', 'unblockSignals', 'clear_tree_view', 'update_tree_from_model', 'update_text_widget_from_model'}  # Exact production flow.
        base = source_class('BaseTabContent.py', 'BaseTabContent', methods)  # Avoid full app/model initialization.
        for name in TABS:  # Every tab inherits the tested lifecycle.
            host = self.host(name, {'entries': [1, 2]})  # Original tree/text.
            for method in methods:
                setattr(host, method, getattr(base, method).__get__(host))  # Bind actual production lifecycle methods.
            host.model = QtCore.QObject()  # Real signal blocking, no persistent settings/save state.
            host.model_context = name  # Background signal argument for fixture only.
            host.main_window = type('Window', (), {'background_processing_signal': Mock()})()  # No desktop window.
            host.update_tree_synced_indicator = Mock(side_effect=lambda value: setattr(host, 'tree_synced', value))  # Existing indicator is not a navigation authority.
            new_data = {'entries': [2, 1], 'target': {'empty': []}}  # Simulate changed model/reordered values.
            host.view.get_json = lambda: new_data  # Supply synthetic updated data.
            host.view.get_text = lambda: json.dumps(new_data, indent=4)  # Production lifecycle serialization input.
            host.model_changed(host)  # Real block -> text refresh -> tree rebuild -> unblock flow.
            self.assertTrue(host.tree_widget.json_navigation.valid)  # Fresh paths survive blocked-signal rebuild.
            node = find_property(host, 'entries').child(1).child(1)  # New second entry.
            self.assertEqual(node.data(0, QT_DATA_JSON_LOCATION)['path'], ['entries', 1])  # Fresh occurrence path.
            self.assertTrue(host.tree_widget.highlight_in_text_box(node))  # Real rebuilt handler works.
            self.assertEqual(host.text_edit.textCursor().selectedText().strip(), '1')  # New order, not stale first entry.

    # test_selection_and_expansion_keep_locations_valid: ordinary right-click selection/expansion is not a data edit.
    def test_selection_and_expansion_keep_locations_valid(self):
        for name in TABS:  # Every tab's familiar interaction flow.
            host = self.host(name, {'target': 42, 'nested': {'x': []}})  # Valid structural fixture.
            node = find_property(host, 'target')  # Selected property.
            host.tree_widget.clearSelection()  # Right-button handler clears existing selection.
            host.tree_widget.setCurrentItem(node)  # Qt tree selection, not OS focus.
            node.setSelected(True)  # Select the actual occurrence.
            host.tree_widget.expand_tree_to_level(2)  # Existing expansion action.
            self.assertTrue(host.tree_widget.json_navigation.valid)  # Selection/expansion must not invalidate content.
            self.assertTrue(host.tree_widget.highlight_in_text_box(node))  # Normal action remains usable.

    # test_large_full_handler: measure late-node navigation through an actual populated tree/editor.
    def test_large_full_handler(self):
        data = {'rows': [{'Name': '😀 Fixture', 'empty': [], 'nested': {'value': index}} for index in range(10000)]}  # Large synthetic data only.
        text = json.dumps(data, indent=4, ensure_ascii=False)  # Actual displayed benchmark document.
        host = self.host('FirstTabContent', data, text)  # Real Qt tree/editor and production builder.
        target = find_property(host, 'rows').child(1).child(9999)  # Exact late object, not first repeated label.
        nested = next(target.child(i) for i in range(target.childCount()) if target.child(i).child(0).data(0, QtCore.Qt.UserRole) == 'nested')  # Structural member.
        value = nested.child(1).child(0).child(1)  # Value scalar under property tuple.
        start = time.perf_counter()  # Measure full shared handler, including editor read and cursor update.
        self.assertTrue(host.tree_widget.highlight_in_text_box(value))  # Real navigation.
        self.assertEqual(host.text_edit.textCursor().selectedText().strip(), '"value": 9999')  # Correct final occurrence.
        print(f'LARGE HANDLER: 10000 rows, {len(text.encode("utf-8"))} UTF-8 bytes, {time.perf_counter() - start:.3f}s')  # Actual elapsed result.

    # test_no_model_save_file_or_sync_mutation: navigation has no access to write/synchronize actions.
    def test_no_model_save_file_or_sync_mutation(self):
        for name in TABS:  # Every tab handler integration.
            data = {'target': 42, 'same': [42, 42]}  # Synthetic fixture, not a save read.
            host = self.host(name, data)  # Valid tree/text.
            host.model = {'editable': copy.deepcopy(data)}  # Model state sentinel.
            host.retained_full_save = {'inactive': {'sentinel': 7}, 'active': copy.deepcopy(data)}  # Retained-save sentinel.
            before = copy.deepcopy((host.model, host.retained_full_save))  # Independent mutation oracle.
            for method in ('sync_tree_from_text_window', 'sync_text_from_tree_window', 'update_model_from_tree',
                           'update_model_from_text_edit', 'update_text_widget_from_model', 'update_tree_from_model'):
                setattr(host, method, Mock(side_effect=AssertionError('Highlight invoked synchronization')))  # Catch forbidden pane/model operations.
            with patch('builtins.open', side_effect=AssertionError('Highlight accessed a file')), \
                 patch.object(host.text_edit, 'setPlainText', side_effect=AssertionError('Highlight replaced text')), \
                 patch.object(host.text_edit, 'insertPlainText', side_effect=AssertionError('Highlight inserted text')):
                self.assertTrue(host.tree_widget.highlight_in_text_box(find_property(host, 'target')))  # Real success path.
            self.assertEqual((host.model, host.retained_full_save), before)  # No editable/retained write-through.
            self.assertFalse(host.isVisible() or host.tree_widget.isVisible() or host.text_edit.isVisible())  # No desktop windows shown.

class SourceMapTests(unittest.TestCase):
    # test_standard_and_rejected_json: strict parser must not silently accept duplicate keys or nonstandard syntax.
    def test_standard_and_rejected_json(self):
        for text in ('null', 'true', 'false', '-12.5e+2', '[]', '{}', '"a\\n\\\\b\\\""'):
            self.assertEqual(JsonSourceMap(text).data, json.loads(text))  # Standard parser agreement.
        for text in ('', '01', '+1', '.5', '1.', '1e', '1e999', 'NaN', 'Infinity', '[1,]', '{"x":1,}',
                     '{"x":1,"\\u0078":2}', '{"x":1 "y":2}', '[true false]', 'truefalse', '\ufeff{}', '\v{}',
                     '"unterminated', '"bad\\q"', '"raw\nnewline"', '[[]', '{}{}'):
            with self.subTest(text=text), self.assertRaises(JsonNavigationError):
                JsonSourceMap(text)  # Refuse unsupported/ambiguous source.

    # test_deterministic_nested_corpus: parser/position map agrees with an independent offset oracle.
    def test_deterministic_nested_corpus(self):
        rng = random.Random(101026)  # Repeatable inputs.
        # generate: vary nested container/scalar shapes without nondeterministic timing.
        def generate(depth):
            if not depth or rng.randrange(3) == 0:
                return rng.choice([None, False, True, 42, -1.25, '😀 /w {} [] " \\ \n'])  # Difficult primitives.
            if rng.randrange(2):
                return [generate(depth - 1) for _ in range(rng.randrange(4))]  # Repeated/empty arrays.
            return {key: generate(depth - 1) for key in ('0', '😀', 'quote"', 'same')[:rng.randrange(5)]}  # Difficult keys.
        for _ in range(150):  # Broad deterministic parser corpus.
            data = generate(5)  # Nested fixtures only, never save files.
            text, expected = annotated_text(data, rng.choice([True, False]))  # Independent emitter.
            source = JsonSourceMap(text)  # Actual parser.
            self.assertTrue(same_json(source.data, data))  # Full structure/type agreement.
            for (path, kind), offset in expected.items():
                self.assertEqual(source.qt_position(path, kind), len(text[:offset].encode('utf-16-le')) // 2)  # Exact every-token coordinates.

    # test_deep_input_is_controlled: excessive nesting produces a controlled navigation exception.
    def test_deep_input_is_controlled(self):
        with self.assertRaises(JsonNavigationError):
            JsonSourceMap('[' * 2000 + '0' + ']' * 2000)  # No raw recursion crash reaches the handler.

    # test_large_source_real_latency: measure a substantial synthetic text without a visible app.
    def test_large_source_real_latency(self):
        data = {'rows': [{'Name': '😀 Fixture', 'empty': [], 'nested': {'value': index}} for index in range(10000)]}  # Large representative shape.
        text = json.dumps(data, indent=4, ensure_ascii=False)  # Source only for this synthetic benchmark.
        start = time.perf_counter()  # Actual elapsed time.
        source = JsonSourceMap(text)  # Parse the actual source once as each navigation does.
        self.assertTrue(same_json(source.data, data))  # Verify full correspondence.
        position = source.qt_position(('rows', 9999, 'nested', 'value'), 'value')  # Late exact target.
        self.assertEqual(text.encode('utf-16-le')[position * 2:position * 2 + 8].decode('utf-16-le'), '9999')  # Correct UTF-16 location.
        print(f'LARGE SOURCE: {len(text.encode("utf-8"))} UTF-8 bytes, 10000 rows, parse/compare/resolve {time.perf_counter() - start:.3f}s')  # Real performance evidence.

if __name__ == '__main__':
    unittest.main(verbosity=2)  # Return nonzero for any real regression.
