# File: test_starship_delete.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_starship_delete.py
# Purpose: Exercise real deletion/planning/controller code with synthetic records and widgets, never live saves or app startup.
import ast  # Load actual GUI/controller methods without requiring Qt or initializing the application.
import copy  # Keep each synthetic context and expected preservation snapshot independent.
import json  # Compare synthetic model text with actual planned candidate data.
import sys  # Temporarily provide the real controller's isolated namespace to the actual menu handler.
import unittest  # Execute repeatable policy, cleanup and transaction checks.
from pathlib import Path  # Read only these project sources and bundled empty-slot resources.
from types import SimpleNamespace  # Explicitly synthetic window/navigation interfaces.
from unittest.mock import patch  # Inject synthetic UI dependencies without touching real save operations.
import StarshipDelete as policy  # Test the production pure planner, not a copied implementation.

ROOT = Path(__file__).resolve().parent  # Keep all resource/source access inside this project.
TEMPLATES = policy.load_delete_templates()  # Actual bundled observed donors, not a live-save read.
LOCATION = 259  # Synthetic stand-in for the actual Qt typed-location role.


# fixture: Build a wholly synthetic active context with ordinary, custom, Iron Vulture and two Corvette ships.
def fixture():
    ships = [copy.deepcopy(TEMPLATES["ordinary"]) for _ in range(12)]  # Fixed twelve-position ownership scaffold.
    appearance = [copy.deepcopy(TEMPLATES["appearance"]) for _ in range(26)]  # Include nonship entries for preservation checks.
    for index in (0, 1, 5, 7, 8):  # Occupied names/resources are synthetic test markers.
        ships[index]["Name"] = f"SYNTHETIC slot {index}"  # Deliberately not any real user ship identity.
        ships[index]["Resource"]["Filename"] = policy.CORVETTE_SCENE if index in (5, 8) else "MODELS/COMMON/SPACECRAFT/FIGHTERS/FIGHTER_PROC.SCENE.MBIN"  # Canonical family marker.
        ships[index]["unrelated_ship_field"] = {"synthetic": index}  # Surviving unknown fields must remain unchanged.
    ships[7]["Resource"]["Filename"] = "MODELS/COMMON/SPACECRAFT/DROPSHIPS/DROPSHIP_PROC.SCENE.MBIN"  # Synthetic custom Hauler/Iron Vulture family case.
    for index in (1, 7):  # Both sides of the six-slot appearance mapping boundary.
        appearance[policy.customisation_index(index)]["CustomData"]["DescriptorGroups"] = [f"^SYNTHETIC_PART_{index}"]  # Custom/Iron Vulture detection.
    appearance[3]["CustomData"]["Colours"] = [{"synthetic_ordinary_colour": True}]  # Ordinary deletion must preserve custom-only locations.
    appearance[16] = {"synthetic_nonship": [1, 2, 3]}  # Explicitly unrelated appearance entry.
    bases = [{"BaseType": {"PersistentBaseTypes": "HomePlanetBase"}, "UserData": 5, "Objects": [{"UserData": 5}]}]  # Matching integer alone is not a ship build.
    bases.extend({"BaseType": {"PersistentBaseTypes": "PlayerShipBase"}, "UserData": i, "Objects": [{"UserData": 9000 + i, "synthetic_parts": [1, 2]}]} for i in (5, 8))  # Header link differs from packed object data.
    player = {"ShipOwnership": ships, "CharacterCustomisationData": appearance, "ShipUsesLegacyColours": [True] * 12, "PersistentPlayerBases": bases, "PrimaryShip": 5, "CorvetteEditAssociatedShipIndex": 5, "CorvetteEditShipName": "synthetic draft", "CorvetteDraftShipSeed": [False, "0x123"], "ShipMoveableContents": [{"synthetic": "preserve"}], "unknown_player_field": [1, {"keep": True}]}  # Preserve every excluded field.
    return {"PlayerStateData": player, "unrelated_context_data": {"synthetic": "preserve"}}  # Not a decoded real save fixture.


