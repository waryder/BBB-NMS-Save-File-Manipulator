# File: test_inventory_organizer.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_inventory_organizer.py
# Purpose: Synthetic, Qt-free planner and memory-transaction regression tests; never open saves.
import copy
import unittest
from InventoryOrganizer import InventoryPlanner, inventory_roster, resolve
from InventoryOrganizerController import InventoryOrganizerController

SUIT = ('PlayerStateData', 'Inventory')
ONE = ('PlayerStateData', 'Chest1Inventory')
TEN = ('PlayerStateData', 'Chest10Inventory')
NINE = ('PlayerStateData', 'Chest9Inventory')

# stack: Build a complete synthetic record with opaque fields that must survive transfers.
def stack(category='Substance', x=0, y=0):
    return {'Id': '^TEST', 'Type': {'InventoryType': category}, 'Index': {'X': x, 'Y': y},
            'Amount': 41, 'Seed': [True, '0x123'], 'Unknown': {'nested': [1, 2]}}

# inventory: Build a sparse inventory without touching application fixtures.
def inventory(slots=None, cells=None):
    return {'Name': '<Synthetic & name>', 'Slots': slots or [], 'Width': 7, 'Height': 8,
            'ValidSlotIndices': cells if cells is not None else [{'X': 0, 'Y': 0}]}

# context: Build only the structures needed by the candidate.
def context() -> dict:
    return {'PlayerStateData': {'Inventory': inventory([stack()]), 'Chest1Inventory': inventory(),
                                'Chest10Inventory': inventory(), 'Chest9Inventory': inventory()}}

