DEBUG=False

CONFIG_SETS = {
    "default": {
        "doc": "Keyboard and OSC looper controller",
        "COMMAND_SET": "commands.KeyCommandSet",
        "INPUT_HANDLER": "kbd.InputHandler"
        },
    "stomp_midi_server": {
        "doc": "JACK-side bridge with MIDI command emitter",
        "COMMAND_SET": "midi.MidiCommandSet",
        "INPUT_HANDLER": "bridge.BridgeInputHandler"
        },
    "stomp_server": {
        "doc": "JACK-side bridge with stomp box OSC looper controller",
        "COMMAND_SET": "commands.StompCommandSet",
        "INPUT_HANDLER": "bridge.BridgeInputHandler"
        },
    "key_server": {
        "doc": "JACK-side bridge with keyboard OSC looper controller",
        "COMMAND_SET": "commands.KeyCommandSet",
        "INPUT_HANDLER": "bridge.BridgeInputHandler"
        },
    "stomp_pedal_client": {
        "doc": "Stomp box input bridged to server",
        "COMMAND_SET": "bridge.BridgeCommandSet",
        "INPUT_HANDLER": "rpi.InputHandler",
        },
    "key_client": {
        "doc": "Keybord input bridged to server",
        "COMMAND_SET": "bridge.BridgeCommandSet",
        "INPUT_HANDLER": "kbd.InputHandler"
        },
    "stomp": {
        "doc": "Stomp box input with OSC looper controller",
        "COMMAND_SET": "commands.StompCommandSet",
        "INPUT_HANDLER": "rpi.InputHandler"
        },
}

# RPi switch settings
# list of GPIO inputs to map to switches 0..n
SWITCH_CHANNELS = [36]
GPIO_DEBOUNCE_DELAY = 200 # ms
# maximum time between taps to count as a double tap
# lower bound is effectively determined by GPIO_DEBOUNCE_DELAY
DOUBLE_TAP_INTERVAL = 0.500 # seconds

# Network bridge mode
UDP_HOST = "127.0.0.1"
UDP_PORT = 21974

# import local settings from the (gitignored) local.py
# If it doesn't exist, that's fine.
try:
    from local import *
    print("Local settings imported.")
except ImportError:
    print("No local settings.")

