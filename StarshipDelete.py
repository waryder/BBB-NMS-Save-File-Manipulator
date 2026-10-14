# File: StarshipDelete.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\StarshipDelete.py
# Purpose: Plan fixed-slot ship deletions without changing input data or writing game saves.
import copy  # Isolate every deleted slot and preserve the complete original context.
import json  # Load the two approved game-observed empty ownership templates.
from pathlib import Path  # Resolve bundled resources relative to this module in source/frozen builds.

LAST_SHIP_NOTICE = "NMS does not allow that last ship to be deleted from inventory; aborting"  # Bill's exact OK-only notice.
CORVETTE_SCENE = "MODELS/COMMON/SPACECRAFT/BIGGS/BIGGS.SCENE.MBIN"  # Game resource identity, never a display-name guess.


class LastShipDeletionError(ValueError):  # Separate policy refusal from malformed-data failures.
    pass  # The UI turns this exception into the exact informational notice.


# customisation_index: Map ownership positions to the experimentally verified appearance positions.
def customisation_index(index):
    return index + 3 if index < 6 else index + 11  # Never shift nonship customisation entries.


# _occupied: Validate record identity and use only Resource.Filename to distinguish occupied slots.
def _occupied(ship):
    if not isinstance(ship, dict) or not isinstance(ship.get("Resource"), dict):  # Invalid records are not empty slots.
        raise ValueError("Malformed starship ownership/resource record; nothing was deleted.")  # Fail closed.
    filename = ship["Resource"].get("Filename", "")  # Absent filenames are valid empty identities.
    if not isinstance(filename, str):  # Do not coerce null, numbers or booleans into occupancy.
        raise ValueError("Malformed starship resource filename; nothing was deleted.")  # Retain the original data.
    return bool(filename)  # Names and seeds may remain populated in empty game-produced records.


# load_delete_templates: Read approved empty records packaged with the app, never from a live save.
def load_delete_templates():
    path = Path(__file__).resolve().with_name("starship_delete_templates.json")  # PyInstaller sets __file__ inside its bundle.
    with path.open("r", encoding="utf-8") as handle:  # Read only this application resource.
        templates = json.load(handle)  # Corruption or a missing resource refuses the operation.
    for key in ("ordinary", "corvette"):  # Validate both complete game-observed ownership donors.
        if _occupied(templates[key]):  # A populated donor must never become an allegedly empty slot.
            raise ValueError("The empty-starship template is occupied; nothing was deleted.")  # No fallback synthesis.
        for inventory in ("Inventory", "Inventory_Cargo", "Inventory_TechOnly"):  # Require complete empty inventory shapes.
            if not isinstance(templates[key].get(inventory), dict) or templates[key][inventory].get("Slots") != []:  # Empty items only.
                raise ValueError("Malformed empty-starship inventory template; nothing was deleted.")  # Fail closed.
    return templates  # Each assignment deep-copies the selected donor.


# _player_and_targets: Validate the fixed twelve-slot roster and combined deletion request before planning.
def _player_and_targets(context, indices):
    player = context.get("PlayerStateData") if isinstance(context, dict) else None  # Work on the active editable branch only.
    if not isinstance(player, dict):  # Establish a real source dictionary before reading ownership.
        raise ValueError("No valid player-state context is loaded.")  # Never construct a missing branch.
    ships = player.get("ShipOwnership")  # Do not construct missing source structures.
    if not isinstance(ships, list) or len(ships) != 12:  # Fixed-slot mapping is established for twelve ownership entries.
        raise ValueError("A valid twelve-slot starship ownership list is required.")  # Refuse unsupported shapes.
    if not isinstance(indices, (list, tuple)) or any(type(i) is not int or not 0 <= i < 12 for i in indices):  # Reject bool/index coercion.
        raise ValueError("Invalid starship-slot selection.")  # No partial application of a mixed request.
    occupied = {i for i, ship in enumerate(ships) if _occupied(ship)}  # Validate even unselected records before counting.
    targets = sorted(set(indices) & occupied)  # Selected empty positions and duplicate descendants are harmless no-ops.
    if targets and not occupied.difference(targets):  # Protect against deleting one last ship OR all remaining ships at once.
        raise LastShipDeletionError(LAST_SHIP_NOTICE)  # The exact notice is independent of missing optional linked data.
    return player, ships, targets, occupied.difference(targets)  # Remaining indices are stable, not compacted.


