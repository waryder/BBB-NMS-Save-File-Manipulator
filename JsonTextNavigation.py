# File: JsonTextNavigation.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\JsonTextNavigation.py
# Purpose: Read-only structural navigation from tree nodes to actual displayed JSON.
import copy  # Retain independent tree-build data, never a reference to editable save data.
from decimal import Decimal, InvalidOperation  # Preserve source-number precision without mutating float-based model data.
import json  # Delegate JSON string escape handling to Python's strict scanner.
import math  # Reject non-finite numbers unsupported by standard JSON.
import re  # Recognize only the JSON number grammar.
from PyQt5.QtCore import Qt  # Reserve a role separate from existing node data.

QT_DATA_JSON_LOCATION = Qt.UserRole + 3  # Explicit typed path plus key/value target.
NODE_DATA_ROLE = Qt.UserRole  # Existing tuple/container/scalar representation.
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')  # Standard JSON numbers.

class JsonNavigationError(ValueError):
    # Controlled navigation failure; callers leave the cursor and all data unchanged.
    pass

# same_json: compare structures without bool/number coercion or dictionary-order sensitivity.
def same_json(left, right):
    if type(left) in (Decimal, float) and type(right) in (Decimal, float) and Decimal in (type(left), type(right)):  # Source decimals versus model floats.
        return Decimal(str(left)) == Decimal(str(right))  # Compare exact source numbers with the model's displayed JSON representation.
    if type(left) is not type(right):  # Conservatively require the same scalar/container types.
        return False  # A valid path alone does not establish correspondence.
    if isinstance(left, dict):  # JSON object layout/order is not identity.
        return left.keys() == right.keys() and all(same_json(left[key], right[key]) for key in left)  # Compare contents.
    if isinstance(left, list):  # Array order and every occurrence are identity.
        return len(left) == len(right) and all(same_json(a, b) for a, b in zip(left, right))  # Compare in order.
    return left == right  # Compare exact scalar values.

