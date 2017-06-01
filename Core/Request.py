
import threading

from pyndn import Name, Interest, Blob, Data

from Util.Util import *

class Request(object):
    def __init__(self, node, name, timeout=30, intermediate_interval=1, on_data=None, on_timeout=None, on_intermediate=None):
        # TODO: allow interest to be a string uri or an Interest object and convert to self.uri AND self.interest in both cases.
        self.node = node
        self.name = name
        self.interest = Interest(Name(name))
        self.timeout = timeout
        self.intermediate_interval = intermediate_interval
        self.later_timer = None

        self.on_data = on_data if on_data is not None else self.on_data_fallback
        self.on_timeout = on_timeout if on_timeout is not None else self.on_timeout_fallback
        self.on_intermediate = on_intermediate

        self.redirect = None
        self.final_segment = None
        self.highest_requested_segment = -1
        self.pending_segments = set()
        self.segments = {}

        self.highest_gim_sent = -1
        self.highest_gim_received = -1
        self.cim_timer = None
        self.cim_name = self.name
        if self.cim_name.endswith("/NFN"):
            self.cim_name = self.cim_name[:-4] + "/R2C/CIM/NFN"

    def send(self):
        if self.timeout is None:
            self.interest.setInterestLifetimeMilliseconds(None)
        else:
            self.interest.setInterestLifetimeMilliseconds(1000 * self.timeout)
        self.node.face.expressInterest(self.interest, self.on_interest_data, self.on_interest_timeout)
        Log.info("Sent interest '{}'".format(self.name))
        if self.intermediate_interval > 0 and self.on_intermediate is not None:
            self.cim_timer = threading.Timer(self.intermediate_interval, self.cim_timer_fired)
            self.cim_timer.start()

    def send_later(self, delay):
        self.later_timer = threading.Timer(delay, self.send)
        self.later_timer.start()

    def cancel(self):
        if self.later_timer is not None:
            self.later_timer.cancel()
        if self.cim_timer is not None:
            self.cim_timer.cancel()

    def cim_timer_fired(self):
        Request(self.node, self.cim_name, timeout=self.intermediate_interval, on_data=self.on_cim_data).send()
        self.cim_timer = threading.Timer(self.intermediate_interval, self.cim_timer_fired)
        self.cim_timer.start()

    def on_cim_data(self, request, data):
        content = data.getContent().toRawStr()
        if not content:
            Log.info("No intermediate results available yet.")
            return
        highest_available = int(content)
        for i in range(self.highest_gim_sent + 1, highest_available + 1):
            self.request_intermediate(i)
        self.highest_gim_sent = highest_available

    def request_intermediate(self, index):
        gim_uri = self.name
        if gim_uri.endswith("/NFN"):
            gim_uri = gim_uri[:-4] + "/R2C/GIM " + str(index) + "/NFN"
        Request(self.node, gim_uri, on_data=self.on_intermediate_data).send()

    def on_intermediate_data(self, request, data):
        index = Util.get_intermediate_index(request.interest)
        if index < 0:
            Log.error("Invalid intermediate result.")
            return

        if index < self.highest_gim_received:
            Log.warn("Received old intermediate out of order. Ignore.")
            return

        self.highest_gim_received = index

        self.on_intermediate(self, index, data)

    def on_interest_data(self, interest, data):
        if self.cim_timer is not None:
            self.cim_timer.cancel()

        content = data.getContent().toRawStr()
        redirectPrefix = "redirect:"
        if content.startswith(redirectPrefix):
            name = content[len(redirectPrefix):]
            self.redirect = Interest(Name(name))
            Log.info("Received redirect for interest '{}' -> '{}':\n{}"
                  .format(Util.interest_to_string(interest), Util.interest_to_string(self.redirect), urllib.parse.unquote(content)))
            self.request_next_segments()
        else:
            Log.info("Received data for interest '{}':\n{}".format(Util.interest_to_string(interest), urllib.parse.unquote(content)))
            self.on_data(self, data)

    def on_interest_timeout(self, interest):
        Log.warn("Interest timed out '{}'".format(Util.interest_to_string(interest)))
        self.on_timeout(self)
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
        Log.info("Sent segment interest '{}'".format(Util.interest_to_string(interest)))
        self.node.face.expressInterest(interest, self.on_segment_data, self.on_segment_timeout)

    def on_segment_data(self, interest, data):
        if self.final_segment is None:
            self.final_segment = data.getMetaInfo().getFinalBlockId().toNumber()

        content = data.getContent()
        if not content.isNull():
            size = content.size()
            name = interest.getName()
            segmentNumber = Util.find_segment_number(name)
            Log.info("Received data ({} bytes) for segment '{}'.".format(size, Util.interest_to_string(interest)))
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
            Log.warn("Received EMPTY data for segment '{}'.".format(Util.interest_to_string(interest)))

    def on_segment_timeout(self, interest):
        Log.warn("Interest timed out '{}'".format(Util.interest_to_string(interest)))
        self.on_timeout(self)

    def handle_completion(self):
        content = bytearray()
        for i in sorted(self.segments):
            segment = self.segments[i]
            content.extend(segment.getContent().buf())
        interest = Interest(Name(self.name))
        blob = Blob(content)
        size = blob.size()
        Log.info("Received all segments ({} bytes) for interest '{}':\n{}"
              .format(size, Util.interest_to_string(interest), urllib.parse.unquote(blob.toRawStr())))
        data = Data(interest.getName())
        data.setContent(blob)
        self.on_data(self, data)

    def on_data_fallback(self, request, data):
        pass

    def on_timeout_fallback(self, request):
        pass

    def on_intermediate_fallback(self, request, index, data):
        pass