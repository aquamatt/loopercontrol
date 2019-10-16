import socket
import sys

from base import BaseInputHandler
from base import BaseCommandSet
import settings


BUFFER_SIZE = 256


def _create_socket():
    """
    Setup UDP socket
    """
    _socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM)

    host = getattr(settings, "UDP_HOST", "127.0.0.1")
    port = getattr(settings, "UDP_PORT", 21974)
    if settings.DEBUG:
        print("UDP connection on {}:{}".format(host, port))

    return _socket, host, port


class BridgeInputHandler(BaseInputHandler):
    """
    An input handler that listens for commands sent over as UDP
    datagrams. Reflected into the supplied commandset.
    """
    def start(self):
        self.socket, host, port = _create_socket()
        self.socket.bind((host, port))

        while(True):
            bytesAddressPair = self.socket.recvfrom(BUFFER_SIZE)
            command = bytesAddressPair[0].decode()

            if settings.DEBUG:
                print("Message received over bridge: {}".format(command))
            self.command_set.handle(command)


class BridgeCommandSet(BaseCommandSet):
    """
    An input handler that receives from the stomp buttons and sends
    commands over the UDP connection
    """
    def __init__(self, *args, **kwargs):
        # as we're a bridge we don't need to do the initialisation in
        # the base class
        self.socket, host, port = _create_socket()
        self.address = (host, port)

    def handle(self, command):
        """
        Get command from the input handler and pitch it over to the server
        """
        msg = str.encode(command)
        if settings.DEBUG:
            print("Sending message over bridge: {}".format(command))
        self.socket.sendto(msg, self.address)