# _linked_data: Require reliable parallel structures and an integer primary-ship reference.
def _linked_data(player, remaining):
    appearances, flags = player.get("CharacterCustomisationData"), player.get("ShipUsesLegacyColours")  # Parallel ship state.
    if not isinstance(appearances, list) or len(appearances) < 23:  # Indices 3–8 and 17–22 must exist.
        raise ValueError("The mapped ship appearance entries are missing.")  # Do not fabricate associated data.
    if not isinstance(flags, list) or len(flags) != 12 or any(type(flag) is not bool for flag in flags):  # Preserve flag shape.
        raise ValueError("The twelve legacy-colour flags are malformed.")  # Reject before constructing candidates.
    primary = player.get("PrimaryShip")  # This reference must continue to identify a real occupied ship.
    if type(primary) is not int or not 0 <= primary < 12:  # Do not silently repair unrelated invalid source state.
        raise ValueError("The selected-ship index is malformed.")  # Retain all original data.
    bases = player.get("PersistentPlayerBases")  # Contains unrelated ground/freighter bases as well as Corvette builds.
    if not isinstance(bases, list) or any(not isinstance(base, dict) for base in bases):  # Require a safe removable list.
        raise ValueError("The persistent player-base list is malformed.")  # Never replace an unknown shape with an empty list.
    return appearances, flags, bases, primary  # All mutation occurs only in a later independent context copy.


# _ship_kind: Identify Corvettes by resource and custom ships by verified separate part descriptors.
def _ship_kind(ship, appearance):
    if not isinstance(appearance, dict) or not isinstance(appearance.get("CustomData"), dict):  # Guard descriptor lookup.
        raise ValueError("A selected ship's mapped appearance is malformed.")  # Retain ownership and linked structures.
    descriptors = appearance["CustomData"].get("DescriptorGroups")  # Custom-built types, including tested Iron Vulture.
    if not isinstance(descriptors, list):  # An unknown custom-data shape is not proof of an ordinary ship.
        raise ValueError("A selected ship's part descriptors are malformed.")  # Refuse an incomplete cleanup.
    filename = ship["Resource"]["Filename"].replace("\\", "/").upper()  # Match the canonical scene independent of slash/case.
    if filename == CORVETTE_SCENE:  # Corvette build records have their own unique linkage.
        return "corvette"  # Their own observed empty ownership donor differs from the Hauler donor.
    return "custom" if descriptors else "ordinary"  # Ordinary/special noncustom variants share the approved common template.


# _corvette_base_positions: Find whole uniquely linked Corvette records using header UserData only.
def _corvette_base_positions(bases, indices):
    positions = set()  # Deleting these entries must not touch any other player base.
    for index in indices:  # Validate every target before constructing a changed context.
        matches = [position for position, base in enumerate(bases)
                   if isinstance(base.get("BaseType"), dict) and base["BaseType"].get("PersistentBaseTypes") == "PlayerShipBase"
                   and type(base.get("UserData")) is int and base["UserData"] == index]  # Never inspect packed object UserData.
        if len(matches) != 1 or not isinstance(bases[matches[0]].get("Objects"), list):  # Missing/ambiguous builds are unsafe.
            raise ValueError(f"Corvette slot {index + 1} does not have one uniquely linked build; nothing was deleted.")  # Atomic refusal.
        positions.add(matches[0])  # Retain list positions separately from ownership indices.
    return positions  # Filtering later preserves the order and full contents of all unrelated bases.


class OrdinaryShipDeletion:  # Own the common deletion rule for ordinary ships and noncustom special variants.
    ownership_template = "ordinary"  # All non-Corvette types share Bill's approved complete empty Hauler donor.

    # __init__: Retain the immutable donor bundle for this one ship's staged cleanup.
    def __init__(self, templates):
        self.templates = templates  # Every assignment below still deep-copies its donor.

    # apply: Replace only ownership and its legacy-colour flag for the ordinary deletion rule.
    def apply(self, player, index):
        donor = self.templates[self.ownership_template]  # Subclasses may choose a distinct complete ownership donor.
        if _occupied(donor):  # An invalid donor cannot turn a populated record into an allegedly empty slot.
            raise ValueError("The empty ownership template is occupied.")  # The original context remains untouched.
        player["ShipOwnership"][index] = copy.deepcopy(donor)  # Never compact ownership or retain removed capacities/identity.
        player["ShipUsesLegacyColours"][index] = False  # Reset only this fixed slot's parallel flag.

    # linked_base_positions: Ordinary/custom ships do not own a Corvette build to remove.
    def linked_base_positions(self, bases, index):
        return set()  # Preserve unrelated base records, including matching integers on nonship base types.


class CustomShipDeletion(OrdinaryShipDeletion):  # Add mapped appearance cleanup for every part-defined custom build, including Iron Vulture.
    # apply: Apply common ownership cleanup, then reset this ship's complete fixed-position appearance entry.
    def apply(self, player, index):
        super().apply(player, index)  # Share the approved donor/flag behavior rather than duplicate it per family.
        appearance_index = customisation_index(index)  # Respect the split 0–5 versus 6–11 mapping.
        player["CharacterCustomisationData"][appearance_index] = copy.deepcopy(self.templates["appearance"])  # Preserve nonship entries.


