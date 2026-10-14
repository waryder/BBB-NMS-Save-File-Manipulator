# File: StarshipUpgrade.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\StarshipUpgrade.py
# Purpose: Plan reference tech replacement, Corvette missing-only upgrades and independent stats/class changes.
import copy  # Stage independent candidates so refusal never changes the original ship.
import math  # Refuse invalid numeric reference statistics.
import random  # Choose needed copies only from the actual matching reference records.
import re  # Strip only numeric procedural seed suffixes, not ordinary or escaped hashed IDs.
from collections import Counter  # Count base technology IDs, including repeated modules.

DEBUG_PREFIX = "[BBB-NMS-SFM/StarshipUpgrade]"  # Identify diagnostics from this module.
DEBUG_ENABLED = False  # Keep non-error diagnostics off unless explicitly enabled.
BASE_SCENES = {  # Exact known base scenes avoid guessing unknown models from a directory.
    "FIGHTERS/FIGHTER_PROC.SCENE.MBIN": "fighter",
    "DROPSHIPS/DROPSHIP_PROC.SCENE.MBIN": "hauler",
    "SCIENTIFIC/SCIENTIFIC_PROC.SCENE.MBIN": "explorer",
    "SHUTTLE/SHUTTLE_PROC.SCENE.MBIN": "shuttle",
    "S-CLASS/S-CLASS_PROC.SCENE.MBIN": "royal",
    "S-CLASS/BIOPARTS/BIOSHIP_PROC.SCENE.MBIN": "living",
    "SENTINELSHIP/SENTINELSHIP_PROC.SCENE.MBIN": "sentinel",
    "SAILSHIP/SAILSHIP_PROC.SCENE.MBIN": "solar",
    "BIGGS/BIGGS.SCENE.MBIN": "corvette",
}
SPECIAL_SCENES = {  # Resolve explicit special associations before ordinary family scenes.
    "FIGHTERS/WRACER.SCENE.MBIN": "starborn_shared",
    "FIGHTERS/WRACERSE.SCENE.MBIN": "starborn_shared",
    "FIGHTERS/SPOOKSHIP.SCENE.MBIN": "boundary_herald",
    "FIGHTERS/VRSPEEDER.SCENE.MBIN": "fighter",
    "FIGHTERS/RASAMAMAGOLD.SCENE.MBIN": "fighter",  # Golden Rasamama S36 uses the Fighter reference.
    "FIGHTERS/VINTAGEINTERCEPTOR.SCENE.MBIN": "sentinel",
    "FIGHTERS/FIGHTERCLASSICGOLD.SCENE.MBIN": "fighter",  # Golden Vector uses the Fighter reference.
    "S-CLASS/BIOPARTS/BIOFIGHTER.SCENE.MBIN": "living",  # The Wraith and this exact biological scene use Living.
}
STAT_IDS = {"^SHIP_DAMAGE", "^SHIP_SHIELD", "^SHIP_HYPERDRIVE", "^SHIP_AGILE"}  # Required reference statistics.


# reference_family: Select only a confirmed scene association, never a ship display name.
def reference_family(ship):
    resource = ship.get("Resource") if isinstance(ship, dict) else None  # Require an ownership record.
    scene = resource.get("Filename") if isinstance(resource, dict) else None  # Inspect the resource scene.
    if not isinstance(scene, str):  # Empty ownership slots and malformed resources cannot be guessed.
        raise ValueError("Missing ship resource scene.")  # Report a ship-specific refusal.
    prefix = "MODELS/COMMON/SPACECRAFT/"  # Known scenes are rooted in the spacecraft directory.
    normalized = scene.replace("\\", "/").upper()  # Compare scenes without mutating the saved resource.
    relative = normalized[len(prefix):] if normalized.startswith(prefix) else ""  # Do not match arbitrary paths.
    family = SPECIAL_SCENES.get(relative) or BASE_SCENES.get(relative)  # Special exceptions always win.
    if family is None:  # Unknown and future scenes must remain untouched.
        raise ValueError(f"Unsupported ship scene: {scene or '(empty)' }.")  # Explain why no donor was used.
    return family  # The caller uses the approved reference filename for this family.


# _inventory: Require an existing inventory object without creating missing structures.
def _inventory(ship, key):
    inventory = ship.get(key) if isinstance(ship, dict) else None  # Read only the requested node.
    if not isinstance(inventory, dict):  # Reject incompatible ownership schemas before copying fields.
        raise ValueError(f"Missing or malformed {key}.")  # Keep the affected ship unchanged.
    return inventory  # Return a reference for inspection, not mutation.


