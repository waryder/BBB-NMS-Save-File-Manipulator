# File: test_inventory_organizer_ui.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_inventory_organizer_ui.py
# Purpose: Synthetic preferences and extracted UI lifecycle tests; never import the app or user preferences.
import ast
import configparser
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from InventoryOrganizer import CATEGORIES, InventoryPlanner, resolve
from InventoryOrganizerPreferences import organizer_settings, settings_payload
from InventoryOrganizerReview import review_rows
from test_inventory_organizer import SUIT, ONE, TEN, NINE, context, stack
from test_inventory_organizer_review import dialog_method, labels_for

QT = SimpleNamespace(UserRole=32, Checked=2, Unchecked=0)
SHIP = ('PlayerStateData', 'ShipOwnership', 8, 'Inventory')

# isolated_class: Extract selected production methods without imports, constructors or singleton side effects.
def isolated_class(filename, classname, names, **namespace):
    tree = ast.parse(Path(__file__).with_name(filename).read_text(encoding='utf-8'))
    node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == classname)
    node.body = [method for method in node.body if isinstance(method, ast.FunctionDef) and method.name in names]
    node.bases = [ast.Name(id='Base', ctx=ast.Load())]
    module = ast.Module(body=[node], type_ignores=[])
    namespace.setdefault('Base', object)
    exec(compile(ast.fix_missing_locations(module), '<isolated synthetic class>', 'exec'), namespace)
    return namespace[classname]

# manager_class: Reuse actual atomic writer methods but deliberately omit IniFileManager initialization.
def manager_class():
    return isolated_class('IniFileManager.py', 'IniFileManager',
                          ('get_inventory_organizer_settings', 'store_inventory_organizer_settings',
                           '_write_nms_preferences'), json=json, configparser=configparser,
                          copy=copy, os=os, tempfile=tempfile)

# manager_fixture: Configure a temporary fixture only, never the actual app preference location.
def manager_fixture(path):
    manager = manager_class()()
    manager.ini_file = str(path)
    manager.config = configparser.ConfigParser(delimiters='=')
    if path.exists():
        manager.config.read(str(path), encoding='utf-8')
    return manager

class Item:
    # __init__: Retain true identity and checkbox state independent of filtered order or label.
    def __init__(self, path, checked=False):
        self.path, self.checked = path, checked
    # data: Match QListWidgetItem's identity access.
    def data(self, role):
        return self.path
    # checkState: Match the Qt check-state contract.
    def checkState(self):
        return QT.Checked if self.checked else QT.Unchecked
    # setCheckState: Restore a saved source check.
    def setCheckState(self, value):
        self.checked = value == QT.Checked

class SourceList:
    # __init__: Represent only currently available entries, in arbitrary filtered order.
    def __init__(self, paths):
        self.items = [Item(path) for path in paths]
    # count: Report visible source count.
    def count(self):
        return len(self.items)
    # item: Return the visible item without reinterpreting its true path.
    def item(self, index):
        return self.items[index]

class Choice:
    # __init__: Supply a safe leave-in-place entry plus currently available true paths.
    def __init__(self, paths):
        self.paths, self.index = [None] + list(paths), 0
    # count: Match the destination combo interface.
    def count(self):
        return len(self.paths)
    # itemData: Return exact stored item identity.
    def itemData(self, index):
        return self.paths[index]
    # setCurrentIndex: Restore the selected available destination or fallback.
    def setCurrentIndex(self, index):
        self.index = index
    # currentData: Read the currently selected true destination.
    def currentData(self):
        return self.paths[self.index]

class Check:
    # __init__: Keep fake option state separate from source checks.
    def __init__(self):
        self.checked = False
    # setChecked: Restore an explicit boolean, including saved false.
    def setChecked(self, value):
        self.checked = value
    # isChecked: Supply the dialog option interface.
    def isChecked(self):
        return self.checked