class JsonSourceMap:
    # __init__: parse actual source and retain key/value offsets by exact typed path.
    def __init__(self, text):
        self.text = text  # Never substitute regenerated JSON for the displayed text.
        self.offset = 0  # Python code-point offset during parsing.
        self.values = {}  # Value starts, including empty containers.
        self.keys = {}  # Property key starts, distinct from value starts.
        try:
            self.data = self._value(())  # Parse the full root and all its descendants.
            self._space()  # Allow trailing standard JSON whitespace only.
            if self.offset != len(text):  # Reject multiple roots and trailing junk.
                raise JsonNavigationError('The text contains trailing data after JSON.')  # Controlled refusal.
        except (ValueError, RecursionError, OverflowError, InvalidOperation) as error:  # Normalize scanner/depth/exact-decimal failures.
            raise JsonNavigationError('The text is not unambiguous supported JSON: ' + str(error)) from error  # Explain.

    # _space: skip only whitespace allowed by the JSON specification.
    def _space(self):
        while self.offset < len(self.text) and self.text[self.offset] in ' \t\r\n':  # Actual source layout.
            self.offset += 1  # Advance without changing the document.

    # _expect: consume one punctuation character after optional JSON whitespace.
    def _expect(self, character):
        self._space()  # Ignore formatting, not content.
        if self.text[self.offset:self.offset + 1] != character:  # Missing/incorrect delimiter.
            raise JsonNavigationError('Expected JSON delimiter ' + character)  # Do not guess.
        self.offset += 1  # Consume exactly the delimiter.

    # _string: decode escaped quotes, backslashes, Unicode and newline escapes correctly.
    def _string(self):
        self._expect('"')  # Confirm the opening string delimiter.
        value, self.offset = json.decoder.scanstring(self.text, self.offset, True)  # Strict standard scanner.
        return value  # Return decoded identity with source offset retained separately.

    # _value: dispatch containers/scalars and record their exact opening position.
    def _value(self, path):
        self._space()  # Value starts after any valid layout whitespace.
        self.values[path] = self.offset  # Record before consuming any token.
        character = self.text[self.offset:self.offset + 1]  # Safe even at unexpected EOF.
        if character == '{':  # Object values need property identity.
            return self._object(path)  # Recurse with exact string keys.
        if character == '[':  # Arrays need occurrence identity.
            return self._array(path)  # Recurse with integer indexes.
        if character == '"':  # Strings may contain apparent structural punctuation.
            return self._string()  # Scanner never interprets punctuation inside strings.
        return self._scalar()  # Parse standard numbers, booleans and null.

    # _scalar: consume standard JSON primitive tokens, rejecting NaN/Infinity and malformed numbers.
    def _scalar(self):
        for token, value in (('true', True), ('false', False), ('null', None)):  # Standard literals only.
            if self.text.startswith(token, self.offset):  # Check at this exact position.
                self.offset += len(token)  # Parent/root parsing validates the next delimiter.
                return value  # Preserve primitive type.
        match = NUMBER.match(self.text, self.offset)  # Recognize a number at the current position.
        if not match:  # Includes empty input and nonstandard constants.
            raise JsonNavigationError('Expected a JSON value.')  # Refuse unsupported input.
        self.offset = match.end()  # Retain actual source endpoint.
        value = json.loads(match.group(), parse_float=Decimal)  # Keep every decimal digit; do not collapse distinct edits through float rounding.
        if isinstance(value, Decimal) and not math.isfinite(float(value)):  # Preserve the application's finite-float range restriction.
            raise JsonNavigationError('Non-finite numbers are unsupported.')  # Controlled refusal.
        return value  # Preserve parsed primitive.

    # _object: parse members, recording property beginnings and rejecting duplicate decoded keys.
    def _object(self, path):
        self._expect('{')  # Consume container opening.
        output = {}  # Independent parsed structure for correspondence checks.
        self._space()  # Empty objects can occupy one line or many.
        if self.text[self.offset:self.offset + 1] == '}':  # Empty object.
            self.offset += 1  # Consume closing brace.
            return output  # Opening offset already recorded.
        while True:  # Parse each exact member occurrence.
            self._space()  # Key may begin on a different line from its value.
            start = self.offset  # Key source position, including its opening quote.
            key = self._string()  # Decode identity independently of decorated tree labels.
            if key in output:  # Duplicate keys make structural matching ambiguous.
                raise JsonNavigationError('Duplicate JSON object keys are unsupported.')  # Refuse first-match behavior.
            child_path = path + (key,)  # String-key segment remains distinct from integer indexes.
            self.keys[child_path] = start  # Property/tuple and key nodes target this beginning.
            self._expect(':')  # Confirm member separator.
            output[key] = self._value(child_path)  # Value/container nodes target their own start.
            if self._end_or_comma('}'):  # Consume closing delimiter or next-member separator.
                return output  # Return parsed object.

    # _array: parse values in order, retaining distinct positions for identical repeated entries.
    def _array(self, path):
        self._expect('[')  # Consume array opening.
        output = []  # Array order is part of correspondence.
        self._space()  # Whitespace has no bearing on indexes.
        if self.text[self.offset:self.offset + 1] == ']':  # Empty array.
            self.offset += 1  # Consume closing bracket.
            return output  # Opening position is still available.
        while True:  # Each member has its own integer index.
            output.append(self._value(path + (len(output),)))  # Never search for repeated values.
            if self._end_or_comma(']'):  # Consume end or prepare the next value.
                return output  # Return exact ordered data.

    # _end_or_comma: validate the container delimiter without accepting trailing commas.
    def _end_or_comma(self, end):
        self._space()  # Accept formatting around punctuation.
        if self.text[self.offset:self.offset + 1] == end:  # Container is complete.
            self.offset += 1  # Consume closing punctuation.
            return True  # Stop the member loop.
        self._expect(',')  # Any other token must be a member separator.
        return False  # Next iteration must parse a real key/value, not a trailing comma.

    # qt_position: translate Python code-point offsets to Qt's UTF-16 cursor coordinate.
    def qt_position(self, path, kind):
        positions = self.keys if kind == 'key' else self.values  # Explicit node target rule.
        if kind not in ('key', 'value') or path not in positions:  # Never accept a missing location.
            raise JsonNavigationError('This tree location is missing from the displayed JSON.')  # Explain.
        prefix = self.text[:positions[path]]  # Count the actual displayed prefix only.
        return len(prefix.encode('utf-16-le', errors='surrogatepass')) // 2  # Non-BMP characters occupy two units.

