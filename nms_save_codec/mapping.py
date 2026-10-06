# File: mapping.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\mapping.py
# Purpose: JSON key de/obfuscation ported from libNOM.map (GPLv3); mapping data comes from MBINCompiler.

from __future__ import annotations

import json
import os

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/mapping]"
# Non-error debug stays behind this flag; errors always raise.
DEBUG_ENABLED = False

# Bundled mapping file (pinned MBINCompiler release) shipped with the package.
BUNDLED_MAPPING_FILE = "mapping_data/mapping.json"
# Bundled legacy keys that newer MBINCompiler releases dropped (from libNOM.map Resources).
BUNDLED_LEGACY_FILE = "mapping_data/mapping_legacy.json"
# Root property name that separates save keys (before it) from account keys (from it on).
ACCOUNT_SPLIT_VALUE = "UserSettingsData"
# The single known obfuscated key with two plaintext meanings (libNOM.map _mapOfCollision).
COLLISION_OBFUSCATED = "NE3"
# The collision's special meaning, only valid under the path hint below.
COLLISION_DEOBFUSCATED = "AllowedToBePurpleWithoutAccess"
# Substring that decides which of the two collision meanings applies.
COLLISION_PATH_HINT = "SolarSystemAttributes"


# Function: _split_at_element
# Purpose: Split mapping pairs into save and account halves at the UserSettingsData entry.
def _split_at_element(pairs: list, value: str) -> list:
    # Find the first pair whose plaintext (Value) equals the split marker.
    index = next((i for i, pair in enumerate(pairs) if pair[1] == value), None)
    # When the marker exists, everything before it is save data and the rest is account data.
    if index is not None:
        # Mirrors libNOM.map SplitAtElement: Take(Index)=save, Skip(Index)=account.
        return [(pairs[:index], False), (pairs[index:], True)]
    # Without the marker the whole list is added once per direction, like libNOM.map does.
    return [(pairs, False), (pairs, True)]


# Function: _setdefault_first
# Purpose: Insert into a dict so the first occurrence wins, matching C# FirstOrDefault.
def _setdefault_first(target: dict, key: str, value: str) -> None:
    # Only write when the key is not present yet; later duplicates are ignored.
    target.setdefault(key, value)