# dialog_fixture: Bind production restore/save methods to synthetic widgets and a temporary manager.
def dialog_fixture(manager, paths):
    fake = SimpleNamespace(window=SimpleNamespace(ini_file_manager=manager), sources=SourceList(paths),
                           routes={category: Choice(paths) for category in CATEGORIES},
                           overflow=Check(), expand=Check(),
                           _settings=organizer_settings(manager.get_inventory_organizer_settings()))
    fake._routing = lambda: {category: combo.currentData() for category, combo in fake.routes.items()}
    fake._restore_settings = lambda: dialog_method('_restore_settings', Qt=QT)(fake)
    fake._save_settings = lambda: dialog_method('_save_settings', Qt=QT, settings_payload=settings_payload,
                                               QMessageBox=SimpleNamespace(warning=Mock()))(fake)
    fake._restore_settings()
    return fake

class PreferenceTests(unittest.TestCase):
    # test_default_and_malformed_fields: Fresh overflow is on, false is respected, invalid paths never route.
    def test_default_and_malformed_fields(self):
        self.assertTrue(organizer_settings({})['overflow'])
        self.assertFalse(organizer_settings({'overflow': False})['overflow'])
        self.assertTrue(organizer_settings({})['expand'])
        self.assertFalse(organizer_settings({'expand': False})['expand'])
        self.assertFalse(organizer_settings(settings_payload(organizer_settings({'expand': False})))['expand'])
        for value in (None, [], 'bad', {'overflow': 'false', 'expand': 1, 'sources': {}, 'routes': []}):
            parsed = organizer_settings(value)
            self.assertTrue(parsed['overflow'])
            self.assertTrue(parsed['expand'])
        value = {'sources': [[list(SHIP), True], [[True], True], ['Exosuit', True], [list(ONE), 'yes']],
                 'routes': {'Substance': list(SHIP), 'Product': ['bad'], 'Special': None, 'bad': list(ONE)}}
        parsed = organizer_settings(value)
        self.assertEqual(parsed['sources'], {SHIP: True})
        self.assertEqual(parsed['routes'], {'Substance': SHIP, 'Special': None})
        self.assertEqual(organizer_settings(settings_payload(parsed)), parsed)

    # test_reinstantiate_sources_routes_options_and_absent_paths: Preserve exact identities across loaded rosters.
    def test_reinstantiate_sources_routes_options_and_absent_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.ini'
            first = dialog_fixture(manager_fixture(path), [SUIT, ONE, SHIP, TEN])
            first.sources.item(2).setCheckState(QT.Checked)
            first.routes['Substance'].setCurrentIndex(3)  # Ship slot 8, not filtered row 2.
            first.overflow.setChecked(False)
            first.expand.setChecked(True)
            first._save_settings()  # No preview or Apply is required.
            missing = dialog_fixture(manager_fixture(path), [TEN, SUIT, ONE])
            self.assertIsNone(missing.routes['Substance'].currentData())
            self.assertFalse(missing.overflow.isChecked())
            self.assertTrue(missing.expand.isChecked())
            missing._save_settings()  # Closing with an absent ship must not erase its stored choices.
            restored = dialog_fixture(manager_fixture(path), [TEN, SHIP, ONE, SUIT])
            self.assertTrue(restored.sources.item(1).checked)
            self.assertEqual(restored.routes['Substance'].currentData(), SHIP)
            self.assertFalse(restored.sources.item(3).checked)
            self.assertFalse(restored.overflow.isChecked())
            self.assertTrue(restored.expand.isChecked())

    # test_route_reversion_and_malformed_json: Repeated changes back to the opening value persist too.
    def test_route_reversion_and_malformed_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.ini'
            manager = manager_fixture(path)
            fake = dialog_fixture(manager, [SUIT, ONE])
            fake.routes['Substance'].setCurrentIndex(2)
            fake._save_settings()
            fake.routes['Substance'].setCurrentIndex(0)
            fake._save_settings()
            self.assertIsNone(dialog_fixture(manager_fixture(path), [ONE, SUIT]).routes['Substance'].currentData())
            manager.config.set('InventoryOrganizer', 'settings', '{malformed')
            self.assertEqual(manager.get_inventory_organizer_settings(), {})
            self.assertTrue(dialog_fixture(manager, [SUIT]).overflow.isChecked())

    # test_atomic_write_failure_preserves_config_and_unrelated_preferences: Exercise real writer on temp files.
    def test_atomic_write_failure_preserves_config_and_unrelated_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.ini'
            path.write_text('[Preferences]\nlegacy_sorter = keep\nnms_save_folder = 100%%folder\n', encoding='utf-8')
            manager = manager_fixture(path)
            original_bytes, original_config = path.read_bytes(), copy.deepcopy(manager.config)
            payload = settings_payload(organizer_settings({'overflow': False}))
            with patch('os.replace', side_effect=OSError('synthetic replace failure')):
                with self.assertRaises(OSError):
                    manager.store_inventory_organizer_settings(payload)
            self.assertEqual(path.read_bytes(), original_bytes)
            self.assertEqual(dict(manager.config['Preferences']), dict(original_config['Preferences']))
            self.assertFalse(manager.config.has_section('InventoryOrganizer'))
            self.assertEqual(list(Path(directory).iterdir()), [path])  # No abandoned temporary sibling.
            manager.store_inventory_organizer_settings(payload)
            reloaded = manager_fixture(path)
            self.assertEqual(dict(reloaded.config['Preferences']), dict(original_config['Preferences']))
            self.assertEqual(reloaded.get_inventory_organizer_settings(), payload)

    # test_choices_invalidate_before_persistence_and_close_persists: Close/Cancel never require Apply.
    def test_choices_invalidate_before_persistence_and_close_persists(self):
        events = []
        fake = SimpleNamespace(_invalidate=lambda: events.append('invalidate'),
                               _save_settings=lambda: events.append('save'))
        dialog_method('_choices_changed')(fake)
        self.assertEqual(events, ['invalidate', 'save'])
        base = type('Base', (), {'done': lambda self, result: events.append(('done', result))})
        cls = isolated_class('InventoryOrganizerDialog.py', 'InventoryOrganizerDialog', ('done',), Base=base)
        dialog = cls()
        dialog._review_running, dialog._save_settings = False, lambda: events.append('save')
        dialog.done(0)  # Reject/Cancel result.
        self.assertEqual(events[-2:], ['save', ('done', 0)])
        dialog._review_running = True
        before = list(events)
        dialog.done(0)
        self.assertEqual(events, before)

