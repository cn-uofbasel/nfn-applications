import asyncio
import urllib
import atexit
import socket
from Util import *

from Log import *
from pyndn import Name, Interest, Face
from pyndn.transport.udp_transport import UdpTransport


class Node(object):
    def __init__(self, port, launch=False):
        self.ip = "127.0.0.1"
        self.port = port
        self.description = self.ip + ":" + str(self.port)
        self.interval = 1
        self.face = None
        self.connected = False
        self.process = None
        if launch:
            self.launch()

    def launch(self):
        self.check_port()
        atexit.register(self.shutdown)
        if not self.connected:
            self.connect()

    def shutdown(self):
        self.process.terminate()
        atexit.unregister(self.shutdown)
        Log.info("Terminated node " + self.description)

    def check_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((self.ip, self.port))
        except socket.error as e:
            if e.errno == 98:
                Log.error("Port is already in use")
            else:
                Log.error(e)
            raise e
        s.close()

    def connect(self):
        if self.face is None:
            connection_info = UdpTransport.ConnectionInfo(self.ip, self.port)
            transport = UdpTransport()
            self.face = Face(transport, connection_info)
            self.connected = True

    def process_events(self):
        if self.face is not None:
            self.face.processEvents()
