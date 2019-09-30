DEBUG=False

# For keyboard input
COMMAND_SET = "commands.KeyCommandSet"
INPUT_HANDLER = "kbd.InputHandler"

# For the pedal board
#COMMAND_SET = "commands.StompCommandSet"
#INPUT_HANDLER = "rpi.InputHandler"

# RPi switch settings
# list of GPIO inputs to map to switches 0..n
SWITCH_CHANNELS = [36]


# import local settings from the (gitignored) local.py
# If it doesn't exist, that's fine.
try:
    from local import *
    print("Local settings imported.")
except ImportError:
    print("No local settings.")

