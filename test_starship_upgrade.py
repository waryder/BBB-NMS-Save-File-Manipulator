# File: test_starship_upgrade.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_starship_upgrade.py
# Purpose: Isolated row-80/81 fixtures and AST-extracted controller checks; no Qt app or real saves.
import ast  # Exercise controller functions without importing the GUI application or PyQt.
import copy  # Keep all synthetic fixtures independent.
import json  # Read only the integrated JSON donor bundle.
import os  # Verify source/frozen resource path decisions.
import sys  # Avoid bytecode writes and expose the frozen-resource marker to isolated tests.
import unittest  # Provide a repeatable real execution result.
from collections import Counter  # Assert reference base-technology multiplicities.
from unittest.mock import patch  # Control random selection in isolated tests without seeding production behavior.
from html import escape  # Match the real result formatter's safe text dependency.
from pathlib import Path  # Resolve repository resources independently of current working directory.
from types import SimpleNamespace  # Supply isolated model, checkbox, and dialog fixtures.
from typing import Any  # Mark deliberately mixed synthetic JSON values explicitly.
sys.dont_write_bytecode = True  # No module cache writes belong to these fixture checks.
from StarshipUpgrade import BASE_SCENES, SPECIAL_SCENES, plan_upgrades, reference_family, ship_label, upgrade_ship, _base_tech_id, _missing_items  # Real logic.

ROOT = Path(__file__).resolve().parent  # All reference/source reads remain inside this project.


# load_reference: Read the actual integrated donor, never a historical manifest or a game save.
def load_reference(filename):
    return json.loads((ROOT / "starship_upgrade_references" / filename).read_text(encoding="utf-8-sig"))  # Read only.


