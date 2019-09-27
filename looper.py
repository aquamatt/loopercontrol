"""
SooperLooper library
"""
import time

from osc4py3 import oscbuildparse
from osc4py3.as_eventloop import *
#from osc4py3.as_allthreads import *

import settings


MINIMUM_LOOP_DURATION = 60 # seconds
MONO, STEREO = (1, 2)


class Channel(object):
    """
    Link to the actual SooperLooper instance
    """
    def __init__(self, looper_addr, looper_port):
        self.looper_addr = looper_addr
        self.looper_port = looper_port
        self.start()

    def start(self):
        osc_startup()
        osc_udp_client(self.looper_addr, self.looper_port, "SooperLooper")

    def _send(self, address, formatter, args):
        msg = oscbuildparse.OSCMessage(address, formatter, args)
        osc_send(msg, "SooperLooper")
        osc_process()
        if settings.DEBUG:
            print("{} {} {}".format(address, formatter, args))

    def _send_hit(self, command, loop=-3):
        """
        Send a 'hit' to some command on a specific loop (defaults to selected)
        """
        self._send("/sl/{}/hit".format(loop), ",s", [command])

    def _send_set(self, control, value, loop=-3):
        """
        Set a property on a given loop
        """
        self._send("/sl/{}/set".format(loop), ",sf", [control, value])

    def _send_global_set(self, param, arg):
        """
        Set a global property
        """
        self._send("/set", ",sf", [param, arg])

    def record(self, loop=-3):
        self._send_hit("record", loop)

    def overdub(self, loop=-3):
        self._send_hit("overdub", loop)

    def undo(self, loop=-3):
        self._send_hit("undo", loop)

    def redo(self, loop=-3):
        self._send_hit("redo", loop)

    def pause(self, loop=-3):
        self._send_hit("pause", loop)

    def pause_multi(self, loops=[]):
        """
        Pause a number of loops simultaneously.
        """
        msgs = []
        for loop in loops:
            msgs.append(
                oscbuildparse.OSCMessage("/sl/{}/hit".format(loop.index),
                                         ",s", ["pause"]
                                         )
                )
            if settings.DEBUG:
                print(">> {} {} {}".format("/sl/{}/hit".format(loop.index), ",s", ["pause"]))

        bundle = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, msgs)
        osc_send(bundle, "SooperLooper")
        osc_process()

    def unpause_multi(self, loops=[]):
        """
        Unpause a number of loops, assuming synced to loop 0.

        We therefore hit trigger on all bar loop 0 and then unpause 0 (unless
        has already been unpaused).
        """
        master = None
        msgs = []
        for loop in loops:
            if loop.index == 0:
                master = loop
                continue
            msgs.append(
                oscbuildparse.OSCMessage("/sl/{}/hit".format(loop.index),
                                         ",s", ["trigger"]
                                         )
                )
        bundle = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, msgs)
        osc_send(bundle, "SooperLooper")
        osc_process()

        if master.state == Loop.PAUSED:
            self.pause(master.index)

    def undo_all(self, loop=-3):
        self._send_hit("undo_all", loop)

    def trigger(self, loop=-3):
        self._send_hit("trigger", loop)

    def select_loop(self, index):
        """
        Set indexed loop as selected.
        """
        self._send_global_set("selected_loop_num", index)

    def add_loop(self, channels=MONO):
        """
        Add loop to SooperLooper
        """
        if channels not in [MONO, STEREO]:
            raise Exception("Can only have 1 or 2 channels on a loop")
        self._send("/loop_add", ",if", [channels, MINIMUM_LOOP_DURATION])

    def set_sync_source(self, loop=0):
        """
        Set sync source globally to the given (zero indexed) loop. Defaults
        to the first.
        """
        # command takes unit-indexed loop index
        self._send_global_set("sync_source", loop+1)

    def set_properties(self, properties={}, loop=-3):
        """
        Take dict of properties and set on the loop.
        e.g.
        properties = dict(sync=1, playback_sync=1, quantize=3)
        """
        messages = []
        for command, value in properties.items():
            msg = oscbuildparse.OSCMessage("/sl/{}/set".format(loop),
                                           ",sf",
                                           [command, value])
            messages.append(msg)
            if settings.DEBUG:
                print(">> {} {} {}".format("/sl/{}/set".format(loop), ",sf", [command, value]))

        if messages:
            bundle = \
                oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, messages)
            osc_send(bundle, "SooperLooper")
            osc_process()

    def clear_loops(self):
        """
        Crude way to clear out loops from the looper. Works so long as
        you don't have more than 10 in there!
        """
        for i in range(10):
            msg = oscbuildparse.OSCMessage("/loop_del", ",i", [-1])
            osc_send(msg, "SooperLooper")
            osc_process()
            time.sleep(0.1)


