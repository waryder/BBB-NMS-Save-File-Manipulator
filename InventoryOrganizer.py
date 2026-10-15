# File: InventoryOrganizer.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\InventoryOrganizer.py
# Purpose: Pure, whole-record inventory routing on independent active-context snapshots.
import copy  # Never mutate the model while planning.
import json  # Compare exact JSON types and numeric representations for stale checks.
from dataclasses import dataclass, field  # Small purpose-specific result and roster records.
from typing import Any  # Opaque JSON payloads remain deliberately schema-preserving.

CATEGORIES = ('Substance', 'Product', 'Technology', 'Consumable', 'Trade', 'Special')
ROOT = ('PlayerStateData',)
CHESTS = tuple(ROOT + ('Chest%dInventory' % number,) for number in range(1, 11))
SOURCE_PATHS = (ROOT + ('Inventory',),) + CHESTS + tuple(
    ROOT + (key,) for key in ('FreighterInventory', 'FishPlatformInventory',
                             'FishBaitBoxInventory', 'CookingIngredientsInventory')) + tuple(
    ROOT + ('ShipOwnership', index, 'Inventory') for index in range(12))

# resolve: Follow true context-relative keys without filtered-index substitution.
def resolve(context, path) -> Any:
    value = context  # Begin at the selected active context, not a retained full save.
    try:
        for key in path:  # Integer ownership slots remain integers.
            value = value[key]
        return value
    except (KeyError, IndexError, TypeError):
        return None  # Missing inventory entries are not fabricated.

# same_context: Compare canonical JSON without conflating booleans, integers or rounded floats.
def same_context(left, right):
    return json.dumps(left, sort_keys=True, ensure_ascii=True, allow_nan=False) == json.dumps(
        right, sort_keys=True, ensure_ascii=True, allow_nan=False)

@dataclass(frozen=True)
class InventoryEntry:
    path: tuple
    label: str
    carried: bool

# inventory_label: Decorate an exact path with the currently loaded inventory/ship name.
def inventory_label(context, path, inventory):
    key = path[1]  # Identity always comes from the true path.
    names = {'Inventory': 'Exosuit', 'FreighterInventory': 'Freighter',
             'FishPlatformInventory': 'Fish Platform', 'FishBaitBoxInventory': 'Fish Bait Box',
             'CookingIngredientsInventory': 'Cooking Ingredients'}
    base = names.get(key, key)
    if path in CHESTS:
        base = 'Container %d' % (CHESTS.index(path) + 1)
    if key == 'ShipOwnership':
        ship = resolve(context, path[:-1])
        base = 'Starship %d' % (path[2] + 1)
        if ship.get('Name'):
            base += ' — ' + str(ship['Name'])
    return base + ': ' + str(inventory.get('Name') or 'No name provided')

# inventory_roster: Match DataViews' roster, skipping unavailable and identifiable unoccupied ships.
def inventory_roster(context):
    entries = []  # Preserve roster order but never use filtered indices as identity.
    for path in SOURCE_PATHS:
        inventory = resolve(context, path)
        if not isinstance(inventory, dict) or not isinstance(inventory.get('Slots'), list):
            continue  # Placeholder or missing data cannot be routed.
        if path[1] == 'ShipOwnership':
            ship = resolve(context, path[:-1])
            resource = ship.get('Resource', {})
            if isinstance(resource, dict) and resource.get('Filename') == '':
                continue  # No unoccupied ownership-slot destinations.
        carried = path[1] in ('Inventory', 'FreighterInventory', 'ShipOwnership', 'FishPlatformInventory')
        entries.append(InventoryEntry(path, inventory_label(context, path, inventory), carried))
    return entries

# coordinate: Validate cells before using them as occupancy keys.
def coordinate(index):
    if not isinstance(index, dict) or any(type(index.get(key)) is not int for key in ('X', 'Y')):
        raise ValueError('An inventory cell has an invalid X/Y position; no changes applied.')
    return index['X'], index['Y']  # Unknown Index fields survive unless the record actually moves.

# validate_inventory: Refuse malformed records rather than losing or overlapping items.
def validate_inventory(inventory):
    if not isinstance(inventory.get('ValidSlotIndices'), list):
        raise ValueError('An inventory has no valid cell list; no changes applied.')
    for slot in inventory['Slots']:
        coordinate(slot.get('Index'))  # Equal original occurrences remain separate records, never equality-removed.
    for cell in inventory['ValidSlotIndices']:
        coordinate(cell)  # Sparse and nonstandard grids remain valid when expansion is off.

# expanded_cells: Build the existing sorter's 120-cell assumption without shrinking unusual grids.
def expanded_cells(inventory):
    grid = [{'X': x, 'Y': y} for x in range(10) for y in range(12)]
    allowed = {coordinate(cell) for cell in grid}
    existing = [coordinate(cell) for cell in inventory['ValidSlotIndices']]
    occupied = [coordinate(slot['Index']) for slot in inventory['Slots']]
    if len(existing) > 120 or not set(existing + occupied).issubset(allowed):
        raise ValueError('Cannot expand this inventory to 120 cells without shrinking its grid or losing positions.')
    return grid  # Width, Height, existing records and all other metadata are left alone.

