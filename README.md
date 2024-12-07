# BBB NMS Save File Manipulator

## Overview
BBB NMS Save File Manipulator is a tool designed to help users manipulate No Man's Sky save files. This tool is intended to fill holes in, and not duplicate, features in the other well-known editors. Primary value adds at this point are:

1) One click sort of bases by Galaxy, System, and then Name.
2) Drag and drop reordering of Bases.
3) One click upgrade of all Starships to Max stats and tech installed. A one click comprehensive starship upgrades to your whole fleet! 
4) Drag and drop reordering of Starships
5) Inventory sort (really moving items). This is the least "finished/polished". I will be adding more categories to the possible sorting criteria. Also I do no checking to save users from moving items to the wrong inventories. For example right now it's on you to make sure you don't put non fish bait in the fish bait inventory. But basically you have a dialog box where you click a bunch of checkboxes to setup your sort...and then click a button to get your inventory items moved around as you want.
6) Saving off an inventory and restore it to any other inventory. The way this works is you save an inventory. On reimport, the items in that save overwrite the the target inventories items. This allows you to save off desired inventory items to refresh any inventory later with a known loadout.
7) Relocate your player to locations stored in the save file "Teleport Endpoints" list. This is a list kept by the game of the last (potentially hundreds) of locations where you teleported to. You can use this to get back to places you visited in the past but never threw a base down.
8) Aside from those, you can pretty much modify any data in the save file at all, and general features provided as in any text editor and Json editor (with a tree view) that you may find out there.




At this point this is a raw version maybe worthy of evaluation but I do not claim this is production ready. I am releasing and promoting only for the purpose of solciting testing and and review of the current state. I do provide screenshots and help files as a seperate zip file if that's all you would like to look at at first.

DISCLAIMERS: I cannot be held liable for any damage this app causes. Period. I have been a software engineer for over 20 years and while I have a confidence in my work, 
				I also know end users will find every flaw in even the best engineered applications, whereas I am a one man show over here. :) I recommend that you save off back up copies 
				of your save files before you use any editor at all, and be aware that BBB NMS Save File Manipulator must really be used by technical experts only. If you are not super 
				comfortable with JSON files, file manipulation, and all aspects of what you see in the app, just stop and do not use it! If you do find any errors I need to know about, 
				I am BigBuffaloBill over on Discord. But please DO NOT write and tell me I wrecked your game! My answer will be "no problem; just use the backup file I told you to make
				and go restore yourself." :) I do use this application regularly myself at this point, but I make backups just in case!!
				

## Note on Usage

Before you even get to the in game help, please know that you need to grab the entire "BaseContext" json from the raw json editor in a tool like Goatfungus, for import into this application. This is the whole of the data this application works on and imports and exports in and out.

## Installation Instructions - Zip file (for use with an existing Python installtion)

All of the following assume a stable python environment. I purposely do not go into the details of setting this up because in honesty my app is intended for techie geeks and if you think python is a snake in the Amazon I'm not sure you are going to want to use this app. :)

1. Go to the Releases page: https://github.com/your_username/BBB-NMS-SFM/releases](https://github.com/waryder/BBB-NMS-Save-File-Manipulator/releases. 
2. Download the latest release zip file.
3. Extract the zip file to a folder on your computer.
4. Open a terminal in the folder where you extracted the files (the same folder where `setup.py` is located).
5. Run the following command to install the application:
```bash
>pip install .
```
6. To run the application, use:
```bash
>bbb_nms_sfm
```

## Installation Instructions - Exe file (single file install for Windows machines)

1. Go to the Releases page: https://github.com/your_username/BBB-NMS-SFM/releases](https://github.com/waryder/BBB-NMS-Save-File-Manipulator/releases.
2. Download the latest release exe file.
3. The exe provided in the release is a standalone application file. You simply drop it in a non-system folder with run permissions and double-click it or otherwise start it as you will. It is not an installation file it will just run.