class CorvetteShipDeletion(CustomShipDeletion):  # Isolate Corvette-specific ownership and construction cleanup from other types.
    ownership_template = "corvette"  # The observed vacant Corvette record differs from the common empty Hauler donor.

    # linked_base_positions: Require the Corvette's whole uniquely linked build before any candidate mutation.
    def linked_base_positions(self, bases, index):
        return _corvette_base_positions(bases, [index])  # Link by header UserData, never by packed object UserData.


DELETION_HANDLERS = {"ordinary": OrdinaryShipDeletion, "custom": CustomShipDeletion, "corvette": CorvetteShipDeletion}  # One explicit strategy per cleanup category.


class StarshipDeletionPlan:  # Own validation, complete staged bundles and references for one combined deletion request.
    # __init__: Retain the original context and validate the combined last-ship constraint before linked-data work.
    def __init__(self, context, indices, templates=None):
        self.context, self.templates = context, templates  # Caller-owned data remains read-only throughout planning.
        self.player, self.ships, self.targets, self.remaining = _player_and_targets(context, indices)  # Fixed-slot identities.

    # _validate_linked_data: Establish reliable appearances, bases and selection before choosing any ship handler.
    def _validate_linked_data(self):
        self.appearances, _, self.bases, self.primary = _linked_data(self.player, self.remaining)  # Preserve existing schema checks.
        if self.primary not in self.remaining and self.primary not in self.targets:  # An already-orphaned selection is unrelated invalid state.
            raise ValueError("The selected ship is not occupied; nothing was deleted.")  # Do not silently repair a different defect.

    # _prepare_handlers: Select the ordinary/custom/Corvette strategy for each complete targeted ship bundle.
    def _prepare_handlers(self):
        kinds = {index: _ship_kind(self.ships[index], self.appearances[customisation_index(index)]) for index in self.targets}  # Validate identity/parts first.
        donors = load_delete_templates() if self.templates is None else self.templates  # Never read a live-save donor at runtime.
        return {index: DELETION_HANDLERS[kind](donors) for index, kind in kinds.items()}  # Category-specific behavior is explicit.

    # _validate_builds: Collect uniquely linked whole Corvette records before applying any staged cleanup.
    def _validate_builds(self, handlers):
        positions = set()  # These are base-list positions, not ownership indices.
        for index, handler in handlers.items():  # Ordinary/custom handlers deliberately contribute no build removals.
            positions.update(handler.linked_base_positions(self.bases, index))  # Ambiguous/missing Corvette builds refuse the entire request.
        return positions  # Preserve the order/full contents of every base outside this set.

    # _apply_handlers: Change only an independent complete context after every selected build has been validated.
    def _apply_handlers(self, handlers, removed_bases):
        candidate = copy.deepcopy(self.context)  # No shared mutable ownership/appearance/build records with the caller.
        player = candidate["PlayerStateData"]  # Operate only on the active editable branch.
        for index, handler in handlers.items():  # Each handler owns one type-specific complete cleanup operation.
            handler.apply(player, index)  # Keep twelve ownership entries and every surviving ship's original position.
        player["PersistentPlayerBases"] = [base for i, base in enumerate(player["PersistentPlayerBases"]) if i not in removed_bases]  # Whole builds only.
        return candidate  # Publishing and disk saving are not responsibilities of the planner.

    # _update_references: Repair only references to ships deleted by this combined request.
    def _update_references(self, player):
        if self.primary in self.targets:  # Leave the selected surviving ship unchanged.
            player["PrimaryShip"] = min(self.remaining)  # Deterministic first remaining occupied position.
        editor = self.player.get("CorvetteEditAssociatedShipIndex")  # An absent editor index is not invented.
        if type(editor) is int and editor in self.targets:  # Clear only the exact deleted referenced ship.
            player["CorvetteEditAssociatedShipIndex"] = -1  # Preserve unrelated/stale references and other draft/editor fields.

    # build: Orchestrate the small purpose-specific planning steps without mutating the caller's data.
    def build(self):
        if not self.targets:  # Empty selections/slots must not read donors or change any model state.
            return copy.deepcopy(self.context), []  # Preserve the existing semantic no-op contract.
        self._validate_linked_data()  # Reject malformed parallel data and selected-ship state.
        handlers = self._prepare_handlers()  # Keep classification separate from mutation.
        removed_bases = self._validate_builds(handlers)  # Validate every Corvette association first.
        candidate = self._apply_handlers(handlers, removed_bases)  # Stage one whole-context candidate.
        self._update_references(candidate["PlayerStateData"])  # Apply the agreed selection/editor policy once.
        return candidate, self.targets  # No partial request is published or written here.


# plan_starship_deletions: Preserve the public planner entry point while delegating responsibilities to the plan object.
def plan_starship_deletions(context, indices, templates=None):
    return StarshipDeletionPlan(context, indices, templates).build()  # File > Save remains a separate user action.