# _coordinate: Validate nonnegative integer coordinates, excluding Python bool values.
def _coordinate(index):
    if not isinstance(index, dict):  # Inventory cells must be coordinate objects.
        raise ValueError("Malformed technology slot coordinate.")  # Refuse ambiguous placement.
    values = (index.get("X"), index.get("Y"))  # Retain the saved X/Y convention.
    if any(type(value) is not int or value < 0 for value in values):  # Bool/float/string are not cells.
        raise ValueError("Malformed technology slot coordinate.")  # Do not coerce invalid values.
    return values  # Hashable coordinates support collision checks.


# _slots: Validate item records and count only installed technology IDs as matching technology.
def _slots(inventory, donor=False):
    slots = inventory.get("Slots")  # Require a real array rather than silently treating null as empty.
    if not isinstance(slots, list):  # A malformed tech structure is not a safe upgrade target.
        raise ValueError("Missing or malformed technology items.")  # Refuse before staging any mutation.
    for slot in slots:  # Validate even retained records so collisions cannot be concealed.
        if not isinstance(slot, dict) or not isinstance(slot.get("Id"), str) or not slot["Id"]:  # Exact IDs only.
            raise ValueError("Malformed technology item ID.")  # Never invent or repair a source ID.
        kind = slot.get("Type")  # Item type distinguishes installed technologies from other entries.
        if not isinstance(kind, dict) or not isinstance(kind.get("InventoryType"), str):  # Require typed records.
            raise ValueError("Malformed technology item type.")  # Leave incompatible records untouched.
        if donor and kind["InventoryType"] != "Technology":  # Only donor technology may be inserted.
            raise ValueError("Reference contains a non-technology tech item.")  # No build/cargo substitution.
        _coordinate(slot.get("Index"))  # Validate the saved cell without modifying it.
    return slots  # Existing records remain intact in the later candidate copy.


# _stats: Validate complete donor stat lists while preserving family-specific markers verbatim.
def _stats(inventory):
    values = inventory.get("BaseStatValues")  # Complete matched-donor lists are the approved payload.
    if not isinstance(values, list):  # Missing data must not erase the target statistics.
        raise ValueError("Reference is missing base statistics.")  # Refuse a malformed donor.
    ids = []  # Detect duplicate stat definitions rather than silently overwriting them.
    for record in values:  # Inspect every general or family-specific statistic.
        if not isinstance(record, dict) or not isinstance(record.get("BaseStatID"), str):  # Require named stats.
            raise ValueError("Malformed reference base statistics.")  # Do not insert an invalid payload.
        value = record.get("Value")  # Each stat must have a finite numeric value.
        if not isinstance(value, (int, float)) or isinstance(value, bool):  # Reject nonnumeric and boolean stats.
            raise ValueError("Malformed reference stat value.")  # Refuse without partial changes.
        try:  # Extremely large malformed integers can overflow finite-number conversion.
            finite = math.isfinite(value)  # Accept only finite numeric reference values.
        except OverflowError as exc:  # Convert invalid numeric payloads into a safe per-ship refusal.
            raise ValueError("Malformed reference stat value.") from exc  # Preserve the original ship.
        if not finite:  # JSON NaN and infinity must not enter the editable context.
            raise ValueError("Malformed reference stat value.")  # Refuse without partial changes.
        ids.append(record["BaseStatID"])  # Keep list order and all family marker records.
    if len(set(ids)) != len(ids) or not STAT_IDS.issubset(ids):  # Require the four approved base statistics.
        raise ValueError("Reference base statistics are incomplete or duplicated.")  # No guessing.
    return values  # Deep-copy the exact list only after the entire candidate is validated.


# _class: Require an S-class donor setting and preserve its complete class object.
def _class(inventory):
    value = inventory.get("Class")  # The approved class changes cover Inventory and Inventory_Cargo only.
    if not isinstance(value, dict) or value.get("InventoryClass") != "S":  # Reject unexpected donors.
        raise ValueError("Reference is missing an S-class setting.")  # Do not downgrade from malformed input.
    return value  # Other inventory fields remain untouched.


