#!/usr/bin/env python
import OSC
import sys

WAIT, RECORDING, OVERDUBBING, PLAYBACK = (1, 2, 3, 4)
STATE = WAIT

c = OSC.OSCClient()
c.connect(('localhost', 9951))

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def send_command(command, loop=-1):
    oscmsg = OSC.OSCMessage()
    oscmsg.setAddress("/sl/{}/hit".format(loop))
    oscmsg.append(command)
    c.send(oscmsg)

def mute(loop=-1):
    send_command("mute", loop)

def clear_all(loop=-1):
    global STATE
    send_command("undo_all", loop)
    STATE = WAIT

def record_or_overdub(loop=-1):
    global STATE
    if STATE == WAIT:
        send_command("record", loop)
        STATE = RECORDING
    elif STATE == PLAYBACK:
        send_command("overdub", loop)
        STATE = OVERDUBBING
    elif STATE == RECORDING:
        send_command("record", loop)
        STATE = PLAYBACK
    elif STATE == OVERDUBBING:
        send_command("overdub", loop)
        STATE = PLAYBACK

while True:
    fetcher = _Getch()
    ch=fetcher()
    if ch == ' ':
        record_or_overdub()
    elif ch == 'U':
        clear_all()
    elif ch == 'q':
        sys.exit(0)