class Looper(object):
    """
    Represents a SooperLooper instance. Can contain many loops
    """
    def __init__(self, channel):
        self.loops = []
        self.channel = channel

        # @todo decide whether the Loop class should not have an index,
        # and whether we should just work on a 'selected loop' basis.
        self.selected_loop = 0

        # used to store loops that have been group paused
        self.group_pause_cache = None

    def add_loop(self, loop, channels=MONO, master=False, create=True):
        """
        Master loop is the one which will be considered the sync source

        If `create` == True, send instruction to SooperLooper to create
        the loop, otherwise just create entry here (for use if binding
        to existing looper setup)
        """
        loop.looper = self
        loop.index = len(self.loops)
        self.loops.append(loop)

        if loop.index == self.selected_loop:
            self.select_loop(loop)

        if create:
            self.channel.add_loop(channels)
            # without out this tiny pause the Looper will not have setup the loop
            # and so the setting of properties will fail as there's no loop on
            # which to set them...
            # It could be shorter, but we'll try and play safe.
            time.sleep(0.05)

            if master:
                self.channel.set_properties(
                    dict(sync=0, playback_sync=0, quantize=3),
                    loop.index)
                self.channel.set_sync_source(loop.index)
            else:
                self.channel.set_properties(
                    dict(sync=1, playback_sync=1, quantize=3),
                    loop.index
                    )

    @property
    def selected(self):
        """
        Return currently selected loop
        """
        return self.loops[self.selected_loop]

    def toggle_pause_all(self):
        """
        Toggle pausing/unpausing of all pausable loops.

        Pause all loops that are not already paused. Can't just do a
        'hit' on Pause for all as this will unpause any paused channels.

        Reverse the previous operation to play. Note that this will NOT unpause
        any loops that were paused *prior* to being group paused.
        """
        if self.group_pause_cache is None:
            self._pause_all()
        else:
            self._unpause_all()

    def _pause_all(self):
        """
        Pause all loops that are not already paused. Can't just do a
        'hit' on Pause for all as this will unpause any paused channels.
        """
        running_loops = [l for l in self.loops
                         if l.state not in [Loop.PAUSED, Loop.WAIT]
                         ]

        self.channel.pause_multi(running_loops)
        for l in running_loops:
            l.state = Loop.PAUSED

        self.group_pause_cache = running_loops

    def _unpause_all(self):
        """
        Unpause those loops paused by pause_all.
        Assumes loop 0 is the master and all others sync to that.
        """
        self.channel.unpause_multi(self.group_pause_cache)
        for l in self.group_pause_cache:
            l.state = Loop.PLAYBACK

        self.group_pause_cache = None

    def select_loop(self, loop):
        self.selected_loop = loop.index
        self.channel.select_loop(loop.index)

    def select_next(self):
        self.selected_loop = (self.selected_loop + 1) % len(self.loops)
        self.select_loop(self.selected)

    def select_previous(self):
        self.selected_loop = (self.selected_loop - 1) % len(self.loops)
        self.select_loop(self.selected)


class Loop(object):
    """
    Represents a single loop in the looper.
    """
    WAIT, RECORDING, OVERDUBBING, PLAYBACK, PAUSED = range(5)

    def __init__(self, looper=None, loop_index=0):
        self.index = loop_index
        self.looper = looper

        # Track layers almost entirely so as to know when we've got to the
        # first layer so that we can undo that with an 'undo_all' and get
        # expected behaviour which you don't get by issuing a 'hit' on that
        # base layer.
        self.current_layer = 0
        self.layers = 0

        # this assumes a brand new Loop...
        self.state = self.WAIT

    def select(self):
        """
        Set this as a selected loop
        """
        self.looper.select_loop(self)

    def play_record_or_overdub(self):
        if settings.DEBUG:
            print("PRO: Enter state: {}".format(self.state))
        if self.state == self.WAIT:
            self.record()

        elif self.state == self.PAUSED:
            self.looper.channel.trigger(self.index)
            self.state = self.PLAYBACK

        elif self.state in [self.PLAYBACK, self.PAUSED]:
            self.overdub()

        elif self.state == self.RECORDING:
            self.looper.channel.record(self.index)
            self.state = self.PLAYBACK

        elif self.state == self.OVERDUBBING:
            self.looper.channel.overdub(self.index)
            self.state = self.PLAYBACK

    def record(self):
        self.looper.channel.record(self.index)
        self.state = self.RECORDING
        self.current_layer = self.layers = 1

    def overdub(self):
        self.looper.channel.overdub(self.index)
        self.state = self.OVERDUBBING
        self.current_layer += 1
        self.layers = self.current_layer

    def pause(self):
        self.looper.channel.pause(self.index)
        self.state = self.PAUSED

    def undo_all(self):
        self.looper.channel.undo_all(self.index)
        self.state = self.WAIT
        self.current_layer = 0

    def undo(self):
        self.looper.channel.undo(self.index)
        if self.current_layer > 0:
            current = self.current_layer
            new = current - 1
            self.current_layer = new if current > 0 else 0

            # SooperLooper doesn't undo the base layer when you call 'undo',
            # only subsequent layers, so this implements that
            if new == 0:
                self.undo_all()

    def redo(self):
        if self.current_layer < self.layers:
            self.looper.channel.redo(self.index)
            self.current_layer += 1
            self.state = Loop.PLAYBACK

    def toggle_pause(self):
        self.looper.channel.pause(self.index)
        relf.state = \
            self.PLAYBACK if self.state == self.PAUSED else self.PAUSED

    def stop_record_and_discard(self):
        """
        If we are RECORDING or OVERDUBBING then stop and discard the layer
        Otherwise, do nothing.
        """
        if self.state in [self.RECORDING, self.OVERDUBBING]:
           self.play_record_or_overdub()  # will toggle to playback
           self.undo()                    # discard last layer
