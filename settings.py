DEBUG=True

# For keyboard input
COMMAND_SET = "commands.KeyCommandSet"
INPUT_HANDLER = "kbd.InputHandler"

# For the pedal board
#COMMAND_SET = "commands.StompCommandSet"
#INPUT_HANDLER = "rpi.InputHandler"

# RPi switch settings
# list of GPIO inputs to map to switches 0..n
SWITCH_CHANNELS = [36]