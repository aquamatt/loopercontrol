DEBUG=False

# For keyboard input RECEIVED over UDP bridge
#COMMAND_SET = "commands.KeyCommandSet"
#INPUT_HANDLER = "kbd.InputHandler"
COMMAND_SET = "midi.MidiCommandSet"
INPUT_HANDLER = "bridge.BridgeInputHandler"


# For the pedal board
#COMMAND_SET = "commands.StompCommandSet"
#INPUT_HANDLER = "rpi.InputHandler"

# RPi switch settings
# list of GPIO inputs to map to switches 0..n
SWITCH_CHANNELS = [36]
GPIO_DEBOUNCE_DELAY = 200 # ms
# maximum time between taps to count as a double tap
# lower bound is effectively determined by GPIO_DEBOUNCE_DELAY
DOUBLE_TAP_INTERVAL = 0.500 # seconds

# Network bridge mode
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT = 21974

# import local settings from the (gitignored) local.py
# If it doesn't exist, that's fine.
try:
    from local import *
    print("Local settings imported.")
except ImportError:
    print("No local settings.")