class PlannerTests(unittest.TestCase):  # Verify complete results and atomic no-op/refusal semantics.
    # test_empty_templates: Validate complete observed donors and the frozen-build resource declaration.
    def test_empty_templates(self):
        for kind in ("ordinary", "corvette"):  # The distinct donors are both empty but not interchangeable.
            self.assertFalse(policy._occupied(TEMPLATES[kind]))  # Resource filename alone determines occupancy.
            self.assertEqual(TEMPLATES[kind]["VehicleCargo"], [])  # Keep the complete empty ownership schema.
        self.assertNotEqual(TEMPLATES["ordinary"], TEMPLATES["corvette"])  # Preserve the observed Corvette-specific vacant record.
        self.assertIn("('starship_delete_templates.json', '.')", (ROOT / "BBB_NMS_Save_File_Manipulator.spec").read_text())  # Included in packaged builds.

    # test_ordinary: Replace only complete ownership and its legacy-colour flag for an ordinary ship.
    def test_ordinary(self):
        original = fixture()  # All surviving data is independently observable.
        result, deleted = policy.plan_starship_deletions(original, [0])  # Delete an ordinary occupied slot.
        expected = copy.deepcopy(original)  # Allowlist exactly the intended changed regions.
        expected["PlayerStateData"]["ShipOwnership"][0] = TEMPLATES["ordinary"]  # Full donor, not partial inventory clearing.
        expected["PlayerStateData"]["ShipUsesLegacyColours"][0] = False  # Only the target flag changes.
        self.assertEqual(result, expected)  # No customisation, build, editor or selected-ship changes.
        self.assertEqual(deleted, [0])  # Zero-based ownership identity retained.
        self.assertEqual(original, fixture())  # Planner never mutates its input.

    # test_custom_both_mappings_and_iron_vulture: All custom part-defined types use the common appearance reset.
    def test_custom_both_mappings_and_iron_vulture(self):
        original = fixture()  # Custom synthetic slots stand in for the common custom rule and tested Iron Vulture rule.
        result, deleted = policy.plan_starship_deletions(original, [1, 7])  # Cross the ownership/customisation mapping discontinuity.
        expected = copy.deepcopy(original)  # No unrelated data may change.
        for index in (1, 7):  # Each replaced record must be an independent whole donor.
            expected["PlayerStateData"]["ShipOwnership"][index] = TEMPLATES["ordinary"]  # Shared approved empty ownership.
            expected["PlayerStateData"]["CharacterCustomisationData"][policy.customisation_index(index)] = TEMPLATES["appearance"]  # Fixed-position canonical reset.
            expected["PlayerStateData"]["ShipUsesLegacyColours"][index] = False  # Clear only the deleted flag.
        self.assertEqual(result, expected)  # Includes preservation of unknown fields and appearance index 16.
        self.assertEqual(deleted, [1, 7])  # Stable indices, no compaction.
        result["PlayerStateData"]["ShipOwnership"][1]["Inventory"]["Slots"].append({"synthetic": True})  # Probe independence after planning.
        self.assertEqual(result["PlayerStateData"]["ShipOwnership"][7]["Inventory"]["Slots"], [])  # No aliased donors.
        self.assertEqual(TEMPLATES["ordinary"]["Inventory"]["Slots"], [])  # The resource donor itself is unchanged.

    # test_corvette: Remove only the complete uniquely linked build and keep a real selected ship.
    def test_corvette(self):
        original = fixture()  # The target Corvette is both selected and editor-referenced.
        result, deleted = policy.plan_starship_deletions(original, [5])  # Remove the current ship with four survivors.
        expected = copy.deepcopy(original)  # Whole-context preservation except this explicit allowlist.
        player = expected["PlayerStateData"]  # Expected changes all occur in the same active branch.
        player["ShipOwnership"][5] = TEMPLATES["corvette"]  # Use the actual observed Corvette vacant record.
        player["ShipUsesLegacyColours"][5] = False  # Delete its parallel colour flag.
        player["CharacterCustomisationData"][8] = TEMPLATES["appearance"]  # Corvette slot 5 maps to appearance 8.
        del player["PersistentPlayerBases"][1]  # Ground base and second Corvette build remain intact/in order.
        player["PrimaryShip"], player["CorvetteEditAssociatedShipIndex"] = 0, -1  # Deterministic occupied fallback and conditional editor clear.
        self.assertEqual(result, expected)  # No packed object UserData, draft, movable contents or unknown-field edits.
        self.assertEqual(deleted, [5])  # No ownership-array shortening.
        self.assertEqual(original, fixture())  # Atomic independent candidate.

    # test_last_ship_and_combined_request: Reject the entire request whenever it would leave zero occupied ships.
    def test_last_ship_and_combined_request(self):
        for indices in ([0, 1, 5, 7, 8], [0, 1, 2, 5, 7, 8, 8]):  # Empty positions and duplicates must not bypass the combined count.
            context = fixture()  # No mutations from the preceding refusal.
            with self.assertRaisesRegex(policy.LastShipDeletionError, "^" + policy.LAST_SHIP_NOTICE + "$"):
                policy.plan_starship_deletions(context, indices)  # No partial application.
            self.assertEqual(context, fixture())  # Every original ship is preserved.
        context = fixture()  # Build a separate one-occupied-ship case.
        for index in (0, 1, 7, 8):
            context["PlayerStateData"]["ShipOwnership"][index] = copy.deepcopy(TEMPLATES["ordinary"])  # Only Corvette 5 remains.
        with self.assertRaises(policy.LastShipDeletionError):
            policy.plan_starship_deletions(context, [5])  # Same notice even for the final Corvette.

    # test_empty_noop_and_filename_only_occupancy: Empty resource identity wins over stale names/seeds.
    def test_empty_noop_and_filename_only_occupancy(self):
        context = fixture()  # Slot 2 has no occupied resource.
        context["PlayerStateData"]["ShipOwnership"][2]["Name"] = "stale synthetic name"  # Must not become a sixth real ship.
        with patch.object(policy, "load_delete_templates", side_effect=AssertionError("No donor read for empty-slot no-op")):
            candidate, indices = policy.plan_starship_deletions(context, [2, 2])  # No donor I/O or mutation.
        self.assertEqual(candidate, context)  # Entire request is semantically unchanged.
        self.assertEqual(indices, [])  # No false success.

    # test_unnamed_ship_and_unrelated_editor: Names never drive occupancy or conditional editor cleanup.
    def test_unnamed_ship_and_unrelated_editor(self):
        context = fixture()  # Current Corvette editor points to 5.
        context["PlayerStateData"]["ShipOwnership"][0]["Name"] = ""  # Real resource, deliberately unnamed ship.
        candidate, indices = policy.plan_starship_deletions(context, [0])  # Still delete this occupied slot.
        self.assertEqual(indices, [0])  # Empty display name is not an empty slot.
        self.assertEqual(candidate["PlayerStateData"]["CorvetteEditAssociatedShipIndex"], 5)  # Not the deleted ship.
        self.assertEqual(candidate["PlayerStateData"]["PrimaryShip"], 5)  # Existing selected survivor unchanged.
        context["PlayerStateData"]["CorvetteEditAssociatedShipIndex"] = 6  # Game-observed orphaned reference to another slot.
        candidate, _ = policy.plan_starship_deletions(context, [5])  # Deleting a different Corvette must not repair it.
        self.assertEqual(candidate["PlayerStateData"]["CorvetteEditAssociatedShipIndex"], 6)  # Explicit leave-alone policy.

    # test_missing_or_duplicate_build_atomic_refusal: Never guess the build or delete only part of a multi-request.
    def test_missing_or_duplicate_build_atomic_refusal(self):
        for duplicate in (False, True):
            context = fixture()  # Work on an independent malformed synthetic source.
            if duplicate:
                context["PlayerStateData"]["PersistentPlayerBases"].append(copy.deepcopy(context["PlayerStateData"]["PersistentPlayerBases"][1]))  # Ambiguous header linkage.
            else:
                del context["PlayerStateData"]["PersistentPlayerBases"][1]  # Missing target Corvette build.
            before = copy.deepcopy(context)  # Allow no partial ordinary-ship cleanup either.
            with self.assertRaisesRegex(ValueError, "uniquely linked build"):
                policy.plan_starship_deletions(context, [0, 5])  # Ordinary and bad Corvette are one transaction.
            self.assertEqual(context, before)  # No input mutations despite the later build refusal.

    # test_bad_shapes_refused: Invalid structures and identities must not be reinterpreted as empty records.
    def test_bad_shapes_refused(self):
        for mutate in (lambda p: p["ShipOwnership"].pop(), lambda p: p["ShipUsesLegacyColours"].pop(), lambda p: p["ShipOwnership"][2].update(Resource=None), lambda p: p.update(PrimaryShip=True), lambda p: p["CharacterCustomisationData"][4].update(CustomData=None)):
            context = fixture()  # Each unsupported shape is independently checked.
            mutate(context["PlayerStateData"])  # Introduce only a synthetic defect.
            before = copy.deepcopy(context)  # Preserve even malformed original input.
            with self.assertRaises(ValueError):
                policy.plan_starship_deletions(context, [1])  # Refuse before any candidate publication.
            self.assertEqual(context, before)  # No repair or compaction.


    # test_only_one_survivor_and_no_compaction: A combined delete can leave one real ship but cannot remove that final survivor.
    def test_only_one_survivor_and_no_compaction(self):
        context = fixture()  # Five synthetic occupied ownership positions.
        candidate, deleted = policy.plan_starship_deletions(context, [0, 1, 5, 8])  # Retain only the custom ship at ownership 7.
        self.assertEqual(deleted, [0, 1, 5, 8])  # Every chosen whole ship is removed atomically.
        self.assertEqual(candidate["PlayerStateData"]["PrimaryShip"], 7)  # Fallback identifies the surviving ship, not position zero.
        self.assertEqual(len(candidate["PlayerStateData"]["ShipOwnership"]), 12)  # Fixed ownership shape retained.
        self.assertEqual(candidate["PlayerStateData"]["ShipOwnership"][7], context["PlayerStateData"]["ShipOwnership"][7])  # Survivor payload unchanged.
        with self.assertRaises(policy.LastShipDeletionError):
            policy.plan_starship_deletions(candidate, [7])  # The next request cannot delete the final custom ship.


    # test_known_ordinary_and_special_scene_coverage: Every current non-Corvette family/variant follows the shared ordinary handler.
    def test_known_ordinary_and_special_scene_coverage(self):
        from StarshipUpgrade import BASE_SCENES, SPECIAL_SCENES  # Reuse the app's actual known scene roster, not invented display names.
        for relative, family in {**BASE_SCENES, **SPECIAL_SCENES}.items():  # Include ordinary Living/Sentinel/Exotic and special variants.
            if family == "corvette":  # Dedicated Corvette cleanup is exercised separately with a uniquely linked build.
                continue  # Do not pretend Corvette uses ordinary deletion.
            with self.subTest(scene=relative):  # A failure identifies the exact affected resource.
                context = fixture()  # Only replace the synthetic ordinary slot's resource identity.
                context["PlayerStateData"]["ShipOwnership"][0]["Resource"]["Filename"] = "MODELS/COMMON/SPACECRAFT/" + relative  # Known scene.
                plan = policy.StarshipDeletionPlan(context, [0])  # Exercise actual strategy selection.
                plan._validate_linked_data()  # Establish the same validated complete source bundle as production.
                self.assertIs(type(plan._prepare_handlers()[0]), policy.OrdinaryShipDeletion)  # All approved shared-rule variants.
                candidate, deleted = plan.build()  # Apply the real planner, not just a classifier assertion.
                self.assertEqual(candidate["PlayerStateData"]["ShipOwnership"][0], TEMPLATES["ordinary"])  # Complete common empty donor.
                self.assertEqual(candidate["PlayerStateData"]["CharacterCustomisationData"], context["PlayerStateData"]["CharacterCustomisationData"])  # Ordinary associated state is untouched.
                self.assertEqual(deleted, [0])  # Exact fixed position, no compaction.

    # test_production_function_size_standard: Keep every deletion function/method within Bill's twenty-line target.
    def test_production_function_size_standard(self):
        for filename in ("StarshipDelete.py", "StarshipDeleteController.py"):  # Limit this check to the current deletion implementation.
            tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))  # Inspect real on-disk production source.
            for node in ast.walk(tree):  # Include class methods as well as public/module helpers.
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):  # No hiding a long routine inside a class.
                    with self.subTest(file=filename, function=node.name, line=node.lineno):  # Identify the exact violating definition.
                        self.assertLessEqual(node.end_lineno - node.lineno + 1, 20)  # Count physical lines, not just statements.


