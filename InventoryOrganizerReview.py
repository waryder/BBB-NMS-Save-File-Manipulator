# File: InventoryOrganizerReview.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\InventoryOrganizerReview.py
# Purpose: Qt-free, whole-record Parts summaries with live routes and positive-destination review rows.
from collections import Counter  # Count records, never their Amount values.
from dataclasses import dataclass
from html import escape  # Loaded inventory names must remain literal, never markup.
from InventoryOrganizer import CATEGORIES, resolve

CATEGORY_NAMES = ('Resources', 'Crafted products', 'Technology', 'Consumables', 'Trade goods', 'Special items')

@dataclass(frozen=True)
class ReviewRow:
    key: tuple
    text: str

# _records: Group original source records into known categories or a safe unknown bucket.
def _records(context, source):
    groups: dict = {category: [] for category in CATEGORIES}
    groups[None] = []  # Never display unknown category payloads or individual item IDs.
    for ordinal, record in enumerate((resolve(context, source) or {}).get('Slots', [])):
        category = record.get('Type', {}).get('InventoryType')
        known = category if category in CATEGORIES else None
        groups[known].append(ordinal)
    return groups

# _counts: Aggregate exact proposed destinations and retained original occurrences for one row.
def _counts(source, category, target, ordinals, labels, plan):
    moves = [move for move in plan.moves if move['from'] == source and move['category'] == category]
    destinations = Counter(move['to'] for move in moves)  # First occurrence preserves overflow order.
    parts = ['%d Parts to destination' % destinations.pop(target, 0)]
    parts += ['%d Parts overflow to %s' % (count, labels[path]) for path, count in destinations.items()]
    retained = len(ordinals) - len(moves)  # Same-source routes are intentionally absent from plan.stays.
    if retained:
        reason = ('unknown category' if category is None else 'no destination chosen' if not target
                  else 'same destination' if target == source else 'destination full')
        parts.append('%d Parts retained (%s)' % (retained, reason))
    return ' + '.join(parts)

# review_rows: Build source-major/category-major rows without planning or exposing item-level data.
def review_rows(context, sources, routes, labels, plan=None):
    rows = []
    for source in sources:  # Caller supplies the visible roster selection order for both states.
        groups = _records(context, source)
        categories = list(CATEGORIES) + ([None] if groups[None] else [])
        for category in categories:
            target = routes.get(category) if category is not None else None
            name = CATEGORY_NAMES[CATEGORIES.index(category)] if category is not None else 'Unknown categories'
            destination = labels[target] if target else 'Leave where they are'
            text = '-> (%s)→(%s):(Cat: %s)' % (labels[source], destination, name)
            if plan is not None:
                # Review shows only positive assigned-destination transfers; live rows stay unfiltered.
                if not any(move['from'] == source and move['category'] == category and move['to'] == target
                           for move in plan.moves):
                    continue
                text += ': ' + _counts(source, category, target, groups[category], labels, plan)
            rows.append(ReviewRow((source, category, target), text))
    return rows

# review_text: Render plain text only, with brief non-item-level proposal and expansion notes.
def review_text(context, sources, routes, labels, plan=None):
    lines = [row.text for row in review_rows(context, sources, routes, labels, plan)]
    if not sources:
        lines.append('No sources selected.')
    if plan is None:
        lines.append('Choose Review Moves to calculate proposed Parts counts. Nothing has been applied or saved.')
    else:
        if plan.expanded:
            lines.append('%d assigned Destination storages proposed for 120 cells.' % len(plan.expanded))
        if not plan.changed:
            lines.append('No app-data changes are proposed.')
        lines.append('Proposed moves only. Nothing has been applied or saved.')
    return '\n'.join(lines)


# review_html: Escape every line and bold only footer notices, keeping transfer rows normal weight.
def review_html(context, sources, routes, labels, plan=None):
    lines = review_text(context, sources, routes, labels, plan).split('\n')
    paragraphs = []  # Each transfer stays one paragraph so only its first visual line has an arrow.
    for line in lines:
        content = escape(line)  # Protect names containing HTML, quotes, ampersands or angle brackets.
        if not line.startswith('-> '):
            content = '<b>' + content + '</b>'  # Only end-of-review messages receive emphasis.
        paragraphs.append('<p style="margin:0; white-space:pre-wrap">' + content + '</p>')
    return ''.join(paragraphs)
