# global_constants.sh


"""

    global_constants.py - Constants used in mqtt_lcp applications
            To implement mqtt messaging in a language other than english, edit this file
            and the appropiate config.json files.

The MIT License (MIT)

Copyright 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""

class Global():
    """ Definition of global literals """
    ACQUIRE = "acquire"
    ADD = "add"
    ADDRESS = "address"
    AVAILABLE = "available"
    BAUDRATE = "baudrate"
    BACKUP = "backup"
    BELL = "bell"
    BLANK = "blank"
    BLOCK = "block"
    BLOCKS = "blocks"
    BROADCAST = "broadcast"
    BROKER = "broker"
    BUS = "bus"
    BUTTON = "button"
    CAB = "cab"
    CLOSE = "close"
    CLOSED = "closed"
    CMD = "cmd"
    COL = "col"
    COLS = "cols"
    COMMAND = "command"
    COMPLETE = "complete"
    CONFIG = "config"
    CONSIST = "consist"
    CURRENT = "current"
    DASHBOARD = "dashboard"
    DATA = "data"
    DAY = "day"
    DCC = "dcc"
    DELAY = "delay"
    DELETE = "delete"
    DESCRIPTION = "description"
    DEVICE_TYPE = "device-type"
    DISPLAY = "display"
    DIVERGE = "diverge"
    DT = "dt"
    DESIRED = "desired"
    DOWN = "down"
    ENTRY = "entry"
    EPOCH = "epoch"
    ERROR = "error"
    EXIT = "exit"
    EXPIRE = "expire"
    FAST = "fast"
    FASTCLOCK = "fastclock"
    FILE = "file"
    FUNCTIONS = "functions"
    GPIO = "gpio"
    GRID = "grid"
    HORN = "horn"
    HOUR = "hour"
    ID = "id"
    IDS = "ids"
    IO = "io"
    INTERVAL = "interval"
    I2C = "i2c"
    IMAGE = "image"
    INPUT = "input"
    INVALID = "invalid"
    INVENTORY = "inventory"
    ITEMS = "items"
    KEYBOARD = "keyboard"
    KEYPAD = "keypad"
    LABEL = "label"
    LARGE = "large"
    LAYOUT = "layout"
    LAYOUTS = "layouts"
    LEVEL = "level"
    LIGHT = "light"
    LIST = "list"
    LOGGER = "logger"
    LOCO = "loco"
    LOCOS = "locos"
    MAX = "max"
    MAX_SPEEDSTEP = "max_speedstep"
    MEDIUM = "medium"
    MENU = "menu"
    MESSAGES = "messages"
    METADATA = "metadata"
    MIN = "min"
    MINUTES = "minutes"
    MONTH = "month"
    MQTT = "mqtt"
    MUX = "mux"
    NAME = "name"
    NEXT = "next"
    NODE = "node"
    NODE_ID = "node-id"
    OFF = "off"
    ON = "on"
    OPTIONS = "options"
    OTHER_TOPICS = "other-topics"
    PAGE = "page"
    PANELS = "panels"
    PASSWORD = "password"
    PATHS = "paths"
    PAUSE = "pause"
    PING = "ping"
    PING_TIME = "ping-time"
    PORT = "port"
    PORTS = "ports"
    PORT_ID = "port-id"
    POWER = "power"
    PRESS = "press"
    PREV = "prev"
    PRODUCT = "product"
    PUBLISH = "pub"
    PUB_TOPICS = "pub-topics"
    RATIO = "ratio"
    READY = "ready"
    REBOOT = "reboot"
    RECEIVED = "rcv"
    RED = "red"
    REFRESH = "refesh"
    REGISTRY = "registry"
    RELEASE = "release"
    REMOVE = "remove"
    REPORT = "report"
    REPORTED = "reported"
    RESPONSE = "response"
    REQUEST = "request"
    REQ = "req"
    RES = "res"
    RES_TOPIC = "res-topic"
    RESET = "reset"
    RFID = "rfid"
    ROSTER = "roster"
    ROTARY = "rotary"
    ROW = "row"
    ROWS = "rows"
    RUN = "run"
    SCREEN_SIZE = "screen-size"
    SECONDS = "seconds"
    SELECT = "select"
    SELF = "self"
    SENSOR = "sensor"
    SENSORS = "sensors"
    SERIAL = "serial"
    SERVO = "servo"
    SESSION_ID = "session-id"
    SET = "set"
    SIGNAL = "signal"
    SIGNALS = "signals"
    SIZE = "size"
    SHUTDOWN = "shutdown"
    SMALL = "small"
    START = "start"
    STATE = "state"
    STATIONARY = "stationary"
    STATUS = "status"
    SUBSCRIBE = "subscribe"
    SUB_ADDRESS = "sub-address"
    SUB_TOPICS = "sub-topics"
    SUPERVISOR = "supervisor"
    SWITCH = "switch"
    SWITCHES = "switches"
    SYSTEM = "system"
    TIME = "time"
    TITLE = "title"
    THROUGH = "through"
    THROTTLE = "throttle"
    TOPICS = "topics"
    TOWER = "tower"
    TRACK = "track"
    THROW = "throw"
    THROWN = "thrown"
    TOPIC = "topic"
    TRACK = "track"
    TURNOUT = "turnout"
    TURNOUTS = "turnouts"
    TYPE = "type"
    TIMESTAMP = "timestamp"
    UP = "up"
    UNKNOWN = "unknown"
    USB = "usb"
    USER = "user"
    VENDOR = "vendor"
    VERSION = "version"
    VERTICAL = "vertical"
    WARRANT = "warrant"
    WARRANTS = "warrants"
    WHITE = "white"
    YEAR = "year"

    MSG_BACKUP_RECEIVED = "Backup command received"
    MSG_COMPLETED = "...Completed."
    MSG_ERROR_NO_DESIRED = "error:desired-missing"
    MSG_EXITING = "Exiting."
    MSG_I2C_DATA_RECEIVED = "I2C Data recvd: "
    MSG_I2C_NOT_CONNECTED = "Error, I2C Device Not Connected: "
    MSG_KEYBOARD_RECEIVED = "Keyboard Input Received: "
    MSG_REBOOT_RECEIVED = "Reboot command received"
    MSG_REQUEST_MSG_RECEIVED = "Request message recvd: "
    MSG_RESPONSE_RECEIVED = "Response message recvd: "
    MSG_SEND_SERIAL = "Sending Serial message: "
    MSG_SERIAL_RECEIVED = "Serial Input received: "
    MSG_SEND_SERIAL_WAIT = "Send / Wait Serial message: "
    MSG_SHUTDOWN_RECEIVED = "Shutdown command received"
    MSG_STARTING = "Starting..."
    MSG_UNKNOWN_REQUEST = "Unknown Request message recvd: "
    MSG_UNKNOWN_NODE = "Unknown Node in message recvd: "
    MSG_NEW_SWITCH = "new turnout req received: "
    MSG_ERROR_BAD_STATE = "error: requested state is not valid: "
    MSG_ERROR_SERVO_NOT_KNOWN = "error: requested servo name not known: "
    MSG_ERROR_SERVO_MOVE = "error: servo movement failed: "

    LOG_LEVEL_CRITICAL = 50
    LOG_LEVEL_ERROR = 40
    LOG_LEVEL_WARNING = 30
    LOG_LEVEL_INFO = 20
    LOG_LEVEL_DEBUG = 10
    LOG_LEVEL_NOTSET = 0
    LOG_LEVEL_CONSOLE = -1

    BUTTON_UP = 100
    BUTTON_PAGE_UP = 101
    BUTTON_DOWN = 90
    BUTTON_PAGE_DOWN = 91
    BUTTON_LEFT = 80
    BUTTON_PAGE_LEFT = 81
    BUTTON_RIGHT = 70
    BUTTON_PAGE_RIGHT = 71
    BUTTON_A = 60
    BUTTON_B = 50
    BUTTON_MENU = 40
    BUTTON_VOLUME = 30
    BUTTON_SELECT = 20
    BUTTON_MENU_PREV = 20
    BUTTON_START = 10
    BUTTON_MENU_NEXT = 10