# Class: KeyMapping
# Purpose: Loads mapping data and renames JSON keys in both directions.
class KeyMapping:
    # Debug prefix required by Bill's code standards (class-level constant).
    DEBUG_PREFIX = "[BBB-NMS-SFM/KeyMapping]"

    # Function: __init__
    # Purpose: Load bundled (or external override) mapping data and build the lookup maps.
    def __init__(self, mapping_path: str | None = None, legacy_path: str | None = None):
        # Resolve bundled files relative to this module so any working directory works.
        base = os.path.dirname(os.path.abspath(__file__))
        # An explicit external file always wins so a drop-in update never needs a repackage.
        self.mapping_path = mapping_path if mapping_path and os.path.isfile(mapping_path) else os.path.join(base, BUNDLED_MAPPING_FILE)
        # Legacy keys have no external override; they ship pinned with the package.
        self.legacy_path = legacy_path if legacy_path and os.path.isfile(legacy_path) else os.path.join(base, BUNDLED_LEGACY_FILE)
        # Version string of the mapping data, taken from the file itself.
        self.version = None
        # Build every map once here; data files are small so lazy loading buys nothing.
        self._build()

    # Function: _read_pairs
    # Purpose: Read one mapping JSON file and return its version plus Key/Value pairs.
    def _read_pairs(self, path: str) -> tuple:
        # Open with UTF-8 because the file contains only ASCII but be explicit anyway.
        with open(path, "r", encoding="utf-8") as handle:
            # Parse the whole document in one call.
            document = json.load(handle)
        # libMBIN_version identifies which MBINCompiler release produced the data.
        version = document.get("libMBIN_version", "")
        # MBINCompiler serializes each pair as {"Key": obfuscated, "Value": plaintext}.
        pairs = [(entry["Key"], entry["Value"]) for entry in document.get("Mapping", [])]
        # Hand both pieces back to the caller.
        return version, pairs

    # Function: _build
    # Purpose: Construct the direction-specific lookup maps exactly like libNOM.map CreateMap.
    def _build(self) -> None:
        # The main map is the pinned MBINCompiler release (or the external override).
        version, pairs = self._read_pairs(self.mapping_path)
        # Keep the version for display and update checks.
        self.version = version
        # Legacy keys are always added on top so older saves keep working.
        _, legacy_pairs = self._read_pairs(self.legacy_path)
        # libNOM.map adds compiler + legacy with both directions and account support.
        combined = pairs + legacy_pairs
        # Split once into save/account halves; the split point is shared by both directions.
        halves = _split_at_element(combined, ACCOUNT_SPLIT_VALUE)
        # Four first-wins dicts: one per direction and per data family.
        self._deobf_save: dict = {}
        self._deobf_account: dict = {}
        self._obf_save: dict = {}
        self._obf_account: dict = {}
        # All plaintext candidates per obfuscated key, needed to resolve the NE3 collision.
        self._deobf_all_save: dict = {}
        self._deobf_all_account: dict = {}
        # Process each half into the six maps.
        for data, use_account in halves:
            # Register every pair into the maps for this family.
            self._add_to_maps(data, use_account)

    # Function: _add_to_maps
    # Purpose: Add one family's pairs into the first-wins maps and candidate lists.
    def _add_to_maps(self, data: list, use_account: bool) -> None:
        # Pick the target dicts for this family up front for a tight loop.
        deobf = self._deobf_account if use_account else self._deobf_save
        obf = self._obf_account if use_account else self._obf_save
        deobf_all = self._deobf_all_account if use_account else self._deobf_all_save
        # Walk every (obfuscated, plaintext) pair in file order.
        for obfuscated, plaintext in data:
            # First occurrence wins, exactly like C# FirstOrDefault over the map list.
            _setdefault_first(deobf, obfuscated, plaintext)
            # The reverse direction looks plaintext up, so swap key and value.
            _setdefault_first(obf, plaintext, obfuscated)
            # Keep every candidate for the collision resolution.
            deobf_all.setdefault(obfuscated, []).append(plaintext)

    # Function: _maps_for
    # Purpose: Return the map pair (deobf, deobf_all) for the requested family.
    def _maps_for(self, use_account: bool) -> tuple:
        # Account data and save data use different key families.
        if use_account:
            # Account maps.
            return self._deobf_account, self._deobf_all_account
        # Save maps.
        return self._deobf_save, self._deobf_all_save

    # Function: obf_map_for
    # Purpose: Return the plaintext-to-obfuscated map for the requested family.
    def obf_map_for(self, use_account: bool) -> dict:
        # Account data and save data use different key families.
        return self._obf_account if use_account else self._obf_save

    # Function: deobfuscate
    # Purpose: Rename every obfuscated key in a parsed JSON tree to its plaintext name.
    def deobfuscate(self, node, use_account: bool = False) -> tuple:
        # Grab the maps for this family once.
        deobf, deobf_all = self._maps_for(use_account)
        # Collect keys the table does not know so the caller can report them.
        unknown_keys: set = set()
        # Run the recursive rename pass; path starts empty at the root.
        result = self._walk_deobfuscate(node, deobf, deobf_all, unknown_keys, "")
        # Hand back the renamed tree plus the unknown key report.
        return result, unknown_keys

    # Function: _walk_deobfuscate
    # Purpose: Recursively rebuild one JSON node with mapped key names (max ~20 lines per standards).
    def _walk_deobfuscate(self, node, deobf: dict, deobf_all: dict, unknown_keys: set, path: str) -> object:
        # Dicts get their keys renamed; lists get their elements walked.
        if isinstance(node, dict):
            # Rebuild in the same order so serialization stays byte-stable.
            rebuilt = {}
            # One child at a time keeps the function short and the logic obvious.
            for key, value in node.items():
                # Child path for collision checks, matching JProperty.Path substring semantics.
                child_path = f"{path}.{key}" if path else key
                # Map the key (or leave it when unknown).
                mapped = self._map_key(key, child_path, deobf, deobf_all)
                # A mapped key is known; an unmapped one may be unknown.
                if mapped == key and key not in deobf:
                    # Only keys that are neither obfuscated names nor plaintext targets count as unknown.
                    if key not in self._plaintext_targets(deobf):
                        unknown_keys.add(key)
                # Recurse into the value with the possibly renamed path.
                rebuilt[mapped] = self._walk_deobfuscate(value, deobf, deobf_all, unknown_keys, child_path)
            # Return the rebuilt dict.
            return rebuilt
        # Lists are walked element by element without path changes.
        if isinstance(node, list):
            # Recurse per element, preserving order.
            return [self._walk_deobfuscate(item, deobf, deobf_all, unknown_keys, path) for item in node]
        # Scalars pass through untouched.
        return node

    # Function: _plaintext_targets
    # Purpose: Return the set of plaintext names for the unknown-key check.
    def _plaintext_targets(self, deobf: dict) -> set:
        # Values of the deobfuscation map are the plaintext targets.
        return set(deobf.values())

    # Function: _map_key
    # Purpose: Resolve one obfuscated key, honoring the single known collision.
    def _map_key(self, key: str, path: str, deobf: dict, deobf_all: dict) -> str:
        # The collision key has two meanings depending on where it appears.
        if key == COLLISION_OBFUSCATED and key in deobf_all:
            # Under SolarSystemAttributes it means the special purple attribute.
            if COLLISION_PATH_HINT in path:
                # Return the collision meaning when the path matches.
                return COLLISION_DEOBFUSCATED
            # Otherwise return the other (normal) meaning, i.e. the first non-collision candidate.
            others = [value for value in deobf_all[key] if value != COLLISION_DEOBFUSCATED]
            # Prefer the first other candidate, exactly like the C# FirstOrDefault.
            return others[0] if others else deobf.get(key, key)
        # Default lookup: first mapping for this obfuscated key.
        return deobf.get(key, key)

    # Function: obfuscate
    # Purpose: Rename every plaintext key in a tree back to its obfuscated form.
    def obfuscate(self, node, use_account: bool = False) -> object:
        # Grab the reverse map for this family once.
        obf = self.obf_map_for(use_account)
        # Run the recursive reverse rename pass.
        return self._walk_obfuscate(node, obf)

    # Function: _walk_obfuscate
    # Purpose: Recursively rebuild one JSON node with obfuscated key names.
    def _walk_obfuscate(self, node, obf: dict) -> object:
        # Dicts get keys renamed; lists get elements walked.
        if isinstance(node, dict):
            # Rebuild in the same order so serialization stays byte-stable.
            rebuilt = {}
            # Rename each key through the reverse map, leaving unknown keys untouched.
            for key, value in node.items():
                # Reverse lookup: plaintext -> obfuscated, first occurrence wins.
                rebuilt[obf.get(key, key)] = self._walk_obfuscate(value, obf)
            # Return the rebuilt dict.
            return rebuilt
        # Lists are walked element by element.
        if isinstance(node, list):
            # Recurse per element, preserving order.
            return [self._walk_obfuscate(item, obf) for item in node]
        # Scalars pass through untouched.
        return node

    # Function: input_uses_obfuscated_keys
    # Purpose: Detect whether a parsed root object still uses obfuscated keys.
    def input_uses_obfuscated_keys(self, root: dict, use_account: bool = False) -> bool:
        # Grab the forward map for this family.
        deobf, _ = self._maps_for(use_account)
        # The obfuscated root carries at least one known obfuscated key (e.g. F2P for Version).
        return any(key in deobf for key in root.keys())