# free_cell: Preserve a preferred cell if valid, otherwise use an actual unoccupied valid position.
def free_cell(inventory, preferred):
    occupied = {coordinate(slot['Index']) for slot in inventory['Slots']}
    cells = inventory['ValidSlotIndices']
    wanted = coordinate(preferred)
    if wanted not in occupied and any(coordinate(cell) == wanted for cell in cells):
        return copy.deepcopy(preferred)  # Preserve any opaque Index metadata when the same position is usable.
    return next(({'X': cell['X'], 'Y': cell['Y']} for cell in cells
                 if coordinate(cell) not in occupied), None)

@dataclass
class InventoryPlan:
    candidate: dict
    moves: list = field(default_factory=list)
    stays: list = field(default_factory=list)
    expanded: list = field(default_factory=list)  # Explicit destinations only; overflow growth is intentionally silent.
    changed: bool = False

class InventoryPlanner:
    # __init__: Own an independent immutable-by-convention baseline for this planning request.
    def __init__(self, context):
        if not isinstance(context, dict) or not isinstance(context.get('PlayerStateData'), dict):
            raise ValueError('No valid editable save context is loaded.')
        self.original = copy.deepcopy(context)
        self.entries = {entry.path: entry for entry in inventory_roster(self.original)}

    # _choices: Validate explicit source and category destinations against the exact available roster.
    def _choices(self, sources, routes):
        sources = set(tuple(path) for path in sources)  # Repeated selections cannot duplicate records.
        routes = {category: tuple(path) if path else None for category, path in routes.items()}
        if any(category not in CATEGORIES for category in routes):
            raise ValueError('Unknown inventory routing category.')
        assigned = {path for path in routes.values() if path}
        if not (sources | assigned).issubset(self.entries):
            raise ValueError('A selected inventory is no longer available.')
        return sources, routes, assigned

    # _expand_assigned: Expand every indicated destination even when no stacks will arrive.
    def _expand_assigned(self, result, assigned):
        for path in SOURCE_PATHS:
            if path not in assigned:
                continue
            inventory = resolve(result.candidate, path)
            cells = expanded_cells(inventory)
            if inventory['ValidSlotIndices'] != cells:
                inventory['ValidSlotIndices'] = cells
                result.expanded.append(path)  # Never include an implicit overflow target here.

    # _destination: Try the assigned target then only unassigned chest overflow, backward from ten.
    def _destination(self, result, source, target, record, assigned, overflow, expand):
        choices = [target] + ([path for path in reversed(CHESTS)
                              if path not in assigned and path != source and path in self.entries] if overflow else [])
        for path in choices:
            inventory = resolve(result.candidate, path)
            cell = free_cell(inventory, record['Index'])
            if path not in assigned and expand:
                cells = expanded_cells(inventory)  # Refuse unsafe growth before insertion, even if one old cell is free.
                trial = dict(inventory, ValidSlotIndices=cells)
                cell = free_cell(trial, record['Index'])
                if cell is not None:
                    inventory['ValidSlotIndices'] = cells  # Silent and only when this spare will receive a stack.
            if cell is not None:
                return path, cell
        return None, None  # No capacity means retain the complete source occurrence unchanged.

    # _route_record: Route one original occurrence, never a newly arrived record.
    def _route_record(self, result, source, ordinal, record, routes, assigned, overflow, expand):
        category = record.get('Type', {}).get('InventoryType')
        target = routes.get(category) if category in CATEGORIES else None
        detail = {'item': str(record.get('Id', 'Unnamed item')), 'from': source, 'ordinal': ordinal}
        if not target:
            result.stays.append(dict(detail, reason='unmatched category' if category not in CATEGORIES else 'no destination chosen'))
            return False
        if target == source:
            return False  # Do not overflow or reposition a same-inventory route.
        destination, cell = self._destination(result, source, target, record, assigned, overflow, expand)
        if destination is None:
            result.stays.append(dict(detail, reason='destination full'))
            return False
        moved = copy.deepcopy(record)
        moved['Index'] = cell  # This is the only field changed on a moved stack.
        resolve(result.candidate, destination)['Slots'].append(moved)
        result.moves.append(dict(detail, to=destination, category=category))
        return True

    # _route_sources: Consume original occurrences once, freeing moved-out cells without equality-based removal.
    def _route_sources(self, result, sources, routes, assigned, overflow, expand):
        occurrences = {source: list(resolve(result.candidate, source)['Slots']) for source in sources}
        for source in SOURCE_PATHS:
            if source not in sources:
                continue
            for ordinal, record in enumerate(resolve(self.original, source)['Slots']):
                if self._route_record(result, source, ordinal, record, routes, assigned, overflow, expand):
                    slots = resolve(result.candidate, source)['Slots']
                    original = occurrences[source][ordinal]  # Identity is unique per original occurrence, not item ID/equality.
                    index = next(index for index, item in enumerate(slots) if item is original)
                    slots.pop(index)  # Free the real source cell immediately; arrivals never enter the original iteration.

    # plan: Stage whole-record moves on a deep copy and track original source occurrences only.
    def plan(self, sources, routes, overflow=False, expand=False):
        sources, routes, assigned = self._choices(sources, routes)
        result = InventoryPlan(copy.deepcopy(self.original))
        for path in sources | assigned | (set(CHESTS).intersection(self.entries) if overflow else set()):
            validate_inventory(resolve(result.candidate, path))  # Fail before any publication, never repair silently.
        if expand:
            self._expand_assigned(result, assigned)
        self._route_sources(result, sources, routes, assigned, overflow, expand)
        result.changed = not same_context(result.candidate, self.original)
        return result
