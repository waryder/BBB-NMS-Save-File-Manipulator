# File: test_inventory_organizer_review.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_inventory_organizer_review.py
# Purpose: Synthetic Qt-free review aggregation and extracted-dialog-method regressions; no saves.
import ast
import copy
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from InventoryOrganizer import CATEGORIES, InventoryPlanner, inventory_roster, resolve
from InventoryOrganizerReview import review_rows, review_text, review_html
from test_inventory_organizer import SUIT, ONE, TEN, NINE, stack, inventory, context

# labels_for: Preserve loaded special characters and true inventory identities.
def labels_for(data):
    return {entry.path: entry.label for entry in inventory_roster(data)}

# dialog_method: Compile only an isolated method; never import Qt or the application module.
def dialog_method(name, **namespace):
    tree = ast.parse(Path(__file__).with_name('InventoryOrganizerDialog.py').read_text(encoding='utf-8'))
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)
    module = ast.Module(body=[method], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), '<isolated dialog method>', 'exec'), namespace)
    return namespace[name]

class ReviewTests(unittest.TestCase):
    # test_shared_targets_categories_and_stable_rows: Never merge sources/categories sharing one destination.
    def test_shared_targets_categories_and_stable_rows(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(), stack('Product', 1)]
        resolve(data, TEN)['Slots'] = [stack('Product')]
        routes = {category: ONE for category in CATEGORIES}
        plan = InventoryPlanner(data).plan((SUIT, TEN), routes, expand=True)
        labels = labels_for(data)
        live = review_rows(data, (SUIT, TEN), routes, labels)
        reviewed = review_rows(data, (SUIT, TEN), routes, labels, plan)
        self.assertEqual([row.key for row in reviewed], [live[i].key for i in (0, 1, 7)])
        self.assertEqual(len(live), 12)
        self.assertEqual([row.key[0] for row in live], [SUIT] * 6 + [TEN] * 6)
        self.assertTrue(all(after.text.startswith(live[index].text + ': ')
                            for index, after in zip((0, 1, 7), reviewed)))
        self.assertIn('1 Parts to destination', reviewed[0].text)
        self.assertIn('1 Parts to destination', reviewed[1].text)
        self.assertIn('1 Parts to destination', reviewed[2].text)
        self.assertNotIn('0 Parts to destination', '\n'.join(row.text for row in reviewed))

    # test_overflow_multiple_containers_and_retained: Count records by actual destination in planner order.
    def test_overflow_multiple_containers_and_retained(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(x=index) for index in range(5)]
        routes = {'Substance': ONE}
        plan = InventoryPlanner(data).plan((SUIT,), routes, overflow=True)
        row = review_rows(data, (SUIT,), routes, labels_for(data), plan)[0]
        self.assertTrue(row.text.endswith('1 Parts to destination + 1 Parts overflow to ' + labels_for(data)[TEN]
                                         + ' + 1 Parts overflow to ' + labels_for(data)[NINE]
                                         + ' + 2 Parts retained (destination full)'))
        self.assertEqual(len(plan.moves), 3)

    # test_retained_same_destination_leave_unknown: Include same-source Parts omitted by planner.stays safely.
    def test_retained_same_destination_leave_unknown(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(), stack('Product', 1), stack('Future<&>', 2)]
        routes = {'Substance': SUIT}
        original = copy.deepcopy(data)
        plan = InventoryPlanner(data).plan((SUIT,), routes)
        live = review_rows(data, (SUIT,), routes, labels_for(data))
        rows = review_rows(data, (SUIT,), routes, labels_for(data), plan)
        self.assertEqual(len(live), 7)
        self.assertEqual(rows, [])
        self.assertNotIn('Future<&>', review_text(data, (SUIT,), routes, labels_for(data), plan))
        self.assertEqual(data, original)
        self.assertFalse(plan.changed)

    # test_no_item_ids_or_amount_totals: IDs never enter output; each complete record is one Part.
    def test_no_item_ids_or_amount_totals(self):
        data = context()
        resolve(data, SUIT)['Slots'] = [stack(), stack('Future'), stack('Product')]
        for record in resolve(data, SUIT)['Slots']:
            record.update(Id='^SECRET_ITEM_<b>&', Amount=999999)
        routes = {'Substance': ONE, 'Product': SUIT}
        plan = InventoryPlanner(data).plan((SUIT,), routes)
        text = review_text(data, (SUIT,), routes, labels_for(data), plan)
        self.assertNotIn('SECRET_ITEM', text)
        self.assertNotIn('999999', text)
        self.assertNotIn('stacks', text.lower())
        self.assertIn('<Synthetic & name>', text)  # Plain-text rendering preserves literal names.
        self.assertIn('1 Parts to destination', text)
        self.assertIn('Nothing has been applied or saved.', text)

    # test_zero_moves_empty_sources_and_expansion_footer: Keep zero routes and never report overflow expansion.
    def test_zero_moves_empty_sources_and_expansion_footer(self):
        data = context()
        resolve(data, SUIT)['Slots'] = []
        routes = {'Substance': ONE}
        plan = InventoryPlanner(data).plan((SUIT,), routes)
        rows = review_rows(data, (SUIT,), routes, labels_for(data), plan)
        self.assertEqual(rows, [])
        self.assertEqual(len(review_rows(data, (SUIT,), routes, labels_for(data))), 6)
        expanded = InventoryPlanner(data).plan((), routes, expand=True)
        text = review_text(data, (), routes, labels_for(data), expanded)
        self.assertIn('No sources selected.', text)
        self.assertIn('1 assigned Destination storages proposed for 120 cells.', text)
        self.assertNotIn(labels_for(data)[TEN], text)
        self.assertNotIn('120 cells', review_text(data, (SUIT,), routes, labels_for(data), plan))

    # test_silent_overflow_growth: Review the movement but disclose explicit expansion only.
    def test_silent_overflow_growth(self):
        data = context()
        resolve(data, ONE)['Slots'] = [stack('Product', x, y) for x in range(10) for y in range(12)]
        routes = {'Substance': ONE}
        plan = InventoryPlanner(data).plan((SUIT,), routes, overflow=True, expand=True)
        text = review_text(data, (SUIT,), routes, labels_for(data), plan)
        self.assertEqual(review_rows(data, (SUIT,), routes, labels_for(data), plan), [])
        self.assertTrue(plan.changed)
        self.assertNotIn('Parts overflow to', text)
        self.assertIn('1 assigned Destination storages proposed for 120 cells.', text)
        self.assertNotIn('overflow expansion', text.lower())

    # test_invalidation_retains_live_rows_without_planning: Extracted real method resets counts and disables Apply.
    def test_invalidation_retains_live_rows_without_planning(self):
        data = context()
        routes, labels = {'Substance': ONE}, labels_for(data)
        fake = SimpleNamespace(controller=Mock(), apply_button=Mock(), preview_button=Mock(), review=Mock(),
                               window=SimpleNamespace(model=SimpleNamespace(get_data=lambda: data)),
                               _selected=lambda: [SUIT], _routing=lambda: routes, labels=labels,
                               expand=SimpleNamespace(isChecked=lambda: False))
        dialog_method('_invalidate', review_html=review_html)(fake)
        fake.controller.invalidate.assert_called_once_with()
        fake.controller.preview.assert_not_called()
        fake.apply_button.setEnabled.assert_called_once_with(False)
        text = fake.review.setHtml.call_args[0][0]
        self.assertIn("-&gt; ", text)
        self.assertIn("&lt;Synthetic &amp; name&gt;", text)
        self.assertNotIn('Parts to destination', text)
        fake.preview_button.setEnabled.assert_called_once_with(True)

    # test_render_uses_same_helper_and_plain_text: Exercise the real presentation method without Qt.
    def test_render_uses_same_helper_and_plain_text(self):
        data = context()
        routes, labels = {'Substance': ONE}, labels_for(data)
        plan = InventoryPlanner(data).plan((SUIT,), routes)
        fake = SimpleNamespace(controller=SimpleNamespace(original=data), _selected=lambda: [SUIT],
                               _routing=lambda: routes, labels=labels, review=Mock())
        dialog_method('_render', review_html=review_html)(fake, plan)
        fake.review.setHtml.assert_called_once_with(review_html(data, [SUIT], routes, labels, plan))
        fake.review.setPlainText.assert_not_called()


    # test_bold_footer_and_safe_transfer_prefix: Escape names and emphasize notices, never the transfer rows.
    def test_bold_footer_and_safe_transfer_prefix(self):
        data, routes = context(), {'Substance': ONE}
        plan = InventoryPlanner(data).plan((SUIT,), routes)
        for proposal in (None, plan):
            html = review_html(data, (SUIT,), routes, labels_for(data), proposal)
            self.assertIn('<p style="margin:0; white-space:pre-wrap">-&gt; (', html)
            self.assertNotIn('<b>-&gt;', html)
            self.assertNotIn('<Synthetic', html)
            self.assertIn('&lt;Synthetic &amp; name&gt;', html)
            self.assertIn('<b>', html)
            self.assertTrue(all(row.text.startswith('-> ') for row in
                                review_rows(data, (SUIT,), routes, labels_for(data), proposal)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
