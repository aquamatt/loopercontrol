"""
Command set for interfacing with MIDI controlled systems
"""
import queue

import jack

from base import BaseCommandSet


# MIDI system setup
midi_msg_q = queue.Queue()

client = jack.Client("PedalBoard")
midi_out = client.midi_outports.register("midi_out")

@client.set_process_callback
def process(frames):
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

# End MIDI system setup


class MidiCommandSet(BaseCommandSet):
    """
    Handle commands from *both* stomp box and keyboard for MIDI.

    Handler functions combining handlers for keyboard and stomp nbox
    input which output MIDI notes to JACK and can thus, through the JACK
    patch panel, be wired to any MIDI controllable client such as
    looper, drum machine or synth.
    """
    def handle_0(self):
        midi_note_on(0, 60)

    def handle_double_0(self):
        midi_note_on(0, 61)

    def handle_1(self):
        midi_note_on(0, 62)

    def handle_double_1(self):
        midi_note_on(0, 63)

    def handle_2(self):
        midi_note_on(0, 64)

    def handle_double_2(self):
        midi_note_on(0, 65)