class TreeJsonNavigation:
    # __init__: invalidate locations on every real tree data/structure change, including blocked widget signals.
    def __init__(self, tree):
        self.valid = False  # No location is trustworthy until a complete build is captured.
        self.capturing = False  # Metadata writes are not user tree edits.
        self.snapshot = None  # Independent, complete tree-build data.
        self.error = 'The tree has no reliable JSON locations yet.'  # Controlled initial explanation.
        model = tree.model()  # Internal Qt model signals survive tree.blockSignals(True).
        for signal in (model.dataChanged, model.rowsInserted, model.rowsRemoved, model.rowsMoved,
                       model.modelReset, model.layoutChanged):  # Cover edit/reorder/delete/rebuild flows.
            signal.connect(self.invalidate)  # Do not infer validity from the sync LED.

    # invalidate: reject stale paths until a supported tree rebuild records fresh ones.
    def invalidate(self, *args):
        if not self.capturing:  # Ignore only our metadata assignments during a verified build.
            self.valid = False  # Even identical-entry reordering must not reuse old occurrence paths.
            self.error = 'The tree changed since its locations were built; rebuild it before highlighting.'  # No repair.

    # capture: attach explicit locations after a builder finishes, validating its artificial hierarchy.
    def capture(self, tree, data):
        self.valid = False  # A partial or failed capture is never navigable.
        self.capturing = True  # Suppress invalidation caused by this feature's metadata writes.
        try:
            if tree.topLevelItemCount() != 1:  # All four tab builders have one JSON-root node.
                raise JsonNavigationError('The tree does not have one supported JSON root.')  # Refuse unsupported layout.
            reconstructed = self._node(tree.topLevelItem(0), ())  # Attach paths from structural node data.
            if not same_json(reconstructed, data):  # Verify builder contents before trusting its paths.
                raise JsonNavigationError('The tree does not correspond to its source JSON.')  # No guessing.
            self.snapshot = copy.deepcopy(data)  # Decouple from later model/retained-save mutations.
            self.valid = True  # Only a complete, matching capture enables navigation.
        except (JsonNavigationError, RecursionError, RuntimeError) as error:  # Unsupported/deleted/deep nodes.
            self.error = str(error)  # Handler reports this instead of crashing or modifying data.
        finally:
            self.capturing = False  # Always restore real-edit invalidation.

    # _tag: store typed path segments and whether the target begins at a key or value.
    def _tag(self, node, path, kind):
        node.setData(0, QT_DATA_JSON_LOCATION, {'path': list(path), 'kind': kind})  # Metadata only, not model data.

    # _node: map list/object/scalar nodes without inspecting labels or flattening the tuple hierarchy.
    def _node(self, node, path):
        data = node.data(0, NODE_DATA_ROLE)  # Existing structural marker/value.
        self._tag(node, path, 'value')  # Containers/scalars always target their value start.
        if isinstance(data, list):  # Children are array values in their actual order.
            return [self._node(node.child(index), path + (index,)) for index in range(node.childCount())]  # Exact occurrence.
        if isinstance(data, dict):  # Children are artificial property tuples, not plain JSON nodes.
            return self._members(node, path)  # Handle key/value children explicitly.
        if isinstance(data, tuple) or node.childCount():  # Tuples only belong under object members.
            raise JsonNavigationError('Unsupported tree value representation.')  # Refuse unknown hierarchy.
        return data  # Primitive value used to verify correspondence.

    # _members: map property tuples/key children to keys and value children to their own values.
    def _members(self, node, path):
        output = {}  # Reconstruct only for validation, never write back to the editable model.
        for index in range(node.childCount()):  # Preserve actual member identity.
            member = node.child(index)  # Property tuple node.
            if not isinstance(member.data(0, NODE_DATA_ROLE), tuple) or member.childCount() != 2:  # Exact known shape.
                raise JsonNavigationError('Unsupported tree property representation.')  # Refuse ambiguous shape.
            key_node = member.child(0)  # Explicit key child; labels may be decorated.
            key = key_node.data(0, NODE_DATA_ROLE)  # Identity is stored structural data.
            if not isinstance(key, str) or key in output or key_node.childCount():  # Standard unique JSON keys.
                raise JsonNavigationError('Unsupported or duplicate tree property keys.')  # Never pick the first occurrence.
            child_path = path + (key,)  # Preserve string key type.
            self._tag(member, child_path, 'key')  # Tuple/property begins at the property key.
            self._tag(key_node, child_path, 'key')  # Key child shares property start.
            output[key] = self._node(member.child(1), child_path)  # Scalar/container child targets value.
        return output  # Compare whole tree contents with its build source.

    # resolve: require whole-tree/text correspondence before returning an exact Qt cursor position.
    def resolve(self, tree, item, text):
        if not self.valid:  # Tree mutations/reorders invalidate every stored path.
            raise JsonNavigationError(self.error)  # Caller leaves selection/data unchanged.
        if item is None or item.treeWidget() is not tree:  # Detached/foreign nodes cannot be trusted.
            raise JsonNavigationError('This node no longer belongs to the current tree.')  # Controlled refusal.
        location = item.data(0, QT_DATA_JSON_LOCATION)  # Use explicit path, never predicted line metadata.
        if not isinstance(location, dict) or set(location) != {'path', 'kind'}:  # Missing/malformed metadata.
            raise JsonNavigationError('This node has no reliable structural JSON location.')  # Explain.
        if not isinstance(location['path'], list) or any(type(segment) not in (str, int) for segment in location['path']):  # Typed path.
            raise JsonNavigationError('This node has an unsupported JSON path.')  # Refuse ambiguous identity.
        source = JsonSourceMap(text)  # Parse fresh actual text every invocation; no stale offset cache.
        if not same_json(source.data, self.snapshot):  # Formatting is allowed; any content/order change is not.
            raise JsonNavigationError('The tree and text contain different data; a reliable match cannot be made.')  # No auto-sync.
        return source.qt_position(tuple(location['path']), location['kind'])  # Exact occurrence, UTF-16 coordinate.