class SignalWidget:  # Small synthetic signal blocker and raw-text editor, not a Qt widget.
    # __init__: Retain enough state to verify publication, rollback and prior blocked states.
    def __init__(self, text=""):
        self.blocked, self.text = False, text  # Explicitly isolated fixture values.

    # blockSignals: Match Qt's return-of-previous-state contract.
    def blockSignals(self, value):
        old, self.blocked = self.blocked, value  # Store the new state without sending events.
        return old  # The controller must restore this exact prior state.

    # toPlainText: Expose only synthetic editor text.
    def toPlainText(self):
        return self.text  # No real app or file read.

    # setPlainText: Store the exact rollback/published editor content.
    def setPlainText(self, text):
        self.text = text  # Formatting preservation is independently observable.


class Model(SignalWidget):  # Model interface records actual publication calls.
    # __init__: Keep one synthetic editable context and a publication counter.
    def __init__(self, context):
        super().__init__()  # Initialize the shared Qt-like signal-blocking contract.
        self.data, self.writes = copy.deepcopy(context), 0  # No retained/full save or disk access.

    # get_data: Return the current synthetic editable branch.
    def get_data(self):
        return self.data  # Production controller sees the same model interface.

    # set_data: Record whole-context publications, including an explicit rollback assignment.
    def set_data(self, data):
        self.data, self.writes = data, self.writes + 1  # No signal side effects are fabricated.


