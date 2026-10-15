# File: InventoryOrganizerPreferences.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\InventoryOrganizerPreferences.py
# Purpose: Validate organizer-only preferences using true paths, retaining unavailable inventories.
from InventoryOrganizer import CATEGORIES, SOURCE_PATHS

# valid_path: Accept only exact supported identities, never labels or filtered row indices.
def valid_path(value):
    if not isinstance(value, (tuple, list)):
        return None
    path = tuple(value)
    # Reject booleans masquerading as integer ship slots and nested/unhashable payloads.
    if any(type(part) not in (str, int) for part in path):
        return None
    return path if path in SOURCE_PATHS else None

# organizer_settings: Normalize malformed or partial saved fields without losing valid absent paths.
def organizer_settings(value):
    value = value if isinstance(value, dict) else {}
    sources, routes = {}, {}
    records = value.get('sources', [])
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, (list, tuple)) or len(record) != 2:
            continue
        path = valid_path(record[0])
        if path is not None and type(record[1]) is bool:
            sources[path] = record[1]
    saved_routes = value.get('routes', {})
    if isinstance(saved_routes, dict):
        for category, target in saved_routes.items():
            path = valid_path(target)
            if category in CATEGORIES and (target is None or path is not None):
                routes[category] = path
    return {'sources': sources, 'routes': routes,
            'overflow': value.get('overflow') if type(value.get('overflow')) is bool else True,
            'expand': value.get('expand') if type(value.get('expand')) is bool else True}

# settings_payload: Serialize exact identities to JSON-compatible records without stringifying integers.
def settings_payload(settings):
    return {'sources': [[list(path), checked] for path, checked in settings['sources'].items()],
            'routes': {category: list(path) if path is not None else None
                       for category, path in settings['routes'].items()},
            'overflow': settings['overflow'], 'expand': settings['expand']}