# _base_tech_id: Ignore a procedural numeric seed while preserving the full technology tag, including its class suffix.
def _base_tech_id(item_id):
    match = re.fullmatch(r"(\^[A-Za-z0-9_]+)#[0-9]+", item_id)  # Known seeded module IDs; a trailing hash alone is not a seed.
    return match.group(1) if match else item_id  # Ordinary IDs and escaped hashed IDs remain distinct and unchanged.


# _missing_items: Count by base technology ID and randomly select only the required reference occurrences.
def _missing_items(existing, reference):
    available = Counter(_base_tech_id(slot["Id"]) for slot in existing if slot["Type"]["InventoryType"] == "Technology")  # Existing seeds do not create deficits.
    groups = {}  # Preserve first-seen reference type order without fabricating modules or seeds.
    for slot in reference:  # Repeated reference records define the required count for that base type.
        groups.setdefault(_base_tech_id(slot["Id"]), []).append(slot)  # Keep complete donor records for later copying.
    missing = []  # The same list drives capacity analysis and actual insertion.
    for base_id, records in groups.items():  # Each technology type is independently satisfied by existing copies.
        deficit = max(0, len(records) - available[base_id])  # Extra existing modules are retained, never replaced or removed.
        if deficit:  # Already-satisfied groups need no random draw or insertion.
            missing.extend(random.sample(records, deficit))  # Sample records without replacement; repeated donor occurrences remain legitimate copies.
    return missing  # Copying preserves selected seeds exactly; a repeated upgrade has no technology additions.


# _sixty_cell_inventory: Stage a fully enabled 10x6 tech grid while retaining installed items and supercharged cells.
def _sixty_cell_inventory(inventory, slots):
    _free_cells(inventory, slots)  # Validate the original layout even when the donor contains no technology.
    cells = [{"X": x, "Y": y} for y in range(6) for x in range(10)]  # Exactly sixty enabled cells, not empty item placeholders.
    allowed = {(cell["X"], cell["Y"]) for cell in cells}  # One canonical target geometry for every selected ship type.
    if any(_coordinate(slot["Index"]) not in allowed for slot in slots):  # Never relocate/delete equipment to shrink an oversized grid.
        raise ValueError("Existing equipment lies outside the 60-slot tech grid; upgrade refused to preserve it.")  # Entire ship stays unchanged.
    special = inventory.get("SpecialSlots", [])  # Preserve each existing supercharged-cell record rather than copy the donor layout.
    if not isinstance(special, list) or any(not isinstance(slot, dict) or _coordinate(slot.get("Index")) not in allowed for slot in special):
        raise ValueError("Supercharged cells lie outside or are incompatible with the 60-slot tech grid.")  # No silent loss of bonuses.
    candidate = copy.deepcopy(inventory)  # Capacity changes remain private until the complete upgrade succeeds.
    candidate.update(Width=10, Height=6, ValidSlotIndices=cells, NumSlotsFromTech=0)  # Match the existing sixty-cell reference convention.
    return candidate  # Installed records and all unrelated inventory fields remain intact.


# _free_cells: Find enabled, unused live cells without copying or expanding the donor layout.
def _free_cells(inventory, slots):
    enabled = inventory.get("ValidSlotIndices")  # The target's enabled cells alone authorize placement.
    width, height = inventory.get("Width"), inventory.get("Height")  # Preserve existing dimensions.
    if not isinstance(enabled, list) or any(type(n) is not int or n <= 0 for n in (width, height)):  # Require geometry.
        raise ValueError("Missing or malformed enabled technology layout.")  # Never invent expansion.
    cells = [_coordinate(index) for index in enabled]  # Validate all target enabled cells.
    occupied = [_coordinate(slot["Index"]) for slot in slots]  # Reserve every existing item, including build parts.
    if len(set(cells)) != len(cells) or any(x >= width or y >= height for x, y in cells):  # Reject invalid layout.
        raise ValueError("Enabled technology layout has duplicate or out-of-bounds cells.")  # Refuse safely.
    if len(set(occupied)) != len(occupied) or not set(occupied).issubset(cells):  # Ambiguous live layout is unsafe.
        raise ValueError("Existing technology has overlapping or disabled cells.")  # Do not move existing items.
    return [cell for cell in cells if cell not in set(occupied)]  # Preserve target enabled-cell order.