class Window:  # Synthetic four-tab host exercising real controller transaction methods.
    # __init__: Construct editor/dirty/source state without initializing the application.
    def __init__(self):
        self.model, self._nms_loading, self.enabled, self.nms_data_changed = Model(fixture()), False, True, False  # Clean synthetic starting state.
        self.nms_source, self.refreshes, self.fail_refresh = {"synthetic_source": True}, 0, False  # Source object identity matters.
        self._starship_delete_running = False  # Match the real dynamically assigned reentrancy guard.
        self._nms_tabs = [SimpleNamespace(text_edit=SignalWidget("  synthetic synchronized formatting  "), tree_widget=SignalWidget(), tree_synced=True, update_tree_synced_indicator=lambda green_if_true: None) for _ in range(4)]  # Isolated four-tab interface.

    # isEnabled: Report the existing window interaction state.
    def isEnabled(self):
        return self.enabled  # No actual desktop/window access.

    # setEnabled: Record the production transaction's guard changes.
    def setEnabled(self, value):
        self.enabled = value  # Tests require restoration after success and failure.

    # _capture_nms_editors: Mirror the exact established rollback contract.
    def _capture_nms_editors(self):
        return [(tab.text_edit.toPlainText(), tab.tree_synced) for tab in self._nms_tabs]  # No user text is read.

    # _refresh_nms_tabs: Observe coherent publications and optionally inject one synthetic rendering failure.
    def _refresh_nms_tabs(self):
        self.refreshes += 1  # Explicitly count success and rollback refreshes.
        for tab in self._nms_tabs:
            tab.text_edit.setPlainText(json.dumps(self.model.get_data()))  # All synthetic views see the complete same candidate.
        if self.fail_refresh and self.refreshes == 1:  # Fail only after a candidate was published and views started refreshing.
            raise RuntimeError("synthetic rendering failure")  # The real controller must restore the original context.

    # _mark_nms_changed: Record actual memory-only edits as unsaved.
    def _mark_nms_changed(self, reason):
        self.nms_data_changed = True  # No save or backup API exists on this fixture.

    # _update_nms_led: Supply only the rollback/status contract.
    def _update_nms_led(self):
        pass  # No claim of actual Qt painting.


