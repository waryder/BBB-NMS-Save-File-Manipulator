# File: version.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\version.py
# Purpose: The one place the application version is set (row 520). setup.py, Help -> About and release names read it.

APP_VERSION = '0.5.0-alpha'  # Package and release version (setup.py, git tag, build names).
DISPLAY_VERSION = 'v' + APP_VERSION.replace('-', ' ')  # Shown to users, e.g. 'v0.5.0 alpha'.
