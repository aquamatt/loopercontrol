#!/usr/bin/env python3
from queue import Queue
import os
import sys

from pynput import keyboard

from looper import *
from utils import Intervals


LOOPER_ADDR = "localhost"
LOOPER_PORT = 9951
NUM_LOOPS = 3
DOUBLE_TAP_INTERVAL = 0.08   # seconds
LONG_PRESS_INTERVAL = 0.5    # seconds


channel = Channel(LOOPER_ADDR, LOOPER_PORT)

# setup loops in SooperLooper
# don't call this if you want to bind to already setup instance
channel.clear_loops()
looper = Looper(channel)
for i in range(NUM_LOOPS):
    loop = Loop()
    looper.add_loop(loop, True if i == 0 else False)
    time.sleep(0.1)

TIMER = Intervals()

q = Queue()


def flush_keys():
    """
    The buffer will have loads of presses in it. Terminate in 'enter',
    read the line and discard.
    """
    this_keyboard = keyboard.Controller()
    this_keyboard.press(keyboard.Key.enter)
    this_keyboard.release(keyboard.Key.enter)
    sys.stdin.readline()


def set_echo(on=False):
    """
    Disable/enable echoing of input to screen
    """
    if on:
        os.system("stty > /dev/null")
    else:
        os.system("stty -echo")


def on_press(key):
    ##
    ## BUG:
    ## This will start time, and put is in frame, when <SHIFT> (or other
    ## modifier) pressed. That will then ensure we ignore another keypress
    ## such as the actual character.

    delta = TIMER.start()
    if delta is None:
        return

    if delta < DOUBLE_TAP_INTERVAL:
        prefix = "double_"
    else:
        prefix = ""

    try:
        ch = key.char
        if key.char == '+':
            ch = "PLUS"
        elif key.char == '-':
            ch = "MINUS"

        q.put_nowait("{}{}".format(prefix, ch))

    except AttributeError:
        ch = None

        if key == keyboard.Key.space:
            ch = "SPACE"
        elif key == keyboard.Key.up:
            ch = "UP"
        elif key == keyboard.Key.down:
            ch = "DOWN"
        elif key == keyboard.Key.left:
            ch = "LEFT"
        elif key == keyboard.Key.right:
            ch = "RIGHT"

        elif key in [keyboard.Key.ctrl,
                     keyboard.Key.ctrl_r,
                     keyboard.Key.shift,
                     keyboard.Key.shift_r,
                     keyboard.Key.alt_gr,
                     keyboard.Key.alt,
                     keyboard.Key.alt_r]:
            TIMER.ignore_next()
            return

        if ch is not None:
            q.put_nowait("{}{}".format(prefix, ch))


def on_release(key):
    delta = TIMER.stop()
    ch = None
    try:
        ch = key.char
        if ch == 'q':
            # Stop listener
            return False
    except AttributeError:
        if key == keyboard.Key.space:
            ch = "SPACE"
        elif key == keyboard.Key.up:
            ch = "UP"
        elif key == keyboard.Key.down:
            ch = "DOWN"
        elif key == keyboard.Key.left:
            ch = "LEFT"
        elif key == keyboard.Key.right:
            ch = "RIGHT"

    if delta is not None and delta >= LONG_PRESS_INTERVAL and ch is not None:
        q.put_nowait("long_{}".format(ch))


# Key command action mappings

def handle_double_SPACE():
    """
    Stop playback. The first tap of the double tap would, if playback was
    the prior state, have started recording/overdubbing. We therefore stop
    that and discard the fraction of a second long layer first before
    pausing everything.

    If recording/overdubbing was happening prior to the double tap, the first
    tap would have stopped that, and this will only pause everything, retaining
    the layer that we had intentionally recorded.
    """
    looper.selected.stop_record_and_discard()
    looper.toggle_pause_all()

def handle_SPACE():
    """
    Toggle though states
    """
    looper.selected.play_record_or_overdub()

def handle_PLUS():
    looper.select_next()

def handle_MINUS():
    looper.select_previous()

def handle_R():
    looper.selected.record()

def handle_U():
    looper.selected.undo_all()

def handle_u():
    looper.selected.undo()

def handle_r():
    looper.selected.redo()

def handle_q():
    osc_terminate()
    flush_keys()
    set_echo()
    sys.exit(0)


#with keyboard.Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()

keyboard.Listener(
    on_press=on_press,
    on_release=on_release).start()

set_echo(False)

# Fetch all the key handler functions in one dict
commands = [i for i in dir() if i.startswith('handle_')]
command_fns = {k: v for (k, v) in globals().items() if k in commands}

# enter event loop to handle keypresses as received.
while True:
    ch = q.get()
#    print("Processing {}".format(ch))
    fn = "handle_{}".format(ch)
    if fn in commands:
        command_fns[fn]()