class Messages:  # Capture exactly which production notice/button arguments were used.
    Ok, information_calls, warning_calls = 1024, [], []  # Synthetic enum value is intentionally not a real Qt dependency.

    # information: Record the exact last-ship notice and allowed/default buttons.
    @classmethod
    def information(cls, *args):
        cls.information_calls.append(args)  # No modal UI is opened.

    # warning: Record honest preflight/rollback failures.
    @classmethod
    def warning(cls, *args):
        cls.warning_calls.append(args)  # Preserve error text for test assertions.


# controller_namespace: Execute production controller definitions against explicit synthetic toolkit dependencies.
def controller_namespace():
    source = ast.parse((ROOT / "StarshipDeleteController.py").read_text(encoding="utf-8"))  # Actual application code.
    body = [node for node in source.body if not isinstance(node, (ast.Import, ast.ImportFrom))]  # Never import Qt/app startup.
    env = {"copy": copy, "QDialog": SimpleNamespace(Accepted=1), "QMessageBox": Messages, "QT_DATA_JSON_LOCATION": LOCATION, "same_json": lambda a, b: type(a) is type(b) and a == b, "LAST_SHIP_NOTICE": policy.LAST_SHIP_NOTICE, "LastShipDeletionError": policy.LastShipDeletionError, "plan_starship_deletions": policy.plan_starship_deletions}  # Dependencies only, not reimplemented controller logic.
    exec(compile(ast.Module(body=body, type_ignores=[]), "actual-starship-delete-controller", "exec"), env)  # Run the real methods.
    return env  # Every request follows production selection, planning, confirmation and publication.