# fixture: Derive a synthetic target with distinct name, seed, cargo, layout and unknown fields.
def fixture(family="fighter", items=0, capacity=80):
    target = load_reference(f"reference_{family}.json")  # Use a donor schema but not any real ownership data.
    target["Name"] = "Fixture <ship> & preserved"  # Include HTML-sensitive name text.
    target["Resource"]["Seed"] = [True, "0x1234567890ABCDEF"]  # Deliberately different target identity.
    target["Resource"]["AltId"] = "fixture-custom-build"  # Preserve complete custom resource data.
    target["UnknownFutureField"] = {"preserve": [1, 2, 3]}  # Prove unknown fields survive.
    target["Inventory"]["Class"] = {"InventoryClass": "C"}  # Force an observable approved class change.
    target["Inventory_Cargo"]["Class"] = {"InventoryClass": "B"}  # Cargo class alone may change.
    target["Inventory"]["BaseStatValues"][0]["Value"] = 1.0  # Force a selective stat change.
    target["Inventory_TechOnly"]["BaseStatValues"][0]["Value"] = 2.0  # Force the other approved stat change.
    tech = target["Inventory_TechOnly"]  # Modify only synthetic target layout for fixture setup.
    tech["Slots"] = tech["Slots"][:items]  # Simulate incomplete equipment without touching actual donors.
    tech["Width"], tech["Height"] = 10, 8  # Allow preserved extras plus full ordinary reference contents.
    tech["ValidSlotIndices"] = [{"X": i % 10, "Y": i // 10} for i in range(capacity)]  # Enabled target cells.
    return target  # Each test receives an independent mutable fixture.


# overflow_fixture: Construct one preserved extra item that makes the sixty-item Fighter donor impossible to fit.
def overflow_fixture():
    target = fixture(items=1, capacity=60)  # Existing item occupies a valid cell.
    target["Inventory_TechOnly"]["Slots"][0]["Id"] = "^PRESERVED_EXTRA"  # No exact donor occurrence is satisfied.
    return target  # Upgrade must report insufficient space without altering the ship.


# controller_functions: Compile actual top-level handlers without GUI imports or app initialization.
def controller_functions():
    tree = ast.parse((ROOT / "StarshipUpgradeController.py").read_text(encoding="utf-8"))  # Inspect actual source.
    functions: list[ast.stmt] = [node for node in tree.body if isinstance(node, ast.FunctionDef)]  # Qt class is not instantiated here.
    environment = {"copy": copy, "json": json, "escape": escape, "plan_upgrades": plan_upgrades, "ship_label": ship_label}  # Real dependencies.
    exec(compile(ast.Module(body=functions, type_ignores=[]), "controller-fixture", "exec"), environment)  # Execute actual handlers.
    return environment  # Tests add only fake UI endpoints, never fabricated donor data.


class FakeModel:  # Isolated model records commits and actual dirty transitions.
    # __init__: Retain synthetic selected-context data and zero commits.
    def __init__(self, data):
        self.data, self.commits, self.dirty = data, 0, False  # No real Qt model or save target.

    # get_data: Match the actual shared model accessor.
    def get_data(self):
        return self.data  # Allow the real controller's stale-selection comparison.

    # set_data: Capture one real candidate publication and simulate the existing dirty observer.
    def set_data(self, data):
        self.data, self.commits, self.dirty = data, self.commits + 1, True  # Genuine fixture mutation.


class UpgradeTests(unittest.TestCase):  # Exercise only fixtures, bundled references and isolated handlers.
    # test_every_current_donor: Verify all eleven donors, allowed fields, existing-tech prefix, and idempotence.
    def test_every_current_donor(self):
        files = sorted((ROOT / "starship_upgrade_references").glob("reference_*.json"))  # Actual bundled inventory.
        self.assertEqual(len(files), 11)  # Detect accidental missing/additional reference bundles.
        for path in files:  # Exercise the real current schemas and empty Corvette donor.
            with self.subTest(reference=path.name):  # Identify any family-specific failure.
                family = path.stem.removeprefix("reference_")  # Use the approved mapping suffix.
                target, reference = fixture(family, items=1), load_reference(path.name)  # Independent actual-schema fixture.
                before, donor_before = copy.deepcopy(target), copy.deepcopy(reference)  # Prove neither input changes.
                upgraded, added = upgrade_ship(target, reference)  # Execute the real selective implementation.
                self.assertEqual(target, before)  # Planner must not mutate the original ship.
                self.assertEqual(reference, donor_before)  # Never mutate the donor, including Corvette slots.
                old_slots = before["Inventory_TechOnly"]["Slots"]  # Preserve every existing item byte-equivalent semantically.
                self.assertEqual(upgraded["Inventory_TechOnly"]["Slots"] if family != "corvette" else upgraded["Inventory_TechOnly"]["Slots"][:len(old_slots)], reference["Inventory_TechOnly"]["Slots"] if family != "corvette" else old_slots)  # Retain order/flags/cells.
                restored = copy.deepcopy(upgraded)  # Remove only the explicitly authorized changes for comparison.
                for inv, key in [("Inventory", "BaseStatValues"), ("Inventory_TechOnly", "BaseStatValues"), ("Inventory", "Class"), ("Inventory_Cargo", "Class")]:
                    self.assertEqual(upgraded[inv][key], reference[inv][key])  # Exact full lists/classes including markers.
                    restored[inv][key] = copy.deepcopy(before[inv][key])  # Restore allowed fields only.
                restored["Inventory_TechOnly"]["Slots"] = copy.deepcopy(old_slots)  # Strip additions only.
                for key in ("Width", "Height", "ValidSlotIndices", "NumSlotsFromTech"):
                    restored["Inventory_TechOnly"][key] = copy.deepcopy(before["Inventory_TechOnly"][key])  # New capacity allowlist.
                self.assertEqual((upgraded["Inventory_TechOnly"]["Width"], upgraded["Inventory_TechOnly"]["Height"], len(upgraded["Inventory_TechOnly"]["ValidSlotIndices"]), upgraded["Inventory_TechOnly"]["NumSlotsFromTech"]), (10, 6, 60, 0))  # Every donor family, including empty-tech Corvette.
                self.assertEqual(restored, before)  # All non-allowlisted fields must be identical.
                expected = Counter(_base_tech_id(slot["Id"]) for slot in reference["Inventory_TechOnly"]["Slots"])  # Count module types, ignoring procedural seeds.
                actual = Counter(_base_tech_id(slot["Id"]) for slot in upgraded["Inventory_TechOnly"]["Slots"])  # Include preserved existing seed variants.
                self.assertFalse(expected - actual)  # At least every reference occurrence is installed.
                cells = [(s["Index"]["X"], s["Index"]["Y"]) for s in upgraded["Inventory_TechOnly"]["Slots"]]  # Actual planned cells.
                self.assertEqual(len(cells), len(set(cells)))  # No addition may collide with a retained/additional item.
                again, count = upgrade_ship(upgraded, reference)  # Repeating the upgrade must be a no-op.
                self.assertEqual((again, count), (upgraded, 0))  # Idempotence includes statistics and complete item records.
                self.assertEqual(added, len(reference["Inventory_TechOnly"]["Slots"]) if family != "corvette" else len(upgraded["Inventory_TechOnly"]["Slots"]) - len(old_slots))  # Honest count.

    # test_sixty_cells_before_insertion: Smaller grids expand before adding reference items; empty large grids normalize safely.
    def test_sixty_cells_before_insertion(self):
        for capacity in (1, 20, 60, 80):  # Cover growth, unchanged capacity, and safe removal of empty excess cells.
            target = fixture(capacity=capacity)  # Synthetic inventory, no installed items.
            target["Inventory_TechOnly"]["NumSlotsFromTech"] = 12  # New contract explicitly normalizes the reference convention.
            before = copy.deepcopy(target)  # Prove staged changes never alter the input.
            upgraded, added = upgrade_ship(target, load_reference("reference_fighter.json"))  # Must fit all sixty donor items after expansion.
            tech = upgraded["Inventory_TechOnly"]  # Actual planned result.
            self.assertEqual((tech["Width"], tech["Height"], len(tech["ValidSlotIndices"]), tech["NumSlotsFromTech"], added), (10, 6, 60, 0, len(load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"])))  # Capacity and donor occupancy are distinct.
            self.assertEqual(target, before)  # Atomic planning.
            self.assertEqual(upgraded["InventoryLayout"], before["InventoryLayout"])  # Unproven cargo/layout counter is not treated as tech capacity.

    # test_oversized_equipment_and_bonus_refusal: Corvette grid failures preserve equipment while still upgrading stats/class.
    def test_oversized_equipment_and_bonus_refusal(self):
        for bonus in (False, True):  # Both installed records and supercharged cells can prevent safe shrinking.
            target = fixture("corvette")  # Build-preserving branch must never wholesale replace equipment.
            tech = target["Inventory_TechOnly"]  # Synthetic grid only.
            record = tech["SpecialSlots"][0] if bonus else copy.deepcopy(load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"][0])  # Valid record.
            record["Index"] = {"X": 0, "Y": 7}  # Existing eighty-cell grid, outside requested sixty cells.
            if not bonus: tech["Slots"] = [record]  # Retain the outlying equipment record.
            before = copy.deepcopy(target)  # Entire original evidence.
            result, reports = plan_upgrades([target], [0], load_reference)  # Actual partial-success path.
            self.assertEqual(reports[0]["status"], "partial")  # Never claim full rejection or successful tech.
            restored = copy.deepcopy(result[0]["Inventory_TechOnly"])  # Tech statistics alone may change.
            restored["BaseStatValues"] = before["Inventory_TechOnly"]["BaseStatValues"]  # Undo approved stats change.
            self.assertEqual(restored, before["Inventory_TechOnly"])  # Items/layout/supercharged cells fully preserved.
            self.assertEqual(result[0]["Inventory"]["Class"]["InventoryClass"], "S")  # Class still applies.
            self.assertEqual(target, before)  # Input immutable.

    # test_all_explicit_scene_mappings: Cover every base and explicit special exception before generic families.
    def test_all_explicit_scene_mappings(self):
        for scene, family in {**BASE_SCENES, **SPECIAL_SCENES}.items():  # Actual implementation mapping table.
            with self.subTest(scene=scene):  # Verify filename case/separator tolerance without rewriting resources.
                ship = {"Resource": {"Filename": "MODELS/COMMON/SPACECRAFT/" + scene}}  # Synthetic minimal identity.
                self.assertEqual(reference_family(ship), family)  # Match the confirmed donor association.
                ship["Resource"]["Filename"] = ship["Resource"]["Filename"].lower().replace("/", "\\")  # Equivalent spelling.
                self.assertEqual(reference_family(ship), family)  # Do not depend on case or slash direction.

    # test_confirmed_named_samples: Assert independent repository sample associations, including custom/special preservation.
    def test_confirmed_named_samples(self):
        samples = [("Custom Hauler", "DROPSHIPS/DROPSHIP_PROC.SCENE.MBIN", "hauler"), ("Iron Vulture", "DROPSHIPS/DROPSHIP_PROC.SCENE.MBIN", "hauler"), ("Boundary Herald", "FIGHTERS/SPOOKSHIP.SCENE.MBIN", "boundary_herald")]  # Verified init_text.py examples.
        for name, scene, expected in samples:  # Names label the fixture but never choose the donor.
            with self.subTest(ship=name):  # Each confirmed association is tested separately.
                target = fixture(expected)  # Synthetic ownership retains appearance/build identity fields.
                target["Name"] = name  # Use the sample's name as a report label only.
                target["Resource"]["Filename"] = "MODELS/COMMON/SPACECRAFT/" + scene  # Exact independently verified resource.
                original_resource = copy.deepcopy(target["Resource"])  # Preserve complete build/seed/AltId data.
                self.assertEqual(reference_family(target), expected)  # Assert independent expected mapping.
                upgraded, results = plan_upgrades([target], [0], load_reference)  # Exercise actual donor selection.
                self.assertEqual(results[0]["status"], "upgraded")  # Current donor is usable in each synthetic target.
                self.assertEqual(upgraded[0]["Resource"], original_resource)  # Custom and special identity survives.

    # test_unknown_models_never_use_directory_guess: Unknown/future fighter scenes must be rejected.
    def test_unknown_models_never_use_directory_guess(self):
        for scene in ["MODELS/COMMON/SPACECRAFT/FIGHTERS/FUTURE.SCENE.MBIN", "elsewhere/FIGHTER_PROC.SCENE.MBIN", ""]:
            with self.subTest(scene=scene), self.assertRaises(ValueError):  # No fallback to a familiar path substring.
                reference_family({"Resource": {"Filename": scene}})  # Execute the actual scene resolver.

    # test_base_id_and_repeat_counts: Both existing seed variants satisfy reference occurrences of the same module type.
    def test_base_id_and_repeat_counts(self):
        target, reference = fixture("corvette"), load_reference("reference_corvette.json")
        reference["Inventory_TechOnly"]["Slots"] = load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"]  # Synthetic populated Corvette donor.  # Real repeated seed example.
        repeated = [s for s in reference["Inventory_TechOnly"]["Slots"] if s["Id"] == "^UP_SMINI4#36184"]  # Three copies.
        reference["Inventory_TechOnly"]["Slots"] = copy.deepcopy(repeated)  # Restrict only the fixture donor contents.
        exact, different = copy.deepcopy(repeated[0]), copy.deepcopy(repeated[0])  # Preserve two existing item records.
        exact["Index"], different["Index"] = {"X": 7, "Y": 5}, {"X": 8, "Y": 5}  # Occupied non-donor cells.
        different["Id"] = "^UP_SMINI4#00001"  # Same base tag, different generated seed.
        different["DamageFactor"] = 0.7  # Existing state must never be repaired/overwritten by donor data.
        target["Inventory_TechOnly"]["Slots"] = [exact, different]  # Set synthetic retained equipment.
        upgraded, added = upgrade_ship(target, reference)  # Count both retained variants by their shared base technology.
        self.assertEqual(added, 1)  # Two existing copies satisfy two of the reference's three copies.
        self.assertEqual(upgraded["Inventory_TechOnly"]["Slots"][:2], [exact, different])  # Keep extras intact.
        self.assertEqual(Counter(_base_tech_id(s["Id"]) for s in upgraded["Inventory_TechOnly"]["Slots"])["^UP_SMINI4"], 3)  # Three copies total regardless of seeds.
        again, count = upgrade_ship(upgraded, reference)  # Repeated upgrade must retain the chosen subset.
        self.assertEqual((again, count), (upgraded, 0))  # No additional seed variants or dirty change on repeat.

    # test_random_subset_uses_only_reference_records: Random selection fills only the base-type deficit without inventing seeds.
    def test_random_subset_uses_only_reference_records(self):
        target, reference = fixture("corvette"), load_reference("reference_corvette.json")
        reference["Inventory_TechOnly"]["Slots"] = load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"]  # Synthetic populated Corvette donor.  # Actual donor schema, synthetic target.
        template = reference["Inventory_TechOnly"]["Slots"][0]  # Full installed-technology record shape.
        donors = []  # Distinct seeds and donor positions make selected records independently identifiable.
        for index, seed in enumerate((101, 202, 303, 404)):
            record = copy.deepcopy(template)  # Preserve complete donor payload.
            record.update(Id=f"^UP_SMINI4#{seed}", Index={"X": index, "Y": 0})  # Controlled reference-only seed choices.
            donors.append(record)  # Four required copies of the same base type.
        existing = copy.deepcopy(template)  # Existing module must retain its own seed and placement.
        existing.update(Id="^UP_SMINI4#999", Index={"X": 9, "Y": 5}, DamageFactor=0.5)  # Different seed still counts as present.
        target["Inventory_TechOnly"]["Slots"] = [existing]  # Three copies are missing, not four.
        reference["Inventory_TechOnly"]["Slots"] = donors  # Never change the bundled reference.
        before, donor_before = copy.deepcopy(target), copy.deepcopy(reference)  # Preserve input evidence.
        with patch("StarshipUpgrade.random.sample", wraps=__import__("random").sample) as sample:  # Execute real random sampling while observing arguments.
            upgraded, added = upgrade_ship(target, reference)  # Real capacity, deficit and copy code.
            sample.assert_called_once_with(donors, 3)  # Sample only the missing count from the matching reference group.
        self.assertEqual(added, 3)  # Capacity analysis and insertion agree.
        output = upgraded["Inventory_TechOnly"]["Slots"]  # Actual staged output.
        self.assertEqual(output[0], existing)  # Existing seed, fuel/damage and position untouched.
        self.assertEqual(len({slot["Id"] for slot in output[1:]}), 3)  # Sampling distinct reference records without replacement.
        for slot in output[1:]: self.assertIn(slot, donors)  # Complete selected records came from the reference, with no invented seed.
        self.assertEqual((target, reference), (before, donor_before))  # Both inputs remain unchanged.
        again, count = upgrade_ship(upgraded, reference)  # Chosen subset satisfies count regardless of omitted seeds.
        self.assertEqual((again, count), (upgraded, 0))  # Stable repeat/no-op behavior.

    # test_different_seeds_on_full_grid_need_no_additions: Same base counts in a full grid must not cause a false capacity rejection.
    def test_different_seeds_on_full_grid_need_no_additions(self):
        target, reference = fixture(items=60, capacity=60), load_reference("reference_fighter.json")  # Sixty existing items.
        for slot in target["Inventory_TechOnly"]["Slots"]:  # Change only procedural seeds in the synthetic target.
            base = _base_tech_id(slot["Id"])  # Keep module family/class tag exact.
            if base != slot["Id"]: slot["Id"] = base + "#99999"  # Existing stat rolls differ from every reference seed.
        before = copy.deepcopy(target["Inventory_TechOnly"]["Slots"])  # Every original record must survive.
        upgraded, added = upgrade_ship(target, reference)  # Full grid is sufficient because no base-type copies are missing.
        self.assertEqual(added, len(reference["Inventory_TechOnly"]["Slots"]))  # Wholesale replacement restores current reference occupancy.
        self.assertEqual(upgraded["Inventory_TechOnly"]["Slots"], reference["Inventory_TechOnly"]["Slots"])  # Approved wholesale replacement includes seeds.

    # test_base_id_boundaries_and_extras: Strip seed only; retain ordinary IDs, hashed IDs and grade distinctions.
    def test_base_id_boundaries_and_extras(self):
        self.assertEqual(_base_tech_id("^UP_SMINI4#36184"), "^UP_SMINI4")  # Procedural numeric seed.
        for item_id in ("^SHIPMINIGUN", "^ABCDEF#", "^UP_SMINI4#not-a-seed"):
            self.assertEqual(_base_tech_id(item_id), item_id)  # No normalization of ordinary/hashed/unknown syntax.
        template = load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"][0]  # Valid typed record.
        def record(item_id):  # record: Construct independent synthetic technology records.
            value = copy.deepcopy(template); value["Id"] = item_id  # Only identity varies.
            return value  # No file or input mutation.
        donors = [record("^UP_SMINI4#1"), record("^UP_SMINI4#2")]  # Two reference copies.
        existing = [record(f"^UP_SMINI4#{i}") for i in (7, 8, 9, 10)]  # Extra copies remain present and require no additions.
        with patch("StarshipUpgrade.random.sample") as sample:
            self.assertEqual(_missing_items(existing, donors), [])  # Already-satisfied group.
            sample.assert_not_called()  # No random seed replacement for existing modules.
        missing = _missing_items([record("^UP_SMINI3#1")], donors)  # Different grade/base ID must not satisfy this tag.
        self.assertEqual(len(missing), 2)  # Do not collapse distinct base tags or classes.

    # test_occupied_donor_position_uses_free_enabled_cell: Additions must not overwrite existing equipment.
    def test_occupied_donor_position_uses_free_enabled_cell(self):
        target, reference = fixture("corvette"), load_reference("reference_corvette.json")
        reference["Inventory_TechOnly"]["Slots"] = load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"]  # Synthetic populated Corvette donor.  # Prepare one insertion fixture.
        reference["Inventory_TechOnly"]["Slots"] = reference["Inventory_TechOnly"]["Slots"][:1]  # One missing item.
        existing = copy.deepcopy(reference["Inventory_TechOnly"]["Slots"][0])  # Occupy its preferred donor cell.
        existing["Id"] = "^EXISTING_BUILD_PART"  # Existing record does not satisfy the reference technology.
        target["Inventory_TechOnly"]["Slots"] = [existing]  # Do not move or rewrite this equipment.
        upgraded, added = upgrade_ship(target, reference)  # Execute collision-safe insertion.
        self.assertEqual(added, 1)  # Add the missing item once.
        self.assertEqual(upgraded["Inventory_TechOnly"]["Slots"][0], existing)  # Preserve the occupied donor cell.
        self.assertNotEqual(upgraded["Inventory_TechOnly"]["Slots"][1]["Index"], existing["Index"])  # Place elsewhere.

    # test_insufficient_space_refuses_whole_ship: Corvette capacity failures now skip only tech while stats/class commit.
    def test_insufficient_space_refuses_whole_ship(self):
        target, donor = fixture("corvette"), load_reference("reference_corvette.json")  # Confirmed Corvette identities.
        slots = copy.deepcopy(load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"])  # Fill sixty cells.
        for slot in slots: slot["Id"] = "^PRESERVED_EXTRA"  # No donor item satisfied.
        occupied = {(s["Index"]["X"], s["Index"]["Y"]) for s in slots}  # Donor may now leave intentional empty cells.
        for y in range(6):  # Keep this capacity-failure fixture explicitly full independent of current donor occupancy.
            for x in range(10):  # Complete all sixty retained cells.
                if (x, y) not in occupied:  # Fill only genuinely unoccupied fixture coordinates.
                    item = copy.deepcopy(slots[0]); item["Index"] = {"X": x, "Y": y}  # Synthetic retained record.
                    slots.append(item)  # Do not alter any actual reference.
        target["Inventory_TechOnly"]["Slots"] = slots  # Full retained inventory.
        donor["Inventory_TechOnly"]["Slots"] = [copy.deepcopy(slots[0])]  # One missing reference record.
        donor["Inventory_TechOnly"]["Slots"][0]["Id"] = "^FUTURE_CORVETTE_TECH"  # Distinct required tag.
        before, donor_before = copy.deepcopy(target), copy.deepcopy(donor)  # Input preservation evidence.
        ships, results = plan_upgrades([target], [0], lambda filename: donor)  # Exercise actual capacity failure.
        self.assertEqual(results[0]["status"], "partial")  # Independent stats upgrade succeeds.
        self.assertIn("need 1, have 0", results[0]["tech_reason"])  # Honest space diagnostic.
        restored = copy.deepcopy(ships[0]["Inventory_TechOnly"])  # Verify equipment/capacity untouched.
        restored["BaseStatValues"] = before["Inventory_TechOnly"]["BaseStatValues"]  # Undo authorized stats only.
        self.assertEqual(restored, before["Inventory_TechOnly"])  # No partial capacity/item publication.
        self.assertEqual(ships[0]["Inventory"]["BaseStatValues"], donor["Inventory"]["BaseStatValues"])  # Stats commit.
        self.assertEqual(ships[0]["Inventory_Cargo"]["Class"], donor["Inventory_Cargo"]["Class"])  # Cargo class commit.
        self.assertEqual((target, donor), (before, donor_before))  # Both inputs immutable.

    # test_corvette_empty_and_future_populated: Current scanner donor adds once; empty and future donors preserve existing builds.
    def test_corvette_empty_and_future_populated(self):
        target, reference = fixture("corvette"), load_reference("reference_corvette.json")  # Current scanner-only donor.
        existing = copy.deepcopy(load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"][0])  # Synthetic build record.
        existing["Id"] = "^CORVETTE_BUILD_PART"  # Distinct retained record.
        target["Inventory_TechOnly"]["Slots"] = [existing]  # Preserve the original build item.
        upgraded, added = upgrade_ship(target, reference)  # Scanner must be inserted without deleting build data.
        self.assertEqual(added, 1)  # One scanner is missing.
        self.assertEqual(upgraded["Inventory_TechOnly"]["Slots"][0], existing)  # Build record unchanged.
        self.assertEqual([s["Id"] for s in upgraded["Inventory_TechOnly"]["Slots"]], ["^CORVETTE_BUILD_PART", "^DUMMY_SCAN"])  # Exactly one scanner added.
        again, count = upgrade_ship(upgraded, reference)  # Existing scanner satisfies the reference.
        self.assertEqual((again, count), (upgraded, 0))  # Repeat is a no-op, not another scanner.
        empty = copy.deepcopy(reference); empty["Inventory_TechOnly"]["Slots"] = []  # Preserve empty-donor regression as a fixture.
        empty_result, count = upgrade_ship(target, empty)  # Empty donor still upgrades stats/classes/capacity.
        self.assertEqual((empty_result["Inventory_TechOnly"]["Slots"], count), ([existing], 0))  # No equipment erased.
        populated = copy.deepcopy(reference)  # Future reference experiment stays in memory.
        populated["Inventory_TechOnly"]["Slots"] = [copy.deepcopy(existing)]  # Distinct synthetic future equipment.
        populated["Inventory_TechOnly"]["Slots"][0]["Id"] = "^FUTURE_CORVETTE_TECH"  # Missing technology.
        future, added = upgrade_ship(upgraded, populated)  # Existing scanner and build item remain.
        self.assertEqual(added, 1)  # One new type inserted.
        self.assertEqual(future["Inventory_TechOnly"]["Slots"][:2], upgraded["Inventory_TechOnly"]["Slots"])  # Existing records fully intact.
        self.assertEqual([s["Id"] for s in load_reference("reference_corvette.json")["Inventory_TechOnly"]["Slots"]], ["^DUMMY_SCAN"])  # Actual donor unchanged by tests.

    # test_invalid_donors_refuse_without_mutation: Cover malformed stats/classes/slots and incomplete inventories.
    def test_invalid_donors_refuse_without_mutation(self):
        target = fixture()  # Synthetic target is reused only because upgrade planning must not mutate it.
        bad_donors = []  # Build invalid donor variants without changing any bundled resource.
        for value in [None, True, "100", float("nan"), float("inf"), 10 ** 400]:  # Invalid numeric values.
            donor = load_reference("reference_fighter.json")  # Independent donor per scenario.
            donor["Inventory"]["BaseStatValues"][0]["Value"] = value  # Corrupt one approved stat field.
            bad_donors.append(donor)  # Exercise safe per-ship validation.
        for key in ["Inventory", "Inventory_Cargo", "Inventory_TechOnly"]:  # Missing ownership nodes.
            donor = load_reference("reference_fighter.json")  # Start with a complete current schema.
            del donor[key]  # Simulate a broken reference.
            bad_donors.append(donor)  # No implicit empty-node replacement is permitted.
        for index, donor in enumerate(bad_donors):  # Report which malformed case unexpectedly passed.
            with self.subTest(case=index), self.assertRaises(ValueError):
                upgrade_ship(target, donor)  # Refuse safely before any candidate publication.
        self.assertEqual(target, fixture())  # Every invalid case leaves target state unchanged.

    # test_invalid_layouts_refuse: Bad reference equipment skips tech but does not prevent valid stat/class upgrades.
    def test_invalid_layouts_refuse(self):
        target, donor = fixture(items=1), load_reference("reference_fighter.json")  # Ordinary replacement branch.
        donor["Inventory_TechOnly"]["Slots"][1]["Index"] = copy.deepcopy(donor["Inventory_TechOnly"]["Slots"][0]["Index"])  # Broken donor overlap.
        before = copy.deepcopy(target)  # Prove original items survive a failed replacement.
        candidate, reports = plan_upgrades([target], [0], lambda filename: donor)  # No wrong-family/stat failure.
        self.assertEqual(reports[0]["status"], "partial")  # Invalid reference equipment is not full success.
        self.assertEqual(candidate[0]["Inventory_TechOnly"]["Slots"], before["Inventory_TechOnly"]["Slots"])  # No equipment loss.
        self.assertEqual(candidate[0]["Inventory"]["Class"]["InventoryClass"], "S")  # Valid class applies.
        self.assertEqual(target, before)  # Caller immutable.

    # test_mixed_batch_and_unselected_preservation: A refusal does not prevent another selected ship from upgrading.
    def test_mixed_batch_and_unselected_preservation(self):
        ships = [overflow_fixture(), fixture("corvette"), fixture("hauler")]  # First rejects, second succeeds, third unselected.
        before = copy.deepcopy(ships)  # Whole-list original must remain unchanged during planning.
        candidate, results = plan_upgrades(ships, [0, 1], load_reference)  # Real batch planner.
        self.assertEqual([r["status"] for r in results], ["upgraded", "upgraded"])  # Ordinary replacement no longer fails for preserved extras.
        self.assertEqual(candidate[0]["Inventory_TechOnly"]["Slots"], load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"])  # Wholesale replacement removes extras.
        self.assertEqual(candidate[2], before[2])  # Unselected ship is untouched.
        self.assertEqual(ships, before)  # Planner does not mutate caller inputs.

    # test_missing_and_wrong_family_reference: Missing resource files and incorrect donors become per-ship rejections.
    def test_missing_and_wrong_family_reference(self):
        ships = [fixture()]  # One supported selected target.
        def missing(filename):  # missing: Simulate an actual missing reference file exception.
            raise FileNotFoundError("Reference file unavailable.")  # No fabricated successful read.
        for loader in [missing, lambda filename: load_reference("reference_living.json")]:  # Missing/wrong-family donor.
            candidate, results = plan_upgrades(ships, [0], loader)  # Actual per-ship failure reporting.
            self.assertEqual(candidate, ships)  # Never apply another family's stats or equipment.
            self.assertEqual(results[0]["status"], "rejected")  # Both failure types are reported.
            self.assertTrue(results[0]["reason"])  # Bottom notes have a useful explanation.

    # test_controller_main_and_expedition_preservation: The same handler edits only shared context ownership.
    def test_controller_main_and_expedition_preservation(self):
        env = controller_functions()  # Real handler bodies, no GUI import.
        for context_key in ["BaseContext", "ExpeditionContext"]:  # Context identity is selected before upgrading.
            with self.subTest(context=context_key):  # Prove no hard-coded BaseContext path.
                context = {"GameMode": "fixture", "SpawnStateData": {"position": [1, 2, 3]}, "PlayerStateData": {"ShipOwnership": [fixture("corvette")], "CharacterCustomisationData": [{"parts": [1]}], "PersistentPlayerBases": [{"interior": "keep"}], "PrimaryShip": 0, "ShipUsesLegacyColours": [True], "UnknownSharedStorage": [5]}}  # Synthetic whole context.
                full_tree = {context_key: copy.deepcopy(context), "OtherRoot": {"keep": True}}  # Retained full codec tree.
                original_tree = copy.deepcopy(full_tree)  # Upgrades must not copy back or save automatically.
                window = SimpleNamespace(model=FakeModel(copy.deepcopy(context)), ini_file_manager=SimpleNamespace(get_starship_upgrade_reference_path=lambda filename: ROOT / "starship_upgrade_references" / filename))  # Real bundle.
                results = env["_upgrade_selected"](window, copy.deepcopy(context), [0])  # Real memory-only handler.
                self.assertEqual(results[0]["status"], "upgraded")  # Successful stats-only Corvette path.
                self.assertEqual(window.model.commits, 1)  # One batch commit, not per-field/ship publication.
                updated = copy.deepcopy(window.model.data); updated["PlayerStateData"]["ShipOwnership"] = context["PlayerStateData"]["ShipOwnership"]  # Strip ownership edits.
                self.assertEqual(updated, context)  # Appearance, build bases, storage, flags and spawn remain identical.
                self.assertEqual(full_tree, original_tree)  # No inactive/full-tree write or automatic save.
                self.assertTrue(window.model.dirty)  # Successful changes use normal model-change semantics.

    # test_controller_noop_and_all_rejected_do_not_commit: No model publication or dirty transition for unchanged results.
    def test_controller_noop_and_all_rejected_do_not_commit(self):
        env = controller_functions()  # Execute actual commit/no-op branch.
        donor = load_reference("reference_corvette.json")  # The bundled donor still has an eighty-cell layout.
        complete, unused = upgrade_ship(donor, donor)  # Normalize to the new sixty-cell contract before testing a no-op.
        unknown = fixture(); unknown["Resource"]["Filename"] = "MODELS/COMMON/SPACECRAFT/FIGHTERS/FUTURE.SCENE.MBIN"  # True full rejection.
        for ship in [unknown, complete]:  # Refusal and already-complete cases.
            context = {"PlayerStateData": {"ShipOwnership": [ship]}}  # Selected shared context fixture.
            window = SimpleNamespace(model=FakeModel(copy.deepcopy(context)), ini_file_manager=SimpleNamespace(get_starship_upgrade_reference_path=lambda filename: ROOT / "starship_upgrade_references" / filename))  # Actual bundle loader.
            env["_upgrade_selected"](window, context, [0])  # No-op/refusal reports must still be available.
            self.assertEqual(window.model.commits, 0)  # Do not trigger false model/dirty signals.
            self.assertFalse(window.model.dirty)  # Previous consistent fixture state is preserved.
            self.assertEqual(window.model.data, context)  # No mutation at all.

    # test_controller_stale_selection_and_unsynced_refusal: Do not overwrite newly loaded data or raw text edits.
    def test_controller_stale_selection_and_unsynced_refusal(self):
        env = controller_functions()  # Real preflight and stale snapshot logic.
        context = {"PlayerStateData": {"ShipOwnership": [fixture("corvette")]}}  # Old selection snapshot.
        newer: dict[str, Any] = copy.deepcopy(context); newer["NewerEdit"] = True  # Simulate modal-event data changes.
        window = SimpleNamespace(model=FakeModel(newer), _nms_tabs=[SimpleNamespace(tree_synced=False)], ini_file_manager=SimpleNamespace(get_starship_upgrade_reference_path=lambda filename: ROOT / "starship_upgrade_references" / filename))  # Pending edit.
        with self.assertRaisesRegex(ValueError, "Sync from Text Window"):
            env["_checked_context"](window)  # Preflight must not auto-sync or discard text.
        with self.assertRaisesRegex(ValueError, "changed during selection"):
            env["_upgrade_selected"](window, context, [0])  # No stale ownership replacement.
        self.assertEqual(window.model.data, newer)  # Preserve the newer whole-context edit.
        self.assertEqual(window.model.commits, 0)  # No candidate publication.

    # test_results_red_names_and_conditional_notes: Actual HTML formatter escapes names/reasons and omits empty notes.
    def test_results_red_names_and_conditional_notes(self):
        env = controller_functions()  # Actual result formatter, not a reconstructed expected implementation.
        success = {"index": 0, "name": "Alpha <tag>", "status": "upgraded", "reason": ""}  # HTML-sensitive ship name.
        rejected = {"index": 1, "name": "Beta & Co", "status": "rejected", "reason": "Need <2> cells."}  # Brief reason.
        text = env["results_html"]([success, rejected])  # Mixed outcomes.
        self.assertIn('style="color: red;">Beta &amp; Co</span>', text)  # Only rejected name is red.
        self.assertIn("Alpha &lt;tag&gt;", text)  # Literal name survives safely.
        self.assertIn("Need &lt;2&gt; cells.", text)  # Reason is safe plain text.
        self.assertGreater(text.index("Upgrade notes:"), text.index("Selected starships:"))  # Notes below list.
        self.assertNotIn("Upgrade notes:", env["results_html"]([success]))  # No notes heading on success-only run.
        self.assertNotIn("color: red", env["results_html"]([success]))  # Successful names remain normal.

    # test_cancel_empty_selection_and_reentrancy: Execute real wrapper branches without opening any dialog.
    def test_cancel_empty_selection_and_reentrancy(self):
        env = controller_functions()  # Actual run_starship_upgrade function.
        window = SimpleNamespace(model=FakeModel({"PlayerStateData": {"ShipOwnership": [fixture("corvette")]}}), _nms_tabs=[], _nms_loading=False)  # Valid context.
        tab = SimpleNamespace(main_window=window)  # Either historical entry point supplies this interface.
        env["_selected_indices"] = lambda ships: []  # Synthetic Cancel/empty picker return.
        env["run_starship_upgrade"](tab)  # No result dialog should be needed.
        self.assertEqual(window.model.commits, 0)  # Cancel never publishes data.
        self.assertFalse(window._starship_upgrade_running)  # Guard restores after early return.
        window._nms_loading = True  # Simulate another active load/save transaction.
        env["_checked_context"] = lambda host: self.fail("Reentrant preflight was executed")  # Must not reach preflight.
        env["run_starship_upgrade"](tab)  # Ignore request during load/save.
        self.assertEqual(window.model.commits, 0)  # No reentrant mutation.

    # test_upgrade_progress_handoff_and_failure_cleanup: Execute the real submitted-upgrade wrapper with synthetic UI boundaries.
    def test_upgrade_progress_handoff_and_failure_cleanup(self):
        for fail in (False, True):  # Successful result handoff and planning-failure cleanup.
            env, events = controller_functions(), []  # Actual wrapper functions, no Qt imports.
            context = {"PlayerStateData": {"ShipOwnership": [fixture("corvette")]}}  # Synthetic editable context.
            window = SimpleNamespace(model=FakeModel(context), _nms_tabs=[], _nms_loading=False, enabled=True)  # No save target.
            window.isEnabled = lambda: window.enabled  # Preserve main-window interaction state.
            window.setEnabled = lambda value: setattr(window, "enabled", value)  # Track disable/restore.
            window.repaint = lambda: events.append("refresh")  # Final editor paint boundary.
            owner = self  # Callbacks assert lifetime ordering.

            class Progress:  # Synthetic dialog interface only.
                def __init__(self, text, parent):
                    owner.assertEqual(text, "Upgrading starships, please wait…")  # Exact user-facing progress.
                    self.visible = False  # Construction alone is not progress display.
                def setEnabled(self, value): pass  # No GUI parent inheritance.
                def show(self): self.visible = True; events.append("show")  # Starts after submitted selection.
                def accept(self): self.visible = False; events.append("dismiss")  # Transaction handoff.
                def deleteLater(self): events.append("delete")  # Deferred QObject release.

            class Results:  # Report construction and presentation are separate observable boundaries.
                def __init__(self, results, parent): events.append("report-ready")  # Prepare while progress remains visible.
                def exec_(self):
                    owner.assertTrue(window.enabled)  # Interactive report must not inherit disabled main-window state.
                    events.append("report-shown")  # Existing results appear immediately after progress cleanup.

            def upgrade(*args):  # Synthetic planning service; actual wrapper owns lifetime.
                owner.assertFalse(window.enabled)  # Main editor disabled throughout upgrading.
                owner.assertIn("show", events)  # Never start work before progress is shown.
                events.append("upgrade")  # Reference/planner/model-publication boundary.
                if fail: raise ValueError("synthetic planning failure")  # Exercise exception cleanup.
                return []  # Report contents are covered independently by real formatter tests.

            env.update({"_selected_indices": lambda ships: [0], "_upgrade_selected": upgrade, "NmsLoadingDialog": Progress, "StarshipUpgradeResultsDialog": Results, "QApplication": SimpleNamespace(processEvents=lambda flags: events.append("events")), "QEventLoop": SimpleNamespace(ExcludeUserInputEvents="exclude-input"), "QMessageBox": SimpleNamespace(warning=lambda *args: events.append("warning"))})  # No actual GUI or files.
            env["run_starship_upgrade"](SimpleNamespace(main_window=window))  # Execute actual submitted-upgrade wrapper.
            self.assertTrue(window.enabled)  # Restore editor on every path.
            self.assertFalse(window._starship_upgrade_running)  # No stranded guard.
            self.assertLess(events.index("show"), events.index("upgrade"))  # Submit progress precedes work.
            if fail:
                self.assertLess(events.index("dismiss"), events.index("warning"))  # Close modal progress before showing failure.
                self.assertNotIn("report-shown", events)  # No false successful result handoff.
            else:
                self.assertLess(events.index("refresh"), events.index("report-ready"))  # Finish editor update first.
                self.assertLess(events.index("report-ready"), events.index("dismiss"))  # No early progress dismissal.
                self.assertLess(events.index("dismiss"), events.index("report-shown"))  # Direct handoff to existing results.

    # test_wholesale_replacement_removes_extras: Ordinary ships lose original extras and receive exact donor records/seeds/positions.
    def test_wholesale_replacement_removes_extras(self):
        target, donor = overflow_fixture(), load_reference("reference_fighter.json")  # Previous extra-item capacity refusal.
        before = copy.deepcopy(target)  # Preserve entire target input.
        target["Inventory_TechOnly"]["Slots"][0]["Index"] = {"X": 0, "Y": 7}  # Original position will be deliberately replaced.
        target["Inventory_TechOnly"]["Height"] = 8  # Original equipment need not fit the new grid because replacement is authorized.
        candidate, reports = plan_upgrades([target], [0], load_reference)  # Real family-specific branch.
        self.assertEqual(reports[0]["status"], "upgraded")  # No capacity union with removed extras.
        self.assertEqual(candidate[0]["Inventory_TechOnly"]["Slots"], donor["Inventory_TechOnly"]["Slots"])  # Exact wholesale payload.
        self.assertEqual(candidate[0]["Resource"], before["Resource"])  # Ship identity/custom resource unchanged.
        self.assertEqual(candidate[0]["Inventory_TechOnly"]["SpecialSlots"], before["Inventory_TechOnly"]["SpecialSlots"])  # Supercharged layout preserved.
        candidate[0]["Inventory_TechOnly"]["Slots"][0]["Id"] = "^TEST_INDEPENDENCE"  # Modify returned fixture only.
        self.assertEqual(load_reference("reference_fighter.json"), donor)  # Donor is never shared or mutated.

    # test_partial_controller_commit_and_report: Stats-only partial success commits normally and receives explicit escaped notes.
    def test_partial_controller_commit_and_report(self):
        target = fixture("corvette")  # Existing oversized build record prevents safe sixty-cell normalization.
        record = copy.deepcopy(load_reference("reference_fighter.json")["Inventory_TechOnly"]["Slots"][0])  # Synthetic equipment.
        record["Index"] = {"X": 0, "Y": 7}  # Preserve outlying equipment rather than remove it.
        target["Inventory_TechOnly"]["Slots"] = [record]  # Only the tech step fails.
        context = {"PlayerStateData": {"ShipOwnership": [target], "PersistentPlayerBases": [{"keep": True}]}}  # Build context.
        window = SimpleNamespace(model=FakeModel(copy.deepcopy(context)), ini_file_manager=SimpleNamespace(get_starship_upgrade_reference_path=lambda filename: ROOT / "starship_upgrade_references" / filename))  # Isolated model.
        env = controller_functions()  # Actual controller functions without a GUI.
        reports = env["_upgrade_selected"](window, copy.deepcopy(context), [0])  # Partial success must publish once.
        self.assertEqual((window.model.commits, window.model.dirty), (1, True))  # Real stat/class edit marks unsaved.
        self.assertEqual(window.model.data["PlayerStateData"]["PersistentPlayerBases"], context["PlayerStateData"]["PersistentPlayerBases"])  # Build preservation.
        self.assertEqual(window.model.data["PlayerStateData"]["ShipOwnership"][0]["Inventory_TechOnly"]["Slots"], [record])  # Equipment intact.
        reports[0]["tech_reason"] += " <tag>"  # Exercise HTML escaping of partial notes.
        html = env["results_html"](reports)  # Actual formatter.
        self.assertIn("Stats/class applied; tech skipped", html)  # No misleading whole rejection.
        self.assertIn("&lt;tag&gt;", html)  # Reason cannot inject markup.
        self.assertNotIn("color: red", html)  # Partial success is distinct from a wholly rejected ship.

    # test_atlantid_only_references: Every populated conventional drive group contains only one Atlantid drive.
    def test_atlantid_only_references(self):
        drives = {"^HDRIVEBOOST1", "^HDRIVEBOOST2", "^HDRIVEBOOST3", "^HDRIVEBOOST4"}  # Exact conventional drive tags.
        for path in (ROOT / "starship_upgrade_references").glob("reference_*.json"):  # Review every integrated reference.
            donor = load_reference(path.name)  # Actual current JSON payload.
            present = [s["Id"] for s in donor["Inventory_TechOnly"]["Slots"] if s["Id"] in drives]  # No guessing compatibility from family.
            if present: self.assertEqual(present, ["^HDRIVEBOOST4"], path.name)  # One highest drive, no lower duplicates.
            if path.name in ("reference_living.json", "reference_corvette.json"): self.assertEqual(present, [])  # Neither previously had conventional drives.

    # test_source_and_frozen_bundle_loader: Execute actual resolver without IniFileManager initialization/writes.
    def test_source_and_frozen_bundle_loader(self):
        tree = ast.parse((ROOT / "IniFileManager.py").read_text(encoding="utf-8"))  # Actual resolver implementation.
        method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "get_starship_upgrade_reference_path")  # New method only.
        env = {"os": os, "sys": sys, "__file__": str(ROOT / "IniFileManager.py")}  # Resolve normal source root.
        exec(compile(ast.Module(body=[method], type_ignores=[]), "loader-fixture", "exec"), env)  # No preferences construction.
        resolver = env["get_starship_upgrade_reference_path"]  # Use real function behavior.
        self.assertEqual(Path(resolver(None, "reference_corvette.json")), ROOT / "starship_upgrade_references" / "reference_corvette.json")  # Current bundle.
        previous = getattr(sys, "_MEIPASS", None)  # Restore any prior frozen marker after fixture.
        try:  # Simulate PyInstaller root without installing/building or copying anything.
            setattr(sys, "_MEIPASS", str(ROOT / "fixture-frozen-root"))  # Synthetic path only.
            self.assertEqual(Path(resolver(None, "reference_fighter.json")), ROOT / "fixture-frozen-root" / "starship_upgrade_references" / "reference_fighter.json")  # Frozen resource path.
        finally:  # Keep test process environment unchanged after the fixture.
            if previous is None: delattr(sys, "_MEIPASS")  # Remove only the fixture-added marker.
            else: setattr(sys, "_MEIPASS", previous)  # Restore existing marker.
        with self.assertRaises(ValueError):  # Do not accept a path outside the reference bundle.
            resolver(None, "../reference_fighter.json")  # Path traversal must fail.

    # test_both_entry_points_delegate_and_python312_syntax: No remaining wholesale overwrite in either named method.
    def test_both_entry_points_delegate_and_python312_syntax(self):
        for filename in ["SecondTabContent.py", "ForthTabContent.py"]:  # Actual application integration points.
            tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))  # Read only project source.
            method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "upgrade_starships")  # Named entry point.
            self.assertEqual(len(method.body), 1)  # No independent old wholesale-copy logic may remain.
            statement = method.body[0]  # Narrow the actual AST structure before inspecting the call.
            assert isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and isinstance(statement.value.func, ast.Name)  # Entry point must be one function call.
            self.assertEqual(statement.value.func.id, "run_starship_upgrade")  # Same shared safe behavior.
        for filename in ["StarshipUpgrade.py", "StarshipUpgradeController.py", "SecondTabContent.py", "ForthTabContent.py", "IniFileManager.py", "WhichStarshipsToUpgradeDialog.py", "test_starship_upgrade.py"]:
            text = (ROOT / filename).read_text(encoding="utf-8")  # Inspect actual source without imports.
            ast.parse(text, feature_version=(3, 12))  # Gaming PC's Python syntax compatibility.
            payload = (ROOT / filename).read_bytes()  # Verify preserved Windows line endings.
            self.assertNotIn(bytes([10]), payload.replace(bytes([13, 10]), b""))  # No mixed/bare LF code lines.


if __name__ == "__main__":  # Run only explicit isolated fixture verification.
    unittest.main(verbosity=2)  # Real PASS/failure counts come from actual execution.
