# BBB NMS Save File Manipulator

A Windows editor for **No Man's Sky** save files that opens your live Steam or GOG saves directly and adds bulk tools the other editors don't have: base sorting and reordering, fleet-wide starship upgrades, category-based inventory sorting, and teleport-endpoint relocation.

> **Alpha software (v0.5.0-alpha).** No warranty. Always back up your live saves before editing — the app's **File → Full Live Save Backup** does this for you. Feedback is welcome: **BigBuffaloBill** on Discord.

## What it does

- **Open saves directly.** File → Open NMS Save File lists your save slots (Steam `st_*` or GOG `DefaultUser`), picks the newer of each slot's Auto/Manual save, and loads the active context (main game or expedition).
- **Save back safely.** File → Save NMS Save File writes the same slot and context you loaded, after a confirmation. Close the game first.
- **Full live save backup.** File → Full Live Save Backup copies your whole NMS save folder to a timestamped, verified backup. Full Live Save Restore shows step-by-step manual restore instructions.
- **Bases.** Sort by galaxy, system and name; move the freighter base to the top; drag and drop to reorder; back up a single base to a file and restore it; delete bases.
- **Starships.** Upgrade selected ships to their reference stats, class and technology; delete ships safely while keeping the game's fixed ship slots.
- **Inventories.** Inventory Sorter moves whole items by category into the containers you choose, with a review step before anything changes; back up an inventory and replace one from a backup.
- **Teleport endpoints.** Move your saved player location to any endpoint in the game's teleport history.
- **Node View and Raw JSON.** Every tab shows a tree and the raw JSON side by side. Edits are checked before they are applied, and unsynced edits are never silently discarded.

All edits change the app's copy of the data only. Nothing is written to your game files until you choose Save.

## Install

### Windows executable (recommended)
1. Download the latest `.exe` from the [Releases page](https://github.com/waryder/BBB-NMS-Save-File-Manipulator/releases).
2. Put it in a folder you can write to (for example a folder in Documents) and run it. There is no installer.
3. On first start, choose where the app keeps its own data (a folder named `BBB NMS SFM Data`). Your game saves are never moved there.

If Windows reports missing MSVC runtime libraries, install the [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist).

### From source
Requires Python 3.8 or later (developed on Python 3.12).

```
pip install -r requirements.txt
python BBB_NMS_Save_File_Manipulator.py
```

## Using it

1. Close No Man's Sky.
2. File → Full Live Save Backup.
3. File → Open NMS Save File, pick your slot, Load Slot.
4. Make your changes on the Bases, Starships, Inventory and Teleport Endpoints tabs.
5. File → Save NMS Save File, check the slot and context, confirm.

Help → Open Help opens the full help, bundled with the app (it also works offline). An online copy is at <https://bigbuffalobill-web.pages.dev/nms-help/>.

## Supported platforms

Windows with the Steam or GOG version of No Man's Sky. Microsoft Store / Game Pass, consoles, macOS and Linux saves are not supported.

## Licence

GNU General Public License v3.0 or later — see [LICENSE](LICENSE).

The save-file codec (`nms_save_codec/`) is a Python port of [libNOM.io](https://github.com/zencq/libNOM.io) (GPLv3). Save-key mapping data comes from [MBINCompiler](https://github.com/monkeyman192/MBINCompiler).

Copyright (C) 2024-2026 BigBuffaloBill - Bill Ryder.