# _place_items: Append independent donor item copies at unused live coordinates only.
def _place_items(candidate, missing, cells):
    occupied = {_coordinate(slot["Index"]) for slot in candidate["Slots"]}  # Track every preserved item.
    remaining = list(cells)  # Use a deterministic target-order fallback when donor positions collide.
    for slot in missing:  # Every addition is independent of both source donor and original target.
        preferred = _coordinate(slot["Index"])  # Use a donor cell only if it is valid and unoccupied.
        cell = preferred if preferred in remaining and preferred not in occupied else remaining[0]  # No collision.
        addition = copy.deepcopy(slot)  # Preserve the complete item, including its generated seed and flags.
        addition["Index"]["X"], addition["Index"]["Y"] = cell  # Only placement coordinates change.
        candidate["Slots"].append(addition)  # Existing items retain order, position and complete contents.
        occupied.add(cell)  # Reserve the new cell before planning the next addition.
        remaining.remove(cell)  # Never reuse an enabled cell within this upgrade.


# _upgrade_technology: Replace ordinary ship equipment or add only missing Corvette technology.
def _upgrade_technology(target_tech, ref_tech, corvette):
    donor_slots = _slots(ref_tech, donor=True)  # Validate complete reference records before any equipment change.
    _free_cells(ref_tech, donor_slots)  # Reject overlapping, disabled or out-of-bounds donor records.
    if corvette:  # Corvette builds and existing equipment must never be wholesale replaced.
        existing = _slots(target_tech)  # Validate retained equipment before planning additions.
        expanded = _sixty_cell_inventory(target_tech, existing)  # Stage sixty cells without deleting build items.
        missing = _missing_items(existing, donor_slots)  # Count base types while preserving existing seeds.
        cells = _free_cells(expanded, existing)  # Capacity and insertion share one staged inventory.
        if len(missing) > len(cells):  # Insufficient space skips only technology, not statistics/class.
            raise ValueError(f"Not enough enabled tech space: need {len(missing)}, have {len(cells)}.")  # Report actual deficit.
        _place_items(expanded, missing, cells)  # Preserve existing records and append actual reference copies.
        return expanded, len(missing)  # Report only added technology for Corvettes.
    donor_grid = _sixty_cell_inventory(ref_tech, donor_slots)  # Validate all replacement positions in the sixty-cell grid.
    replacement = copy.deepcopy(target_tech)  # Retain inventory metadata outside the authorized equipment/capacity fields.
    for key in ("Slots", "Width", "Height", "ValidSlotIndices", "NumSlotsFromTech"):  # Copy complete reference items/seeds/positions.
        replacement[key] = copy.deepcopy(donor_grid[key])  # Never merge original equipment into ordinary references.
    _sixty_cell_inventory(replacement, donor_slots)  # Validate preserved target supercharged cells against the new grid.
    count = len(donor_slots) if replacement["Slots"] != target_tech.get("Slots") else 0  # Repeated replacement is a no-op.
    return replacement, count  # Reference equipment is independent of both input objects.


# upgrade_ship: Apply approved stats/classes even when the independent technology step is skipped.
def upgrade_ship(ship, reference, details=None):
    target_inv, target_tech = _inventory(ship, "Inventory"), _inventory(ship, "Inventory_TechOnly")  # Require editable inventory nodes.
    target_cargo = _inventory(ship, "Inventory_Cargo")  # Cargo contents and geometry are never replaced.
    ref_inv, ref_tech = _inventory(reference, "Inventory"), _inventory(reference, "Inventory_TechOnly")  # Require matched donor nodes.
    ref_cargo = _inventory(reference, "Inventory_Cargo")  # Validate the approved cargo-class payload.
    stats, tech_stats = _stats(ref_inv), _stats(ref_tech)  # Invalid statistics remain a whole-ship rejection.
    inventory_class, cargo_class = _class(ref_inv), _class(ref_cargo)  # Invalid classes cannot claim a successful upgrade.
    corvette = reference_family(ship) == "corvette"  # Only confirmed Corvettes use missing-only equipment logic.
    candidate, count, tech_reason = copy.deepcopy(ship), 0, ""  # Keep caller data immutable during both upgrade steps.
    try:  # Technology has its own all-or-nothing boundary independent of stats/class.
        candidate["Inventory_TechOnly"], count = _upgrade_technology(target_tech, ref_tech, corvette)  # Stage equipment/capacity together.
    except (ValueError, TypeError, KeyError) as exc:  # Leave original tech items/layout intact on a technology failure.
        tech_reason = str(exc)  # The result report must explicitly identify the skipped technology step.
    candidate["Inventory"]["BaseStatValues"] = copy.deepcopy(stats)  # Apply validated reference ship statistics.
    candidate["Inventory_TechOnly"]["BaseStatValues"] = copy.deepcopy(tech_stats)  # Apply approved tech statistics even when equipment is skipped.
    candidate["Inventory"]["Class"], candidate["Inventory_Cargo"]["Class"] = copy.deepcopy(inventory_class), copy.deepcopy(cargo_class)  # Preserve all other cargo fields.
    if details is not None:  # Batch callers receive honest partial-success information without breaking tuple callers.
        details.update(tech_mode="missing-only" if corvette else "replacement", tech_skipped=bool(tech_reason), tech_reason=tech_reason)  # Report actual branch.
    return candidate, count  # A technology failure never rolls back valid stats/class changes.


