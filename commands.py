import sys

from looper import BaseCommandSet


class KeyCommandSet(BaseCommandSet):
    def handle_double_SPACE(self):
        """
        Stop playback of selected loop. The first tap of the double tap would, if
        playback was the prior state, have started recording/overdubbing. We
        therefore stop that and discard the fraction of a second long layer first
        before pausing everything.

        If recording/overdubbing was happening prior to the double tap, the first
        tap would have stopped that, and this will only pause everything, retaining
        the layer that we had intentionally recorded.
        """
        self.looper.selected.stop_record_and_discard()
        self.looper.selected.pause()

    def handle_SPACE(self):
        """
        Toggle though states
        """
        self.looper.selected.play_record_or_overdub()

    def handle_DOWN(self):
        self.looper.select_next()

    def handle_UP(self):
        self.looper.select_previous()

    def handle_R(self):
        self.looper.selected.record()

    def handle_U(self):
        self.looper.selected.undo_all()

    def handle_u(self):
        self.looper.selected.undo()

    def handle_r(self):
        self.looper.selected.redo()

    def handle_q(self):
        # osc_terminate()
        self.handler.flush_keys()
        self.handler.set_echo()
        sys.exit(0)


class StompCommandSet(BaseCommandSet):
    def handle_0(self):
        self.looper.selected.play_record_or_overdub()

    def handle_double_0(self):
        """
        Stop playback of selected loop. The first tap of the double tap would, if
        playback was the prior state, have started recording/overdubbing. We
        therefore stop that and discard the fraction of a second long layer first
        before pausing everything.

        If recording/overdubbing was happening prior to the double tap, the first
        tap would have stopped that, and this will only pause everything, retaining
        the layer that we had intentionally recorded.
        """
        self.looper.selected.stop_record_and_discard()
        self.looper.selected.pause()
