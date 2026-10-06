# File: selftest.py
# Purpose: Round-trip smoke test for the NmsSaveFile class against a directory of live save copies.
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\selftest.py
#
# Usage (from the repo root, NEVER against the live save directory):
#   python -m nms_save_codec.selftest <path-to-COPY-of-a-save-directory>
#
# This is the "step 2 smoke test" from the post-NMS-update procedure: it either
# passes (nothing to do) or fails loudly with a named error (format drifted).

from __future__ import annotations

import json
import os
import struct
import sys
import tempfile

from .platforms import get_platform
from .save_file import NmsSaveFile
from .xxtea import decrypt_meta

# Debug prefix required by Bill's code standards.
DEBUG_PREFIX = "[BBB-NMS-SFM/selftest]"


# Function: _first_root_key
# Purpose: Small helper that reports a key found in the root, for the log line.
def _first_root_key(tree: dict, candidates: list) -> str:
    # Walk the candidate list and return the first one present.
    for name in candidates:
        # Present means found.
        if name in tree:
            # Report it.
            return name
    # None of the candidates exist.
    return "<none>"


# Function: test_save_round_trip
# Purpose: Full decode -> deobfuscate -> obfuscate -> encode -> decode cycle for one .hg pair.
def test_save_round_trip(save_dir: str, data_name: str, results: list) -> None:
    # Full path to the data file under test.
    data_path = os.path.join(save_dir, data_name)
    # Skip files that were not staged for the test.
    if not os.path.isfile(data_path):
        # Nothing to test; note it and move on.
        results.append((data_name, "SKIP", "file not present"))
        # Done with this name.
        return
    # Load the save with its mf_ sibling when one exists.
    obj = NmsSaveFile(platform="steam").load_file(data_path)
    # Decode with readable keys.
    tree = obj.decode(deobfuscate_keys=True)
    # The deobfuscated save root must carry the well-known plaintext keys.
    version_key = _first_root_key(tree, ["Version"])
    # Root plaintext Version is the strongest signal the mapping worked.
    ok = version_key == "Version"
    # A save must also expose its BaseContext (what the GUI imports today).
    ok = ok and "BaseContext" in tree
    # Round-trip: encode the tree back to disk bytes.
    encoded = obj.encode()
    # Re-decode the encoded bytes through a fresh instance to avoid shared state.
    again = NmsSaveFile(platform="steam")
    # The temp file keeps the source basename so filename-based account/slot detection stays correct.
    tmp_dir = tempfile.mkdtemp()
    # Full temp path under the preserved name.
    tmp_path = os.path.join(tmp_dir, data_name)
    try:
        # Write the encoded payload.
        with open(tmp_path, "wb") as tmp:
            # One write of the full payload.
            tmp.write(encoded)
        # Load the temp file and decode with the same rename pass, so both sides compare plaintext.
        tree2 = again.load_file(tmp_path).decode(deobfuscate_keys=True)
    finally:
        # Always clean the temp directory up.
        os.unlink(tmp_path)
        # Remove the now-empty directory too.
        os.rmdir(tmp_dir)
    # The round-tripped tree must be semantically identical to the original.
    same = json.loads(json.dumps(tree2)) == json.loads(json.dumps(tree))
    # Both conditions must hold for a pass.
    results.append((data_name, "PASS" if (ok and same) else "FAIL", f"Version={version_key} BaseContext={'BaseContext' in tree} roundtrip={same} unknown_keys={len(obj.unknown_keys)}"))


# Function: test_account_round_trip
# Purpose: Decode -> encode -> decode cycle for accountdata.hg (plain JSON, account key family).
def test_account_round_trip(save_dir: str, results: list) -> None:
    # Standard account data filename.
    data_path = os.path.join(save_dir, "accountdata.hg")
    # Skip when the account file was not staged.
    if not os.path.isfile(data_path):
        # Nothing to test.
        results.append(("accountdata.hg", "SKIP", "file not present"))
        # Done.
        return
    # Load the account file (no mf_ sibling needed for the cycle test).
    obj = NmsSaveFile(platform="steam").load_file(data_path)
    # Decode with readable keys using the account key family.
    tree = obj.decode(deobfuscate_keys=True)
    # Encode the account tree back to disk bytes (uncompressed form).
    encoded = obj.encode()
    # Decode the encoded bytes again in-process.
    again = NmsSaveFile(platform="steam")
    # The temp file keeps the accountdata.hg name so account detection works on reload.
    tmp_dir = tempfile.mkdtemp()
    # Full temp path under the preserved name.
    tmp_path = os.path.join(tmp_dir, "accountdata.hg")
    try:
        # Write the payload.
        with open(tmp_path, "wb") as tmp:
            # One write of the full payload.
            tmp.write(encoded)
        # Load and decode the re-encoded account file with the same rename pass.
        tree2 = again.load_file(tmp_path).decode(deobfuscate_keys=True)
    finally:
        # Clean the temp directory up.
        os.unlink(tmp_path)
        # Remove the now-empty directory too.
        os.rmdir(tmp_dir)
    # Semantic equality closes the loop.
    same = tree2 == tree
    # Report the account result.
    results.append(("accountdata.hg", "PASS" if same else "FAIL", f"roundtrip={same} unknown_keys={len(obj.unknown_keys)}"))


