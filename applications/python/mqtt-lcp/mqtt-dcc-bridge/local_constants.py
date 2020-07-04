# local_constants.sh


"""

    local_constants.py - Constants used in mqtt-dcc-bridge


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
class Local():
    """ local constants """

    MSG_POWER_PUBLISHED = "power status published: "
    MSG_THROTTLE_PUBLISHED = "throttle status published: "
    MSG_CAB_PUBLISHED = "cab status published: "
    MSG_NEW_SWITCH = "new turnout info received: "
    MSG_NEW_TRACK = "new track info received: "
    MSG_NEW_CAB = "new cab info received: "
    MSG_ERROR_BAD_STATE = "error: desired state is not valid: "
    MSG_ERROR_THROTTLE_ALREADY_CONNECTED = "throttle is already connected"
    MSG_ERROR_THROTTLE_NOT_CONNECTED = "throttle is not connected"
    MSG_ERROR_CAB_ALREADY_ACQUIRED = "cab is already acquired"
    MSG_ERROR_CAB_NOT_ACQUIRED = "cab has not been acquired"
    MSG_ERROR_NO_DCC_ID = "no dcc id specifed: "
    MSG_ERROR_SINGLE_STEAL = "steal/share only allowed on a single loco"
    MSG_ERROR_FORCED_DISCONNECT = "forced disconnect"
    MSG_ERROR_NO_SLOTS_AVAIL = "no registers/slots available"
    MSG_ERROR_FUNC_NUM = "function number must be between 0-28"
    MSG_ERROR_FUNC_ACTION = "function action must be on or off"
    MSG_ERROR_BAD_PORT = "error: port not found in config file "
    MSG_ERROR_INVALID_REQUEST = "request is invalid"