class PlannerTests(unittest.TestCase):
    # plan: Keep test setup explicit and use the production public planner.
    def plan(self, data, sources=(SUIT,), routes=None, overflow=False, expand=False):
        return InventoryPlanner(data).plan(sources, routes or {'Substance': ONE}, overflow, expand)

    # test_snapshot_and_conservation: Preserve every opaque field and keep the input untouched.
    def test_snapshot_and_conservation(self):
        data = context()
        original = copy.deepcopy(data)
        result = self.plan(data)
        self.assertEqual(data, original)
        self.assertEqual(resolve(result.candidate, ONE)['Slots'], [stack()])
        self.assertEqual(resolve(result.candidate, SUIT)['Slots'], [])
        self.assertEqual(len(result.moves), 1)
        self.assertTrue(result.changed)

    # test_sparse_positions_and_existing_items: Use actual free cells, never compact a destination.
    def test_sparse_positions_and_existing_items(self):
        data = context()
        target = resolve(data, ONE)
        target['Slots'] = [stack('Product', 9, 11)]
        target['ValidSlotIndices'] = [{'X': 9, 'Y': 11}, {'X': 4, 'Y': 7}]
        result = self.plan(data)
        self.assertEqual(resolve(result.candidate, ONE)['Slots'][0], target['Slots'][0])
        self.assertEqual(resolve(result.candidate, ONE)['Slots'][1]['Index'], {'X': 4, 'Y': 7})
        self.assertEqual(resolve(result.candidate, ONE)['ValidSlotIndices'], target['ValidSlotIndices'])

    # test_full_without_expansion: A full target cannot silently grow or consume a source stack.
    def test_full_without_expansion(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product')]
        result = self.plan(data)
        self.assertFalse(result.changed)
        self.assertEqual(result.stays[0]['reason'], 'destination full')
        self.assertEqual(result.candidate, data)

    # test_assigned_expansion_only: Expand even unused explicit targets, preserving dimensions.
    def test_assigned_expansion_only(self):
        data = context()
        result = self.plan(data, sources=(), expand=True)
        self.assertTrue(result.changed)
        self.assertEqual(len(result.moves), 0)
        self.assertEqual(len(resolve(result.candidate, ONE)['ValidSlotIndices']), 120)
        self.assertEqual(resolve(result.candidate, ONE)['Width'], 7)
        self.assertEqual(resolve(result.candidate, TEN), resolve(data, TEN))
        self.assertEqual(result.expanded, [ONE])

    # test_overflow_backward_and_exclusions: Overflow is unassigned chest-only, reversed and not the source.
    def test_overflow_backward_and_exclusions(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product')]
        result = self.plan(data, overflow=True)
        self.assertEqual(result.moves[0]['to'], TEN)
        self.assertEqual(len(resolve(result.candidate, TEN)['ValidSlotIndices']), 1)
        result = self.plan(data, routes={'Substance': ONE, 'Special': TEN}, overflow=True)
        self.assertEqual(result.moves[0]['to'], NINE)
        data['PlayerStateData']['Chest10Inventory'] = inventory([stack()])
        result = self.plan(data, sources=(TEN,), overflow=True)
        self.assertEqual(result.moves[0]['to'], NINE)

    # test_overflow_expansion_is_lazy_and_silent: Only a used spare grows; no expansion notice identifies it.
    def test_overflow_expansion_is_lazy_and_silent(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product', x, y) for x in range(10) for y in range(12)]
        resolve(data, TEN)['Slots'] = [stack('Product')]
        result = self.plan(data, overflow=True, expand=True)
        self.assertEqual(result.moves[0]['to'], TEN)
        self.assertEqual(len(resolve(result.candidate, TEN)['ValidSlotIndices']), 120)
        self.assertEqual(resolve(result.candidate, NINE), resolve(data, NINE))
        self.assertNotIn(TEN, result.expanded)

    # test_no_rerouting_and_duplicate_records: Original occurrences move once, not by equality lookup.
    def test_no_rerouting_and_duplicate_records(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(), stack()]
        resolve(data, ONE)['ValidSlotIndices'].append({'X': 1, 'Y': 0})
        result = self.plan(data, sources=(SUIT, ONE))
        self.assertEqual(len(result.moves), 2)
        self.assertEqual(len(resolve(result.candidate, ONE)['Slots']), 2)
        self.assertEqual(resolve(result.candidate, ONE)['Slots'][1]['Index'], {'X': 1, 'Y': 0})
        result = self.plan(data, routes={'Substance': SUIT}, overflow=True)
        self.assertEqual(result.candidate, data)

    # test_unknown_and_unrouted: Unknown and explicitly unassigned categories remain untouched.
    def test_unknown_and_unrouted(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack('Future'), stack('Special')]
        result = self.plan(data)
        self.assertEqual(len(result.stays), 2)
        self.assertEqual(result.candidate, data)

    # test_stable_paths_and_empty_ships: Missing roster entries do not relabel subsequent entries.
    def test_stable_paths_and_empty_ships(self):
        data = context()
        data['PlayerStateData']['ShipOwnership'] = [
            {'Resource': {'Filename': ''}, 'Inventory': inventory()},
            {'Resource': {'Filename': 'SHIP'}, 'Name': 'Real ship', 'Inventory': inventory()}]
        roster = inventory_roster(data)
        self.assertIn(TEN, [entry.path for entry in roster])
        self.assertIn(('PlayerStateData', 'ShipOwnership', 1, 'Inventory'), [e.path for e in roster])
        self.assertNotIn(('PlayerStateData', 'ShipOwnership', 0, 'Inventory'), [e.path for e in roster])
        self.assertIn('Container 10', next(e.label for e in roster if e.path == TEN))

    # test_global_expansion_off: Assigned and overflow capacities remain byte-for-byte equivalent as JSON values.
    def test_global_expansion_off(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product')]
        resolve(data, SUIT)['Slots'] = [stack(), stack(x=1), stack(x=2)]
        result = self.plan(data, overflow=True)
        for entry in inventory_roster(data):
            self.assertEqual(resolve(result.candidate, entry.path)['ValidSlotIndices'],
                             resolve(data, entry.path)['ValidSlotIndices'])
        self.assertEqual([move['to'] for move in result.moves], [TEN, NINE])
        self.assertEqual(len(result.stays), 1)

    # test_no_reroute_from_selected_overflow: Newly arrived stacks must not be processed as source members.
    def test_no_reroute_from_selected_overflow(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product')]
        result = self.plan(data, sources=(SUIT, TEN, NINE), overflow=True)
        self.assertEqual(len(result.moves), 1)
        self.assertEqual(result.moves[0]['to'], TEN)
        self.assertEqual(len(resolve(result.candidate, TEN)['Slots']), 1)
        self.assertEqual(len(result.stays), 0)

    # test_multiset_conservation: Preserve opaque record fields, including equal records, across the entire context.
    def test_multiset_conservation(self):
        import json
        from collections import Counter
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(), stack(), stack('Future')]
        resolve(data, ONE)['ValidSlotIndices'] += [{'X': 1, 'Y': 0}]
        result = self.plan(data)
        original, candidate = [], []
        for entry in inventory_roster(data):
            original += resolve(data, entry.path)['Slots']
            candidate += resolve(result.candidate, entry.path)['Slots']
        stripped = lambda slots: Counter(json.dumps({k: v for k, v in record.items() if k != 'Index'},
                                                     sort_keys=True) for record in slots)
        self.assertEqual(stripped(original), stripped(candidate))

    # test_assigned_move_expansion: Assigned storage grows before inserting and leaves other data unchanged.
    def test_assigned_move_expansion(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product')]
        result = self.plan(data, expand=True)
        self.assertEqual(len(result.moves), 1)
        self.assertEqual(len(resolve(result.candidate, ONE)['ValidSlotIndices']), 120)
        self.assertEqual(resolve(result.candidate, ONE)['Slots'][0], stack('Product'))

    # test_no_arbitrary_overflow: A non-chest inventory named Container is never an implicit destination.
    def test_no_arbitrary_overflow(self):
        data = context()
        for path in (ONE, TEN, NINE):
            resolve(data, path)['Slots'] = [stack('Product')]
        data['PlayerStateData']['FreighterInventory'] = inventory()
        data['PlayerStateData']['FreighterInventory']['Name'] = 'Container'
        result = self.plan(data, overflow=True)
        self.assertFalse(result.changed)
        self.assertEqual(len(result.stays), 1)

    # test_all_categories_share_destination: Six routes can share a destination with no merging or sorting.
    def test_all_categories_share_destination(self):
        from InventoryOrganizer import CATEGORIES
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(category, index) for index, category in enumerate(CATEGORIES)]
        result = self.plan(data, routes={category: ONE for category in CATEGORIES}, expand=True)
        self.assertEqual([record['Type']['InventoryType'] for record in resolve(result.candidate, ONE)['Slots']], list(CATEGORIES))
        self.assertEqual(len(result.moves), 6)

    # test_unsafe_expansion_refused: Never shrink unusual capacity or discard an occupied position.
    def test_unsafe_expansion_refused(self):
        for field in ('Slots', 'ValidSlotIndices'):
            data = context()
            resolve(data, ONE)[field] = [stack(x=12)] if field == 'Slots' else [{'X': 12, 'Y': 0}]
            with self.assertRaises(ValueError):
                self.plan(data, expand=True)

class Widget:
    # __init__: Fake only signal and raw-editor state; do not import Qt.
    def __init__(self, text='exact raw formatting'):
        self.text, self.blocked = text, False
    # blockSignals: Return the previous guard state just like QObject.
    def blockSignals(self, value):
        old, self.blocked = self.blocked, value
        return old
    # setPlainText: Preserve exact rollback text.
    def setPlainText(self, value):
        self.text = value

class Model(Widget):
    # __init__: Start with independent synthetic context data.
    def __init__(self):
        super().__init__()
        self.data = context()
    # get_data: Match the active editable-context interface.
    def get_data(self):
        return self.data
    # set_data: Emulate complete-context publication, without Qt or files.
    def set_data(self, value):
        self.data = value

class Tab:
    # __init__: Expose only the transaction's required tab interface.
    def __init__(self):
        self.text_edit, self.tree_widget, self.tree_synced = Widget(), Widget(), True
    # update_tree_synced_indicator: Match the real explicit-boolean signature.
    def update_tree_synced_indicator(self, value):
        self.tree_synced = value

class Window:
    # __init__: Fake every relevant view/dirty/guard state without launching the application.
    def __init__(self):
        self.model, self._nms_tabs, self.nms_source = Model(), [Tab() for _ in range(4)], object()
        self._nms_loading, self.nms_data_changed, self.enabled = False, False, True
        self.fail, self.refreshes = False, 0
    # isEnabled: Report exact initial interaction state.
    def isEnabled(self):
        return self.enabled
    # setEnabled: Emulate transaction guard transitions.
    def setEnabled(self, value):
        self.enabled = value
    # _capture_nms_editors: Capture all raw formatting and synchronization states.
    def _capture_nms_editors(self):
        return [(tab.text_edit.text, tab.tree_synced) for tab in self._nms_tabs]
    # _refresh_nms_tabs: Simulate a partially destructive rendering failure once.
    def _refresh_nms_tabs(self):
        self.refreshes += 1
        for tab in self._nms_tabs:
            tab.text_edit.text = 'reformatted'
        if self.fail:
            self.fail = False
            raise RuntimeError('synthetic refresh failure')
    # _mark_nms_changed: Emulate the existing main API without writing a save.
    def _mark_nms_changed(self, reason):
        self.nms_data_changed = True
    # _update_nms_led: Supply the production dirty-state recovery hook.
    def _update_nms_led(self):
        pass

class ControllerTests(unittest.TestCase):
    # prepare: Build a preview using only fake interfaces.
    def prepare(self):
        window = Window()
        controller = InventoryOrganizerController(window)
        controller.preview((SUIT,), {'Substance': ONE})
        return window, controller

    # test_apply_and_noop: A preview alone is cancel-safe; success dirties exactly once and consumes it.
    def test_apply_and_noop(self):
        window, controller = self.prepare()
        self.assertFalse(window.nms_data_changed)
        self.assertEqual(window.refreshes, 0)
        self.assertTrue(controller.apply())
        self.assertTrue(window.nms_data_changed)
        self.assertEqual(window.refreshes, 1)
        with self.assertRaises(ValueError):
            controller.apply()
        controller.preview((SUIT,), {'Substance': SUIT})
        self.assertFalse(controller.apply())
        self.assertEqual(window.refreshes, 1)

    # test_fresh_noop_and_busy_refusal: Noop cannot dirty; pre-existing operation guards cannot be stolen.
    def test_fresh_noop_and_busy_refusal(self):
        window = Window()
        controller = InventoryOrganizerController(window)
        controller.preview((SUIT,), {'Substance': SUIT})
        self.assertFalse(controller.apply())
        self.assertFalse(window.nms_data_changed)
        self.assertEqual(window.refreshes, 0)
        for name in ('_nms_loading', '_starship_upgrade_running', '_starship_delete_running'):
            setattr(window, name, True)
            with self.assertRaises(ValueError):
                controller.preview((SUIT,), {'Substance': ONE})
            self.assertTrue(getattr(window, name))
            setattr(window, name, False)

    # test_partial_guard_failure: Failure acquiring a later widget restores every earlier acquired guard.
    def test_partial_guard_failure(self):
        window, controller = self.prepare()
        original = copy.deepcopy(window.model.data)
        def reject_guard(value):
            # reject_guard: Emulate a widget refusing acquisition before publication.
            raise RuntimeError('synthetic signal guard failure')
        window._nms_tabs[1].tree_widget.blockSignals = reject_guard
        with self.assertRaises(RuntimeError):
            controller.apply()
        self.assertEqual(window.model.data, original)
        self.assertFalse(window.model.blocked)
        self.assertTrue(window.enabled)
        self.assertFalse(window._nms_loading)
        self.assertEqual(window.refreshes, 0)

    # test_capacity_only_apply: A zero-move expansion still publishes a complete candidate.
    def test_capacity_only_apply(self):
        window = Window()
        controller = InventoryOrganizerController(window)
        controller.preview((), {'Substance': ONE}, expand=True)
        self.assertTrue(controller.apply())
        self.assertEqual(len(resolve(window.model.data, ONE)['ValidSlotIndices']), 120)

    # test_stale_source_model_and_sync: Reject every stale or raw-pending preview without implicit sync.
    def test_stale_source_model_and_sync(self):
        for change in ('source', 'model', 'sync'):
            window, controller = self.prepare()
            if change == 'source':
                window.nms_source = object()
            elif change == 'model':
                window.model.data['new'] = 'edit'
            else:
                window._nms_tabs[3].tree_synced = False
            original = copy.deepcopy(window.model.data)
            with self.assertRaises(ValueError):
                controller.apply()
            self.assertEqual(window.model.data, original)
            self.assertEqual(window.refreshes, 0)

    # test_source_metadata_and_opaque_codec: Source checks never serialize or deepcopy a retained codec.
    def test_source_metadata_and_opaque_codec(self):
        window = Window()
        window.nms_source = {'context_key': 'BaseContext', 'codec': object()}
        controller = InventoryOrganizerController(window)
        controller.preview((SUIT,), {'Substance': ONE})
        window.nms_source['context_key'] = 'ExpeditionContext'
        with self.assertRaises(ValueError):
            controller.apply()
        self.assertEqual(window.refreshes, 0)

    # test_cancel_and_private_candidate: Cancel leaves exact editors/dirty flags and cannot publish a mutable UI copy.
    def test_cancel_and_private_candidate(self):
        window = Window()
        controller = InventoryOrganizerController(window)
        original, editors = copy.deepcopy(window.model.data), window._capture_nms_editors()
        result = controller.preview((SUIT,), {'Substance': ONE})
        result.candidate.clear()
        controller.invalidate()
        with self.assertRaises(ValueError):
            controller.apply()
        self.assertEqual(window.model.data, original)
        self.assertEqual(window._capture_nms_editors(), editors)
        self.assertFalse(window.nms_data_changed)
        result = controller.preview((SUIT,), {'Substance': ONE})
        result.candidate.clear()
        self.assertTrue(controller.apply())
        self.assertEqual(resolve(window.model.data, ONE)['Slots'], [stack()])

    # test_equal_model_replacement_and_preview_sync: Replacing equal data is stale, and pending text blocks preview.
    def test_equal_model_replacement_and_preview_sync(self):
        window, controller = self.prepare()
        window.model.data = copy.deepcopy(window.model.data)
        with self.assertRaises(ValueError):
            controller.apply()
        window._nms_tabs[0].tree_synced = False
        with self.assertRaises(ValueError):
            controller.preview((SUIT,), {'Substance': ONE})
        self.assertEqual(window.refreshes, 0)

    # test_rollback_prior_dirty_and_disabled: Preserve a caller's non-default dirty/enabled state on failure.
    def test_rollback_prior_dirty_and_disabled(self):
        window, controller = self.prepare()
        window.nms_data_changed, window.enabled, window.fail = True, False, True
        with self.assertRaises(RuntimeError):
            controller.apply()
        self.assertTrue(window.nms_data_changed)
        self.assertFalse(window.enabled)
        self.assertFalse(window._nms_loading)

    # test_rollback: Recover complete context, exact text, dirty state and pre-existing guards.
    def test_rollback(self):
        window, controller = self.prepare()
        original, editors = copy.deepcopy(window.model.data), window._capture_nms_editors()
        window._nms_tabs[0].text_edit.blocked = True
        window.fail = True
        with self.assertRaises(RuntimeError):
            controller.apply()
        self.assertEqual(window.model.data, original)
        self.assertEqual(window._capture_nms_editors(), editors)
        self.assertFalse(window.nms_data_changed)
        self.assertFalse(window._nms_loading)
        self.assertTrue(window.enabled)
        self.assertTrue(window._nms_tabs[0].text_edit.blocked)
        self.assertFalse(window.model.blocked)

class DialogStaticTests(unittest.TestCase):
    # test_roster_matches_data_views: Parse the existing roster without importing Qt or any application modules.
    def test_roster_matches_data_views(self):
        import ast
        from pathlib import Path
        from InventoryOrganizer import SOURCE_PATHS
        tree = ast.parse(Path(__file__).with_name('DataViews.py').read_text(encoding='utf-8'))
        method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                      and node.name == 'init_inventory_source_list')
        assignment = next(node for node in method.body if isinstance(node, ast.Assign))
        self.assertEqual(SOURCE_PATHS, tuple(tuple(path) for path in ast.literal_eval(assignment.value)))

    # test_ui_labels_defaults_and_escaping: Verify the separate UI contract without importing or launching Qt.
    def test_ui_labels_defaults_and_escaping(self):
        import ast
        from pathlib import Path
        tree = ast.parse(Path(__file__).with_name('InventoryOrganizerDialog.py').read_text(encoding='utf-8'))
        constants = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
                     if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        self.assertEqual(constants['OVERFLOW_LABEL'], "Overflow: if destination is full, overflow to other 'Container' type storages.")
        self.assertEqual(constants['OVERFLOW_HELP'], 'Unassigned containers only, working backward from Container 10. Otherwise items stay where they are.')
        self.assertEqual(constants['EXPAND_LABEL'], 'Expand all Destination storages to 120 cells.')
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        checked = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == 'setChecked']
        defaults = {node.func.value.attr: node.args[0].value for node in checked
                    if isinstance(node.func.value, ast.Attribute) and isinstance(node.args[0], ast.Constant)}
        self.assertEqual(defaults, {'overflow': True, 'expand': True})
        self.assertTrue(any(isinstance(node.func, ast.Attribute) and node.func.attr == 'setHtml' for node in calls))
        self.assertEqual(sum(isinstance(node.func, ast.Name) and node.func.id == 'QTextBrowser' for node in calls), 1)
        self.assertFalse(any(isinstance(node, ast.Attribute) and node.attr == 'summary' for node in ast.walk(tree)))
        strings = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        self.assertIn('Review Summary', strings)
        self.assertIn('Review Moves', strings)
        self.assertFalse(any('stacks' in text.lower() for text in strings))

if __name__ == '__main__':
    unittest.main(verbosity=2)
