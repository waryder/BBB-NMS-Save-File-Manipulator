# File: README.md
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\nms_save_codec\README.md
# Purpose: How to use the first-cut Steam/GOG encode/decode library and CLI.

# nms_save_codec (first cut)

Python port of the **Steam / GOG** encode/decode path in [libNOM.io](https://github.com/waryder/libNOM.io).

**License: GNU GPLv3.** libNOM.io is GPLv3, not MIT. This package copies that
logic and is therefore a derivative work under GPLv3.

## NmsSaveFile class (release candidate)

`save_file.py` adds a self-contained class on top of the codec functions. It
decodes `.hg` files straight into editable Python dicts - including JSON key
deobfuscation - and encodes them back into game-ready bytes:

```python
from nms_save_codec import NmsSaveFile

obj = NmsSaveFile(platform="steam").load_file(r"P:\...\st_76561199060525572\save.hg")
tree = obj.decode()            # readable key names ("Version", "BaseContext", ...)
# ... edit the dict ...
written = obj.write_to(r"P:\some\output\dir")   # save.hg + mf_save.hg, sizes patched
```

- Key mapping data comes from MBINCompiler `mapping.json` (the ONE hard,
  per-NMS-update dependency). A pinned copy ships in `mapping_data/`; drop a
  newer `mapping.json` next to the package files to override it without
  repackaging.
- Platforms are routed through `platforms.py`: Steam and GOG are implemented;
  Switch / PlayStation / Microsoft are stubs that raise with a clear message.
- `python -m nms_save_codec.selftest <dir-with-COPIES-of-saves>` runs the
  round-trip smoke test. NEVER point it at the live save directory.

## What it does

| File | Operation | What actually happens |
|---|---|---|
| `save.hg`, `save2.hg`, … | decrypt / encrypt | LZ4 streaming chunks (`E5 A1 ED FE`). **Not encrypted.** |
| `accountdata.hg` | decrypt / encrypt | Uncompressed JSON (identity + trailing NUL). |
| `mf_save*.hg`, `mf_accountdata.hg` | decrypt / encrypt | XXTEA on 32-bit words. Key `NAESEVADNAYRTNRG` + slot mix. |

Not in this cut: JSON key deobfuscation (`libNOM.map`), PlayStation `memory.dat`,
Switch, Microsoft Store, SpookyHash rewrite of old META_FORMAT_1.

## Install the one extra dependency

```
pip install lz4
```

The rest of the codec is stdlib.

## CLI (writes stdout — pipe to a file)

From the manipulator repo root:

```
python nms_save_codec_cli.py --decrypt save.hg > save.json
python nms_save_codec_cli.py --decrypt --pretty save.hg > save.pretty.json
python nms_save_codec_cli.py --encrypt --kind data save.json > save.repacked.hg

python nms_save_codec_cli.py --decrypt --kind meta mf_save.hg > mf_save.bin
python nms_save_codec_cli.py --encrypt --kind meta --slot 2 mf_save.bin > mf_save.repacked.hg
```

`--info` prints detection to **stderr** so it does not pollute the pipe.

Slots (Steam): `1` = accountdata, `2` = `save.hg`, `3` = `save2.hg`, `N+1` = `saveN.hg`.

## Library

```python
from nms_save_codec import decrypt_file, encrypt_file

json_bytes = decrypt_file(r"P:\...\st_76561199060525572\save.hg")
native = encrypt_file("save.json", kind="data")
```

The manipulator GUI still pastes JSON. This package is the next step so it can
open `save*.hg` directly.
