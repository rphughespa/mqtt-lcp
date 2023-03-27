#!/usr/bin/python3
#local_Local.py

"""

    local_constants.py - Constants used in mqtt messaging.
            To implement mqtt messaging in a language other than english, edit this file
            and the appropiate config.json files.

the MIT License (MIT)

Copyright © 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""

class Local(object):
    """ local constants """
    ACQUIRE = "Acquire"
    ACQUIRED = "Acquired"
    AUTO_SIGNALS = "Automatic Signals"
    BACKUP = "Backup"
    BELL = "Bell"
    BLOCK = "Block"
    CAB_ALL = "all"
    CAB_A = "a"
    CAB_B = "b"
    CONSIST = "Consist"
    CTC_TRAFFIC_CONTROL = "Central Traffic Control"
    DASHBOARD = "Dashboard"
    DEFAULT_FG = "black"
    DEFAULT_BG = "snow2"
    #DEFAULT_FG = "white"
    #DEFAULT_BG = "black"
    EMPTY = "empty"
    FASTCLOCK = "Fastclock"
    FASTCLOCK_PAUSE = "Pause Fastclock"
    FASTCLOCK_RESET = "Reset Fastclock"
    FASTCLOCK_RUN = "Run Fastclock"
    FUNCTIONS = "Functions"
    HORN = "Horn"
    IS_REVERSED = "Loco is reversed"
    KEYPAD = "Keypad"
    LIGHT = "Lighr"
    LOCALTIME = "Local Time"
    LOCATION = "Location"
    LOCO_IMAGE_WIDTH = 190
    LOCO_IMAGE_HEIGHT = 40
    LOCO = "Loco"
    LOCOS = "Locos"
    PANEL = "Panel"
    PANELS = "Panels"
    POWER = "Power"
    REBOOT = "Reboot"
    RELEASE = "Release"
    RELEASE_ALL = "Release All"
    REQUEST = "Request"
    ROSTER = "Roster"
    ROUTE = "Route"
    ROUTES = "Routes"
    SELECTED = "Selected"
    SIGNAL = "Signal"
    SIGNALS = "Signals"
    SHUTDOWN = "Shutdown"
    SWITCHES = "Switches"
    SYSTEM = "System"
    THROTTLE = "Throttle"
    TOWER = "Tower"
    TRACK_POWER = "Track Power"
    TRAFFIC_CONTROL = "Traffic Control"
    UNSELECT = "unselect"
    UNSELECTED = "unselected"
    WARRANT = "Warrant"
    WARRANTS="Warrants"

    MSG_ADD_TO_LIST = "Add to Locos List"
    MSG_BACKUP_1 = "Backup"
    MSG_BACKUP_2 = "Initiate the backup of the config\n files of all nodes on the layout."
    MSG_CONTROL = "Traffic Control"
    MSG_POWER_PUBLISHED = "Power published: "
    MSG_BACKUP_CONFIRM = "Backup the nodes !!!\n\nContinue?"
    MSG_FASTCLOCK_RESET = "Fastclock has been\nReset"
    MSG_FASTCLOCK_PAUSED = "Fastclock has been\nPaused"
    MSG_FASTCLOCK_RUNNING = "Fastclock is\nRunning"
    MSG_REBOOT_CONFIRM = "Reboot the computer !!!\n\nContinue?"
    MSG_REBOOT_PUBLISHED = "Reboot command published:  "
    MSG_RELEASE_CONFIRM = "Release all Locos ?"
    MSG_TRACK_POWER_1 = "Track Power"
    MSG_TRACK_POWER_2 = "Power is currently: "
    MSG_TRAFFIC_CONTROL = "CTC Traffic Control"
    MSG_SHUTDOWN_1 = "Shutdown"
    MSG_SHUTDOWN_2 = "Initiate clean shutdown\nof layout computers.\n\nRemember:\n" + \
        " Wait one minute before\nyou power down layout."
    MSG_SHUTDOWN_CONFIRM = "Shutdown the layout !!!\n\nContinue?"
    MSG_SHUTDOWN_PUBLISHED = "Shutdown broadcast published ..."
    MSG_STEAL_NEEDED_CONFIRM = "is being used by another throttle.\n\nSteal it?"
