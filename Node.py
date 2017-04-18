import asyncio
import urllib
import atexit

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
        atexit.register(self.shutdown)

    def shutdown(self):
        self.process.terminate()
        print("Terminated node " + self.description)

    def connect(self):
        if self.face is None:
            connection_info = UdpTransport.ConnectionInfo(self.ip, self.port)
            transport = UdpTransport()
            self.face = Face(transport, connection_info)
            self.connected = True

    def process_events(self):
        if self.face is not None:
            self.face.processEvents()

    @staticmethod
    def interest_to_string(interest):
        uri = interest.getName().toUri()
        cmps = uri.split("/")
        last_component = cmps[-1]
        is_segment = last_component.startswith("%00")
        if is_segment:
            cmps.pop()
        string = urllib.parse.unquote("/".join(cmps))
        if is_segment:
            string += "/" + last_component
        return string

    def on_data(self, interest, data):
        content = data.getContent().toRawStr()
        print("Received data for interest '{}':\n{}".format(self.interest_to_string(interest),
                                                            urllib.parse.unquote(content)))
        pass

    def on_timeout(self, interest):
        print("Interest timed out '{}'".format(self.interest_to_string(interest)))
        pass

    def send_interest(self, uri, on_data=None, on_timeout=None, timeout=30):
        if not self.connected:
            self.connect()
        if not on_data:
            on_data = self.on_data
        if not on_timeout:
            on_timeout = self.on_data
        name = Name(uri)
        interest = Interest(name)
        interest.setInterestLifetimeMilliseconds(1000 * timeout)
        self.face.expressInterest(interest, on_data, on_timeout)
        print("Sent interest '{}'".format(self.interest_to_string(interest)))

    def send_interest_later(self, delay, uri, on_data=None, on_timeout=None, timeout=30):
        loop = asyncio.get_event_loop()
        loop.call_later(delay, self.send_interest, uri, on_data, on_timeout, timeout)


