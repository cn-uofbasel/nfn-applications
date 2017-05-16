import asyncio
import urllib
import atexit
import socket
from Util import *

from pyndn import Name, Interest, Blob, Data

class Request(object):
    def __init__(self, node, interest, timeout=30, on_data=None, on_timeout=None):
        self.node = node
        self.uri = interest
        self.timeout = timeout

        self.on_data = on_data if on_data is not None else self.on_data_fallback
        self.on_timeout = on_timeout if on_timeout is not None else self.on_timeout_fallback

        self.redirect = None
        self.final_segment = None
        self.highest_requested_segment = -1
        self.pending_segments = set()
        self.segments = {}

    def send(self):
        name = Name(self.uri)
        interest = Interest(name)
        interest.setInterestLifetimeMilliseconds(1000 * self.timeout)
        self.node.face.expressInterest(interest, self.on_interest_data, self.on_interest_timeout)
        print("Sent interest '{}'".format(Util.interest_to_string(interest)))

    def on_interest_data(self, interest, data):
        content = data.getContent().toRawStr()
        redirectPrefix = "redirect:"
        if content.startswith(redirectPrefix):
            name = content[len(redirectPrefix):]
            self.redirect = Interest(Name(name))
            print("Received redirect for interest '{}' -> '{}':\n{}"
                  .format(Util.interest_to_string(interest), Util.interest_to_string(self.redirect), urllib.parse.unquote(content)))
            self.request_next_segments()
        else:
            print("Received data for interest '{}':\n{}".format(Util.interest_to_string(interest), urllib.parse.unquote(content)))
            self.on_data(self, data)

    def on_interest_timeout(self, interest):
        print("Interest timed out '{}'".format(Util.interest_to_string(interest)))
        pass

    def request_next_segments(self):
        if self.final_segment is None:
            self.request_segment(self.highest_requested_segment + 1)
        else:
            while self.highest_requested_segment < self.final_segment:
                self.request_segment(self.highest_requested_segment + 1)

    def request_segment(self, index):
        if index > self.highest_requested_segment:
            self.highest_requested_segment = index
        self.pending_segments.add(index)
        segment_name = Name(self.redirect.getName())
        segment_name.appendSegment(index)
        interest = Interest(segment_name)
        print("Sent segment interest '{}'".format(Util.interest_to_string(interest)))
        self.node.face.expressInterest(interest, self.on_segment_data, self.on_segment_timeout)

    def on_segment_data(self, interest, data):
        if self.final_segment is None:
            self.final_segment = data.getMetaInfo().getFinalBlockId().toNumber()

        content = data.getContent()
        if not content.isNull():
            size = content.size()
            name = interest.getName()
            segmentNumber = Util.find_segment_number(name)
            print("Received data ({} bytes) for segment '{}'.".format(size, Util.interest_to_string(interest)))
            self.segments[segmentNumber] = data
            self.pending_segments.remove(segmentNumber)
            allSegmentsReceived = self.final_segment is not None \
                                  and self.highest_requested_segment >= int(self.final_segment) \
                                  and self.pending_segments.__len__() == 0
            if allSegmentsReceived:
                self.handle_completion()
            else:
                self.request_next_segments()
        else:
            print("Received EMPTY data for segment '{}'.".format(Util.interest_to_string(interest)))

    def on_segment_timeout(self, interest):
        print("Interest timed out '{}'".format(Util.interest_to_string(interest)))

    def handle_completion(self):
        content = bytearray()
        for i in sorted(self.segments):
            segment = self.segments[i]
            content.extend(segment.getContent().buf())
        interest = Interest(Name(self.uri))
        blob = Blob(content)
        size = blob.size()
        data = Data(interest.getName())
        data.setContent(blob)
        self.on_data(self, data)
        print("Received all segments ({} bytes) for interest '{}':\n{}"
              .format(size, Util.interest_to_string(interest), urllib.parse.unquote(blob.toRawStr())))

    def on_data_fallback(self, request, data):
        pass

    def on_timeout_fallback(self, request):
        pass