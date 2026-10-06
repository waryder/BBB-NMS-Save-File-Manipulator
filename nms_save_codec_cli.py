# File: nms_save_codec_cli.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec_cli.py
# Purpose: Command-line test harness that encrypts or decrypts to stdout.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nms_save_codec.codec import decrypt_bytes, encrypt_bytes
from nms_save_codec.slots import guess_kind_from_filename, guess_slot_from_filename
from nms_save_codec.streaming import is_streaming_save, looks_like_json

DEBUG_PREFIX = "[BBB-NMS-SFM/nms_save_codec_cli]"
DEBUG_ENABLED = False


# Function: _read_input
# Purpose: Load the source path, or stdin when the path is '-'.
def _read_input(path: str) -> bytes:
    # '-' means the user is piping bytes in.
    if path == "-":
        return sys.stdin.buffer.read()
    # Otherwise read the named file in binary mode.
    return Path(path).read_bytes()


# Function: _write_stdout
# Purpose: Push result bytes to stdout.buffer so the user can pipe to a file.
def _write_stdout(blob: bytes) -> None:
    # Binary stdout avoids the Windows console encoding the JSON.
    sys.stdout.buffer.write(blob)
    # Do not add a trailing newline; the caller asked for pipe-friendly output.


# Function: _maybe_pretty_json
# Purpose: Optionally indent decrypted JSON so a human can review it.
def _maybe_pretty_json(blob: bytes, pretty: bool) -> bytes:
    # Leave binary / non-JSON alone even when --pretty was passed.
    if not pretty or not looks_like_json(blob):
        return blob
    # Parse then dump with 2-space indent; keep Unicode unescaped.
    parsed = json.loads(blob.decode("utf-8"))
    text = json.dumps(parsed, indent=2, ensure_ascii=False)
    # Re-encode as UTF-8 for stdout.buffer.
    return text.encode("utf-8")


# Function: _print_info
# Purpose: Write a short detection summary to stderr (never pollutes the pipe).
def _print_info(path: str, blob: bytes, kind: str, slot: int | None) -> None:
    # Detection goes to stderr so `> out.json` stays clean.
    kind_guess = guess_kind_from_filename(path) if path != "-" else "unknown"
    # Slot guess can fail for '-' / odd names; that is fine for --info.
    try:
        slot_guess = guess_slot_from_filename(path) if path != "-" else None
    except ValueError:
        slot_guess = None
    # Describe the first few bytes so a bad file is obvious.
    head = blob[:16].hex(" ")
    # Streaming vs JSON vs opaque is the main branch the codec cares about.
    shape = "streaming" if is_streaming_save(blob) else ("json" if looks_like_json(blob) else "binary")
    print(
        f"{DEBUG_PREFIX} path={path} bytes={len(blob)} shape={shape} "
        f"kind={kind} kind_guess={kind_guess} slot={slot} slot_guess={slot_guess} head={head}",
        file=sys.stderr,
    )


# Function: build_parser
# Purpose: Define --decrypt / --encrypt and the supporting flags.
def build_parser() -> argparse.ArgumentParser:
    # Epilog shows the two pipe recipes Bill asked for.
    parser = argparse.ArgumentParser(
        prog="nms_save_codec_cli.py",
        description=(
            "First-cut Steam/GOG NMS save codec. Decrypt LZ4 save??.hg or XXTEA "
            "mf_*.hg, or encrypt JSON / plaintext meta back. Writes the result to stdout."
        ),
        epilog=(
            "Examples:\n"
            "  python nms_save_codec_cli.py --decrypt save.hg > save.json\n"
            "  python nms_save_codec_cli.py --encrypt --kind data save.json > save.hg\n"
            "  python nms_save_codec_cli.py --decrypt --kind meta mf_save.hg > mf_save.bin\n"
            "  python nms_save_codec_cli.py --encrypt --kind meta --slot 2 mf_save.bin > mf_save.hg\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Exactly one of encrypt / decrypt must be chosen.
    mode = parser.add_mutually_exclusive_group(required=True)
    # Decrypt: .hg / mf_*.hg -> JSON or plaintext meta.
    mode.add_argument("--decrypt", action="store_true", help="Decode a native save or meta file")
    # Encrypt: JSON / plaintext meta -> native bytes.
    mode.add_argument("--encrypt", action="store_true", help="Encode JSON or plaintext meta to native")
    # Kind defaults to filename sniffing.
    parser.add_argument(
        "--kind",
        choices=("auto", "data", "meta"),
        default="auto",
        help="data = save??.hg LZ4/JSON; meta = mf_*.hg XXTEA; auto = guess from name",
    )
    # Slot is required for meta encrypt when the name is not a Steam filename.
    parser.add_argument(
        "--slot",
        type=int,
        default=None,
        help="StoragePersistentSlotEnum ordinal (2=save.hg, 3=save2.hg, 1=account)",
    )
    # Account files skip LZ4 and use the account key family.
    parser.add_argument(
        "--account",
        action="store_true",
        help="Treat the file as accountdata (no LZ4; account meta key family)",
    )
    # Identity data encode: useful to review the terminated JSON without LZ4.
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="On --encrypt --kind data, skip LZ4 and emit terminated JSON bytes",
    )
    # Pretty-print decrypted JSON to make piping into a reviewer easier.
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="On --decrypt of JSON, indent the object (still written to stdout)",
    )
    # Detection summary on stderr.
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print detection details to stderr before writing stdout",
    )
    # Positional source; '-' reads stdin.
    parser.add_argument("input", help="Source file, or '-' to read stdin")
    return parser


# Function: main
# Purpose: Parse argv, run encrypt or decrypt, write stdout.
def main(argv: list[str] | None = None) -> int:
    # Build and parse the flag set.
    parser = build_parser()
    # argv=None means sys.argv[1:], which is what a console_script wants.
    args = parser.parse_args(argv)
    # Load the source bytes once.
    blob = _read_input(args.input)
    # Optional detection dump (stderr only).
    if args.info:
        _print_info(args.input, blob, args.kind, args.slot)
    # Decrypt path: native -> JSON / plaintext meta.
    if args.decrypt:
        result = decrypt_bytes(
            blob,
            args.kind,
            hint_slot=args.slot,
            is_account=args.account,
            source_name=args.input if args.input != "-" else "",
        )
        # Optional indent for human review.
        result = _maybe_pretty_json(result, args.pretty)
        _write_stdout(result)
        return 0
    # Encrypt path: JSON / plaintext meta -> native.
    result = encrypt_bytes(
        blob,
        args.kind,
        hint_slot=args.slot,
        is_account=args.account,
        source_name=args.input if args.input != "-" else "",
        compress=not args.no_compress,
    )
    _write_stdout(result)
    return 0


# Standard module entry so `python nms_save_codec_cli.py` works from the repo root.
if __name__ == "__main__":
    sys.exit(main())
