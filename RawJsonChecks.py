# File: RawJsonChecks.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\RawJsonChecks.py
# Purpose: App-integrity checks run before Raw JSON is applied. They protect this app's own processing
#          (Node View labels, Sort Bases, inventory/ship lookups, Set Player Location). They do NOT validate
#          No Man's Sky game rules; game correctness is the user's responsibility per the app disclaimers.

from imports import (get_galaxy_system_planet_from_full_addr, GALAXIES,  # Same helpers the Bases labels use.
                     GALAXY_FROM_GALACTIC_ADDR_IDX, SYSTEM_FROM_GALACTIC_ADDR_IDX)

MAX_STARSHIPS = 12  # The app's starship labels and inventory lookups know exactly 12 ship slots.
ADDRESS_INT_FIELDS = ('VoxelX', 'VoxelY', 'VoxelZ', 'SolarSystemIndex', 'PlanetIndex')  # Endpoint label fields.


# first_entry_problem: Return a user-facing reason a tab's array cannot be processed, or None when it is usable.
def first_entry_problem(model_context, entries):
    if model_context == 'tab2' and len(entries) > MAX_STARSHIPS:  # Fixed ship-slot count used by the app.
        return f'Starships can hold at most {MAX_STARSHIPS} entries; this text has {len(entries)}.'
    check = ENTRY_CHECKS.get(model_context)  # Per-tab field rules.
    if check is None:  # Contexts without rules keep their previous behaviour.
        return None
    for index, entry in enumerate(entries):  # Report the first problem only.
        if not isinstance(entry, dict):  # Every tab processes each entry as a JSON object.
            return f'Entry [{index}] must be a JSON object ({{ ... }}).'
        problem = check(entry)  # Tab-specific required fields.
        if problem:  # Stop at the first unusable entry.
            return f'Entry [{index}]: {problem}'
    return None  # Every entry can be processed.


# teleport_location_problem: Return why an endpoint cannot be used by Set Player Location, or None.
def teleport_location_problem(endpoint):
    if not isinstance(endpoint, dict) or not isinstance(endpoint.get('UniverseAddress'), dict):  # Address is copied.
        return "This endpoint has no usable 'UniverseAddress'."
    position = endpoint.get('Position')  # Three coordinates are copied into the player position.
    if not isinstance(position, list) or len(position) < 3:  # Fewer would fail part-way through the update.
        return "This endpoint's 'Position' must be a list of three numbers."
    return None  # Safe to apply.


# _name_problem: The labels join Name into text, and Sort Bases compares names, so Name must be text or empty.
def _name_problem(entry):
    if 'Name' not in entry:  # Every tab label reads Name.
        return "'Name' is missing."
    name = entry['Name']  # Empty values are replaced by the app's default label text.
    if name and not isinstance(name, str):  # Numbers, objects or lists cannot be joined into a label.
        return "'Name' must be text."
    return None  # Usable name.


# _base_address_usable: Run the same conversions the Bases label and Sort Bases use; True when they succeed.
def _base_address_usable(value):
    try:
        parts = get_galaxy_system_planet_from_full_addr(value)  # The label calls this for every base.
        if parts[GALAXY_FROM_GALACTIC_ADDR_IDX]:  # The label looks up a non-empty galaxy part.
            GALAXIES[int(parts[GALAXY_FROM_GALACTIC_ADDR_IDX], 16)]  # Same lookup as the label.
        if value:  # Sort Bases converts both parts whenever the address is not empty.
            int(parts[GALAXY_FROM_GALACTIC_ADDR_IDX], 16)  # Galaxy sort key.
            int(parts[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16)  # System sort key.
        return True  # Label and sort can both process it.
    except Exception:  # Any failure here would also fail in the label or sort code.
        return False


# _check_base: Fields the Bases Node View label and Sort Bases rely on.
def _check_base(entry):
    problem = _name_problem(entry)  # Label and sort both read Name.
    if problem:
        return problem
    if not _base_address_usable(entry.get('GalacticAddress')):  # Missing addresses also fail.
        return "'GalacticAddress' is missing or is not an address the app can read."
    if 'Objects' in entry and not isinstance(entry['Objects'], list):  # The label counts Objects records.
        return "'Objects' must be a JSON array."
    return None  # Usable base.


# _check_endpoint: Fields the Teleport Endpoints Node View label relies on.
def _check_endpoint(entry):
    problem = _name_problem(entry)  # The label shows Name.
    if problem:
        return problem
    universe = entry.get('UniverseAddress')  # Galaxy name comes from RealityIndex.
    if not isinstance(universe, dict) or not isinstance(universe.get('RealityIndex'), int):
        return "'UniverseAddress' must be an object with a whole-number 'RealityIndex'."
    galactic = universe.get('GalacticAddress')  # Portal address is built from these numbers.
    if not isinstance(galactic, dict) or not all(isinstance(galactic.get(k), int) for k in ADDRESS_INT_FIELDS):
        return "'UniverseAddress.GalacticAddress' must contain whole numbers for " + ', '.join(ADDRESS_INT_FIELDS) + '.'
    return None  # Usable endpoint.


ENTRY_CHECKS = {'tab1': _check_base, 'tab2': _name_problem, 'tab3': _name_problem, 'tab4': _check_endpoint}  # Per-tab rules.