# is_unoccupied: Identify an absent ship solely from an empty or absent resource filename.
def is_unoccupied(ship):
    if not isinstance(ship, dict):  # Malformed records are errors, not ordinary empty slots.
        return False  # Preserve existing validation and rejection behavior.
    resource = ship.get("Resource", {})  # An absent resource supplies no filename.
    if not isinstance(resource, dict):  # Do not hide malformed resource structures as unoccupied.
        return False  # Leave incompatible resource data to the normal validator.
    return resource.get("Filename") in (None, "")  # Name and seed do not determine occupancy.


# ship_label: Produce distinct labels for unoccupied, unnamed and named ownership slots.
def ship_label(ship, index):
    if is_unoccupied(ship):  # Missing ship resource, even if stale name/seed fields remain.
        return f"Slot {index + 1} - (unoccupied)"  # Preserve the exact requested one-based text.
    name = ship.get("Name") if isinstance(ship, dict) else None  # Never use names for donor selection.
    return name if isinstance(name, str) and name.strip() else f"Starship {index + 1} (unnamed)"  # Honest fallback.


# plan_upgrades: Plan each selected ship independently and report refusals without altering inputs.
def plan_upgrades(ships, indices, load_reference):
    if not isinstance(ships, list):  # An upgrade cannot operate on TeleportEndpoints or an absent context.
        raise ValueError("No valid ship ownership list is loaded.")  # The GUI reports this before mutation.
    candidate, results, references = copy.deepcopy(ships), [], {}  # Keep both inputs and donor cache independent.
    for index in dict.fromkeys(indices):  # Deduplicate selections while preserving UI selection order.
        if type(index) is not int or not 0 <= index < len(ships):  # Refuse invalid selection state.
            raise ValueError("Invalid selected ship index.")  # Do not publish a partially planned batch.
        ship = ships[index]  # Read from the original list, never a prior candidate mutation.
        result = {"index": index, "name": ship_label(ship, index), "status": "rejected", "reason": "", "added": 0}  # Explicit outcomes.
        if is_unoccupied(ship):  # Empty ownership cells are not rejected ships.
            result["status"] = "unoccupied"  # Report a separate no-op outcome without reference loading.
            results.append(result)  # Keep the selected slot in the results list.
            continue  # Preserve the entire empty record and all other ship candidates.
        try:  # A per-ship refusal must not prevent other selected ships from upgrading.
            family = reference_family(ship)  # Resolve special scenes before ordinary mappings.
            if family not in references:  # Read each matched reference at most once per upgrade request.
                reference = load_reference(f"reference_{family}.json")  # Current integrated donors only.
                if reference_family(reference) != family:  # Wrong-family references must never replace family markers.
                    raise ValueError("Reference ship family does not match the selected ship.")  # Safe per-ship refusal.
                references[family] = reference  # Cache only a donor with the confirmed association.
            upgraded, added = upgrade_ship(ship, references[family], result)  # Staging never changes the original.
            result.update(status="partial" if result["tech_skipped"] else ("upgraded" if upgraded != ship else "unchanged"), added=added)  # Distinguish no-op.
            candidate[index] = upgraded  # Publish only a fully validated per-ship candidate to the staged list.
        except (ValueError, TypeError, KeyError, OSError) as exc:  # Schema/reference/placement failures are refusals.
            result["reason"] = str(exc)  # Brief notes identify the affected ship and exact failure.
        results.append(result)  # Include every selected ship, even rejected and already-complete ships.
    return candidate, results  # No Qt, disk write, context switch, sorting or automatic live save occurs here.