# Function: test_meta_patch
# Purpose: Patch sizes in a decrypted mf_ meta, re-encrypt, decrypt again, and verify.
def test_meta_patch(save_dir: str, results: list) -> None:
    # Standard first-slot meta filename.
    meta_path = os.path.join(save_dir, "mf_save.hg")
    # Skip when the meta was not staged.
    if not os.path.isfile(meta_path):
        # Nothing to test.
        results.append(("mf_save.hg", "SKIP", "file not present"))
        # Done.
        return
    # Load save.hg so its meta sibling decrypts along with it.
    obj = NmsSaveFile(platform="steam").load_file(os.path.join(save_dir, "save.hg"))
    # Meta must have been loaded by the sibling guess.
    if obj._meta_plain is None:
        # Loud failure with context.
        results.append(("mf_save.hg", "FAIL", "meta sibling not loaded"))
        # Done.
        return
    # Patch the sizes and re-encrypt for the same slot.
    meta_out = obj.encode_meta()
    # Decrypt the re-encrypted meta with the same slot hint.
    plain_out, slot = decrypt_meta(meta_out, obj._meta_slot, is_account=False)
    # The patched decompressed size must match the last encoded payload length.
    patched = struct.unpack_from("<I", plain_out, 0x38)[0]
    # Compare against the payload the class just encoded.
    ok = patched == len(obj._last_plain_payload)
    # Report the meta result.
    results.append(("mf_save.hg", "PASS" if ok else "FAIL", f"slot={slot} size_decompressed=0x{patched:X} expected=0x{len(obj._last_plain_payload):X}"))


# Function: test_platform_stubs
# Purpose: Confirm unimplemented platforms fail loudly instead of pretending to work.
def test_platform_stubs(results: list) -> None:
    # Try each stub name; every one must raise NotImplementedError.
    for name in ("switch", "playstation", "microsoft"):
        try:
            # Request the stub platform.
            get_platform(name)
            # Getting here means the stub silently succeeded - a bug.
            results.append((f"platform:{name}", "FAIL", "stub did not raise"))
        except NotImplementedError:
            # The loud failure is exactly what we want.
            results.append((f"platform:{name}", "PASS", "raises NotImplementedError"))
        except Exception as exc:  # noqa: BLE001 - selftest reports every failure mode
            # Any other exception type is a bug in the seam.
            results.append((f"platform:{name}", "FAIL", f"wrong exception: {exc}"))


# Function: run
# Purpose: Execute every test group against the supplied save directory copy.
def run(save_dir: str) -> int:
    # Result rows: (test name, status, detail).
    results: list = []
    # Both live save slots that were staged.
    for name in ("save.hg", "save2.hg"):
        # Round-trip each slot.
        test_save_round_trip(save_dir, name, results)
    # Account data cycle.
    test_account_round_trip(save_dir, results)
    # Meta patch cycle.
    test_meta_patch(save_dir, results)
    # Platform stub behavior.
    test_platform_stubs(results)
    # Print the report table.
    print(f"{DEBUG_PREFIX} run: NmsSaveFile self-test against {save_dir}")
    # One line per result.
    for name, status, detail in results:
        # Aligned columns keep the output readable.
        print(f"  [{status:4}] {name:22} {detail}")
    # Any FAIL means a nonzero exit code for scripted use.
    failed = any(status == "FAIL" for _, status, _ in results)
    # Exit code 1 on failure so scheduled runs can detect it.
    return 1 if failed else 0


# Function: main
# Purpose: CLI entry so the self-test runs as a module from the repo root.
def main() -> None:
    # A missing argument is a usage error, not a crash.
    if len(sys.argv) != 2:
        # Explain the usage clearly.
        print(f"usage: python -m nms_save_codec.selftest <save-directory-COPY>")
        # Exit with a usage error code.
        sys.exit(2)
    # Run the whole suite and propagate the exit code.
    sys.exit(run(sys.argv[1]))


# Run as a module: python -m nms_save_codec.selftest <dir>
if __name__ == "__main__":
    main()