class ReviewLifecycleTests(unittest.TestCase):
    # test_exact_prefix_and_full_overflow_retained_filter: Assert punctuation, case, record counts and live rows.
    def test_exact_prefix_and_full_overflow_retained_filter(self):
        data, routes = context(), {'Substance': ONE}
        labels = {SUIT: 'Exosuit: inventory name', ONE: 'Container 1: storage name', TEN: 'Container 10: customname',
                  NINE: 'Container 9: spare'}
        prefix = '-> (Exosuit: inventory name)→(Container 1: storage name):(Cat: Resources)'
        self.assertEqual(review_rows(data, (SUIT,), routes, labels)[0].text, prefix)
        self.assertEqual(review_rows(data, (SUIT,), routes, labels,
                                    InventoryPlanner(data).plan((SUIT,), routes))[0].text,
                         prefix + ': 1 Parts to destination')
        resolve(data, SUIT)['Slots'] = [stack(x=index) for index in range(5)]
        plan = InventoryPlanner(data).plan((SUIT,), routes, overflow=True)
        self.assertEqual(review_rows(data, (SUIT,), routes, labels, plan)[0].text,
                         prefix + ': 1 Parts to destination + 1 Parts overflow to Container 10: customname'
                         ' + 1 Parts overflow to Container 9: spare + 2 Parts retained (destination full)')
        resolve(data, ONE)['Slots'] = [stack('Product')]
        for overflow in (False, True):
            plan = InventoryPlanner(data).plan((SUIT,), routes, overflow=overflow)
            self.assertEqual(review_rows(data, (SUIT,), routes, labels, plan), [])
            self.assertEqual(len(review_rows(data, (SUIT,), routes, labels)), 6)
            self.assertEqual(plan.changed, overflow)  # Overflow moves remain applicable despite hidden rows.

    # test_progress_success_error_and_prior_enabled_state: Paint before planning and always dismiss/restore.
    def test_progress_success_error_and_prior_enabled_state(self):
        for failure in (False, True):
            for enabled in (False, True):
                events, progress = [], Mock()
                progress.show.side_effect = lambda: events.append('show')
                progress.repaint.side_effect = lambda: events.append('paint')
                progress.accept.side_effect = lambda: events.append('close')
                fake = SimpleNamespace(_review_running=False, isEnabled=lambda: enabled,
                                       setEnabled=Mock(), window=SimpleNamespace(isEnabled=lambda: enabled, setEnabled=Mock()),
                                       _selected=lambda: [SUIT], _routing=lambda: {'Substance': ONE},
                                       overflow=Check(), expand=Check(), controller=Mock())
                # preview: Assert guards are active at the actual synchronous planner boundary.
                def preview(*unused):
                    events.append('plan')
                    self.assertTrue(fake._review_running)
                    fake.setEnabled.assert_called_with(False)
                    if failure:
                        raise ValueError('synthetic planning failure')
                    return 'plan'
                fake.controller.preview.side_effect = preview
                app = SimpleNamespace(processEvents=lambda flag: events.append('events'))
                method = dialog_method('_review_plan', NmsLoadingDialog=lambda *args: progress,
                                       QApplication=app, QEventLoop=SimpleNamespace(ExcludeUserInputEvents=7))
                if failure:
                    with self.assertRaises(ValueError):
                        method(fake)
                else:
                    self.assertEqual(method(fake), 'plan')
                self.assertEqual(events, ['show', 'paint', 'events', 'plan', 'close'])
                self.assertFalse(fake._review_running)
                fake.setEnabled.assert_called_with(enabled)
                fake.window.setEnabled.assert_called_with(enabled)
                progress.accept.assert_called_once_with()

    # test_preview_errors_invalidate_and_empty_review_can_apply: Display filtering never gates plan.changed.
    def test_preview_errors_invalidate_and_empty_review_can_apply(self):
        for failure in (False, True):
            fake = SimpleNamespace(_review_running=False, apply_button=Mock(), _render=Mock(),
                                   _invalidate=Mock(), review=Mock(), _review_plan=Mock())
            fake._review_plan.return_value = SimpleNamespace(changed=True)
            if failure:
                fake._review_plan.side_effect = ValueError('synthetic failure')
            warning = Mock()
            dialog_method('_preview', QMessageBox=SimpleNamespace(warning=warning))(fake)
            if failure:
                fake._invalidate.assert_called_once_with()
                warning.assert_called_once()
            else:
                fake.apply_button.setEnabled.assert_called_with(True)
                fake._render.assert_called_once()
            fake._review_running = True
            fake._review_plan.reset_mock()
            dialog_method('_preview')(fake)
            fake._review_plan.assert_not_called()

    # test_progress_setup_failure_restores_guards: A failure before planning cannot strand interaction state.
    def test_progress_setup_failure_restores_guards(self):
        fake = SimpleNamespace(_review_running=False, isEnabled=lambda: True, setEnabled=Mock(),
                               window=SimpleNamespace(isEnabled=lambda: False, setEnabled=Mock()))
        method = dialog_method('_review_plan', NmsLoadingDialog=Mock(side_effect=RuntimeError('synthetic setup failure')))
        with self.assertRaises(RuntimeError):
            method(fake)
        self.assertFalse(fake._review_running)
        fake.setEnabled.assert_called_with(True)
        fake.window.setEnabled.assert_called_with(False)

    # test_loading_pattern_is_modal_and_non_cancellable_static: Reuse existing user-close suppression exactly.
    def test_loading_pattern_is_modal_and_non_cancellable_static(self):
        tree = ast.parse(Path(__file__).with_name('NmsLoadController.py').read_text(encoding='utf-8'))
        dialog = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'NmsLoadingDialog')
        self.assertEqual(dialog.bases[0].id, 'TextOnlyLoadingDialog')
        methods = {node.name: node for node in dialog.body if isinstance(node, ast.FunctionDef)}
        self.assertIsInstance(methods['reject'].body[0], ast.Return)
        self.assertEqual(methods['closeEvent'].body[0].value.func.attr, 'ignore')
        text = Path(__file__).with_name('imports.py').read_text(encoding='utf-8')
        self.assertIn('self.setWindowModality(Qt.ApplicationModal)', text)
        self.assertIn('~Qt.WindowCloseButtonHint', text)

    # test_restore_order_and_friendly_labels_static: Restore before connecting signals; raw categories stay internal.
    def test_restore_order_and_friendly_labels_static(self):
        tree = ast.parse(Path(__file__).with_name('InventoryOrganizerDialog.py').read_text(encoding='utf-8'))
        init = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == '__init__')
        calls = [node.func.attr for node in ast.walk(init) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        self.assertLess(calls.index('_restore_settings'), calls.index('_connect'))
        destinations = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == '_destinations')
        label = next(node for node in ast.walk(destinations) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name) and node.func.id == 'QLabel')
        self.assertIsInstance(label.args[0], ast.Subscript)
        self.assertEqual(label.args[0].value.id, 'CATEGORY_NAMES')
        self.assertEqual(CATEGORIES, ('Substance', 'Product', 'Technology', 'Consumable', 'Trade', 'Special'))


    # test_source_shortcut_order_and_membership: Each shortcut replaces checks and persists once.
    def test_source_shortcut_order_and_membership(self):
        paths = [SUIT, ONE, SHIP, TEN, ('PlayerStateData', 'FreighterInventory'),
                 ('PlayerStateData', 'FishPlatformInventory'), ('PlayerStateData', 'FishBaitBoxInventory'),
                 ('PlayerStateData', 'CookingIngredientsInventory')]
        mobile = {SUIT, SHIP, paths[4], paths[5]}  # Fish Platform belongs to Mobile Storages.
        from InventoryOrganizer import inventory_roster
        from test_inventory_organizer import inventory
        data = context()
        for path in paths[4:]:
            data['PlayerStateData'][path[1]] = inventory()
        actual = {entry.path: entry.carried for entry in inventory_roster(data)}
        self.assertTrue(actual[paths[5]])
        self.assertFalse(actual[paths[6]])
        self.assertFalse(actual[paths[7]])
        self.assertFalse(actual[ONE])
        for selection, expected in [('all', set(paths)), ('carried', mobile),
                                    ('stationary', set(paths) - mobile), ('clear', set())]:
            sources = SourceList(paths)
            sources.blockSignals = Mock(return_value=False)
            fake = SimpleNamespace(sources=sources, _choices_changed=Mock(),
                                   entries=[SimpleNamespace(path=path, carried=path in mobile) for path in paths])
            dialog_method('_select_group', Qt=QT)(fake, selection)
            self.assertEqual({item.path for item in sources.items if item.checked}, expected)
            fake._choices_changed.assert_called_once_with()
            self.assertEqual(sources.blockSignals.call_args_list[-1].args, (False,))
        tree = ast.parse(Path(__file__).with_name('InventoryOrganizerDialog.py').read_text(encoding='utf-8'))
        method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == '_sources')
        loop = next(node for node in method.body if isinstance(node, ast.For))
        self.assertEqual(ast.literal_eval(loop.iter), (('Select all', 'all'), ('Mobile Storages', 'carried'),
                                                     ('Stationary Storages', 'stationary'), ('Clear', 'clear')))

if __name__ == '__main__':
    unittest.main(verbosity=2)
