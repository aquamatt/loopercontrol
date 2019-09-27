"""
Base classes
"""
import settings


class BaseCommandSet(object):
    """
    Sub-class to create a command set by adding methods named
    handle_<key> to it.
    """
    def __init__(self, looper, input_handler=None):
        self.handler = input_handler
        self.looper = looper

        fns = type(self).__dict__
        self.commands = {k: v
                         for (k, v) in fns.items() if k.startswith("handle_")}
        if settings.DEBUG:
            print("Commands: \n : {}".format("\n : ".join(self.commands.keys())))

    def handle(self, command):
        """
        Execute function handler for given command if available
        """
        fn = "handle_{}".format(command)
        try:
            self.commands[fn](self)
        except KeyError:
            if settings.DEBUG:
                print("Could not find command: {}".format(command))


class BaseInputHandler(object):
    """
    Base class for Input handlers, be the input a keyboard, stomp box,
    or something else.
    """

    def __init__(self, command_set):
        self.command_set = command_set
        self.command_set.handler = self

    def start(self):
        raise NotImplementedError
