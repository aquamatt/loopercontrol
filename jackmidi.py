#!/usr/bin/env python3
#
# dependencies (pip3 installable):
#
# - cffi
# - JACK-Client
#
# To get ALSA midi clients appearing in JACK Midi connections use:
#
# $ a2jmidid -e
#
# But can, alternatively, wire output of this to System:midi_playback
# and in ALSA window, write from Midi Through to Sooperlooper.
#
# Other applications that appear in the Jack MIDI box, like Guitarix,
# can be connected to directly
#
# To have System MIDI Capture input/output in the MIDI tab (which allows sending
# through to the ALSA midi sequencer) it is essential that in the JACK settings
# the MIDI driver be set to 'seq'
#
# MIDI event table:
# https://www.onicos.com/staff/iz/formats/midi-event.html
#
# This helped understand how to send midi events - notably that it has to
# happen on the midi thread:
#
# https://github.com/spatialaudio/jackclient-python/issues/47
#
import jack
import queue
import time


def show_ports():
    print("\n".join(client.get_ports()))


midi_msg_q = queue.Queue()

client = jack.Client("MyClient")
midi_out = client.midi_outports.register("midi_out")
midi_in = client.midi_inports.register("midi_in")


@client.set_process_callback
def process(frames):
    global midi_msg_q
    midi_out.clear_buffer()
    try:
        while True:
            midi_msg = midi_msg_q.get(block=False)
            print("Channel {}: note {}, velocity {}".format(*midi_msg))
            midi_out.write_midi_event(0, midi_msg)
    except queue.Empty:
        pass

client.activate()

def midi_note_on(channel, midi_note):
    '''Transmit a MIDI "note on" message'''
    midi_msg_q.put((0x90 | channel, midi_note, 127))

while True:
    midi_note_on(0, 60)
    time.sleep(2)