# selected_tree: Build synthetic typed-location nodes with a real fixture context and source snapshot.
def selected_tree(window, paths):
    tree = SimpleNamespace(parent=SimpleNamespace(main_window=window, model_context="tab2"), json_navigation=SimpleNamespace(valid=True, snapshot=copy.deepcopy(window.model.get_data()["PlayerStateData"]["ShipOwnership"])))  # No decorated-label parsing.
    tree.right_button_selected_nodes = [SimpleNamespace(treeWidget=lambda: tree, data=lambda column, role, path=path: {"path": path, "kind": "value"}) for path in paths]  # Paths distinguish complete ships and descendants.
    return tree  # Supports the actual selection/controller interface.


class ControllerTests(unittest.TestCase):  # No PyQt, MainWindow constructor, game launch or disk-save behavior.
    # setUp: Start each request with fresh production definitions and isolated UI records.
    def setUp(self):
        self.env, self.window, self.confirmations = controller_namespace(), Window(), []  # Independent transaction host.
        Messages.information_calls, Messages.warning_calls = [], []  # No prior modal-message results.

    # confirm: Return a production-compatible synthetic confirmation constructor with an optional modal callback.
    def confirm(self, accepted=True, callback=None):
        def factory(count):  # Capture the actual deduplicated occupied target count.
            self.confirmations.append(count)  # Empty slots/descendants must not inflate confirmation.
            def execute():  # Simulate only the modal result and optional explicitly injected intervening event.
                if callback:
                    callback()  # Test stale-source/data/reentrancy guards.
                return 1 if accepted else 0  # Match the injected QDialog.Accepted constant.
            return SimpleNamespace(exec_=execute)  # No actual confirmation window.
        return factory  # Reuse this interface across all real controller requests.

    # run_request: Execute the real controller using the selected synthetic tree paths.
    def run_request(self, paths, accepted=True, callback=None):
        return self.env["run_starship_delete"](selected_tree(self.window, paths), self.confirm(accepted, callback))  # Real function path.

    # test_success_commits_once_and_marks_dirty: Ownership and every affected linked structure publish together.
    def test_success_commits_once_and_marks_dirty(self):
        source = self.window.nms_source  # Retained source object must not change on memory-only deletion.
        self.assertTrue(self.run_request([[5], [5, "Inventory"], [2]]))  # Descendant and empty selected slot coalesce/no-op.
        expected, _ = policy.plan_starship_deletions(fixture(), [5])  # Whole actual planner result.
        self.assertEqual(self.window.model.get_data(), expected)  # Complete coherent model result.
        self.assertEqual((self.window.model.writes, self.window.refreshes, self.confirmations), (1, 1, [1]))  # One commit, not shortened-array writes.
        self.assertTrue(self.window.nms_data_changed)  # Remains unsaved.
        self.assertIs(self.window.nms_source, source)  # No source replacement/full-save write.
        self.assertTrue(self.window.enabled)  # Interaction restored.
        self.assertFalse(self.window._nms_loading or self.window._starship_delete_running)  # Guards released.
        self.assertFalse(self.window.model.blocked)  # Signals restored.
        self.assertFalse(Messages.warning_calls)  # No hidden failure.

    # test_exact_ok_only_last_ship_notice: Combined deletion refusal shows exact text and no confirmation.
    def test_exact_ok_only_last_ship_notice(self):
        self.assertFalse(self.run_request([[i] for i in (0, 1, 5, 7, 8)]))  # Would remove all five occupied ships.
        self.assertEqual(Messages.information_calls[0][2:], (policy.LAST_SHIP_NOTICE, Messages.Ok, Messages.Ok))  # Exact text, OK only/default.
        self.assertEqual(self.confirmations, [])  # Do not offer a confirmation that could bypass the policy.
        self.assertEqual(self.window.model.writes, 0)  # No partial changes.
        self.assertFalse(self.window.nms_data_changed)  # Unchanged saved/unsaved state.

    # test_cancel_and_empty_noops: Cancel and selecting an already-empty position cannot create edits.
    def test_cancel_and_empty_noops(self):
        self.assertFalse(self.run_request([[5]], accepted=False))  # Preserve the existing Cancel semantics.
        self.assertFalse(self.run_request([[2]]))  # No second confirmation for empty slot.
        self.assertEqual(self.confirmations, [1])  # Only the occupied first request needed confirmation.
        self.assertEqual(self.window.model.get_data(), fixture())  # Every structure retained.
        self.assertEqual(self.window.model.writes, 0)  # No unnecessary re-publication.
        self.assertFalse(self.window.nms_data_changed)  # No-op dirty-state preservation.

    # test_pending_raw_stale_tree_root_and_nested_refused: Never silently overwrite work or guess a whole-ship target.
    def test_pending_raw_stale_tree_root_and_nested_refused(self):
        self.window._nms_tabs[3].tree_synced = False  # An unrelated tab contains pending raw text.
        self.assertFalse(self.run_request([[5]]))  # Refuse before confirmation/publication.
        self.window._nms_tabs[3].tree_synced = True  # Now test structural selection safety independently.
        self.assertFalse(self.run_request([[]]))  # Root list deletion must never compact all ownership data.
        self.assertFalse(self.run_request([[5, "Inventory"]]))  # A child alone must not unexpectedly delete its whole ship.
        tree = selected_tree(self.window, [[5]])  # Synthetic stale path metadata.
        tree.json_navigation.valid = False  # Matches actual production invalidation after structural edits.
        self.assertFalse(self.env["run_starship_delete"](tree, self.confirm()))  # Fail closed.
        self.assertEqual(self.window.model.writes, 0)  # All four refusals retain the model.
        self.assertEqual(len(Messages.warning_calls), 4)  # Each refusal is explained.

    # test_intervening_source_or_model_change_refused: Modal confirmation cannot apply a stale request.
    def test_intervening_source_or_model_change_refused(self):
        self.assertFalse(self.run_request([[5]], callback=lambda: setattr(self.window, "nms_source", {"different_source": True})))  # Identical data, different loaded source.
        self.assertEqual(self.window.model.writes, 0)  # Do not modify newer source state.
        self.assertFalse(self.run_request([[5]], callback=lambda: self.window.model.data.update(newer_edit=True)))  # Intervening model edit.
        self.assertTrue(self.window.model.data["newer_edit"])  # Do not roll back the user's intervening edit.
        self.assertEqual(self.window.model.writes, 0)  # No stale candidate publication.

    # test_refresh_failure_rolls_back_model_text_dirty_and_guards: Exercise real post-publication failure recovery.
    def test_refresh_failure_rolls_back_model_text_dirty_and_guards(self):
        before_text = self.window._capture_nms_editors()  # Exact synthetic user formatting, not regenerated text.
        self.window.fail_refresh = True  # Inject one actual exception through the production publication path.
        self.window._nms_tabs[0].tree_widget.blocked = True  # Preserve an already-blocked widget's prior ownership.
        self.assertFalse(self.run_request([[5]]))  # Failure must never be reported as deletion success.
        self.assertEqual(self.window.model.get_data(), fixture())  # Restore all ownership and linked data.
        self.assertEqual(self.window._capture_nms_editors(), before_text)  # Restore exact raw formatting/sync flags.
        self.assertEqual((self.window.model.writes, self.window.refreshes), (2, 2))  # Candidate then original, both explicitly refreshed.
        self.assertFalse(self.window.nms_data_changed)  # Failed transaction is not a successful unsaved edit.
        self.assertTrue(self.window._nms_tabs[0].tree_widget.blocked)  # Prior blocked state retained.
        self.assertFalse(self.window._nms_loading or self.window._starship_delete_running or self.window.model.blocked)  # All owned guards released.
        self.assertTrue(self.window.enabled)  # No stranded disabled window.
        self.assertIn("synthetic rendering failure", Messages.warning_calls[-1][2])  # Honest actual error.

    # test_menu_routes_actual_single_delete_method: Actual CustomTreeWidget method dispatches to the guarded controller.
    def test_menu_routes_actual_single_delete_method(self):
        source = ast.parse((ROOT / "CustomTreeWidget.py").read_text(encoding="utf-8"))  # Real production tree source.
        cls = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "CustomTreeWidget")  # No imports/startup.
        methods: list[ast.stmt] = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in ("delete_node", "delete_tree_nodes_selected")]  # Actual entry/dispatch methods.
        env = {"logger": SimpleNamespace(debug=lambda *args: None), "DeleteTreeNodesSelectedDialog": self.confirm(), "QDialog": SimpleNamespace(Accepted=1)}  # Synthetic dialog/logger only.
        exec(compile(ast.Module(body=methods, type_ignores=[]), "actual-tree-delete-menu", "exec"), env)  # Execute the real menu handlers.
        tree = selected_tree(self.window, [[5]])  # Same typed slot metadata as the production builder.
        tree.delete_tree_nodes_selected = lambda: env["delete_tree_nodes_selected"](tree)  # Bind the actual handler.
        with patch.dict(sys.modules, {"StarshipDeleteController": SimpleNamespace(run_starship_delete=self.env["run_starship_delete"])}):
            env["delete_node"](tree, tree.right_button_selected_nodes[0])  # Real single-node menu path delegates through safe multi-handler.
        self.assertEqual(self.window.model.writes, 1)  # The integration actually committed a complete planned deletion.
        self.assertEqual(len(self.window.model.get_data()["PlayerStateData"]["ShipOwnership"]), 12)  # No generic list shortening.


    # test_other_tab_keeps_generic_deletion_route: The starship dispatch must not change ordinary deletion on other tabs.
    def test_other_tab_keeps_generic_deletion_route(self):
        source = ast.parse((ROOT / "CustomTreeWidget.py").read_text(encoding="utf-8"))  # Actual shared tree implementation.
        cls = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "CustomTreeWidget")  # Avoid application imports.
        method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "delete_tree_nodes_selected")  # Real dispatch method.
        env = {"logger": SimpleNamespace(debug=lambda *args: None), "DeleteTreeNodesSelectedDialog": self.confirm(accepted=False), "QDialog": SimpleNamespace(Accepted=1)}  # Cancel before destructive generic actions.
        exec(compile(ast.Module(body=[method], type_ignores=[]), "actual-other-tab-delete", "exec"), env)  # Execute actual shared code.
        tree = SimpleNamespace(parent=SimpleNamespace(model_context="tab1"), right_button_selected_nodes=[object()])  # Nonstarship synthetic tab.
        with patch.dict(sys.modules, {"StarshipDeleteController": SimpleNamespace(run_starship_delete=lambda *args: self.fail("Wrong tab reached ship deletion"))}):
            env["delete_tree_nodes_selected"](tree)  # Must use the unchanged generic confirmation/cancel branch.
        self.assertEqual(self.confirmations, [1])  # Existing nonstarship confirmation still called.
        self.assertEqual(self.window.model.writes, 0)  # No starship-model transaction.


if __name__ == "__main__":  # Running this file never initializes Qt or real application/live-save access.
    unittest.main(verbosity=2)  # Print genuine individual test results and the actual total.
