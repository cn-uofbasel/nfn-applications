from TestSuite import *
from Network import *
from Request import *
from LoremIpsum import *

from random import randint


class MobileServerTest(Test):
    def __init__(self):
        super().__init__()
        self.current_prefix = None
        self.timer = None

    def setup(self):
        self.network = StarNetwork(4, 2)
        identifier = "test"
        name = "/hub/nfn_service_Waypoint/(@x call 2 x '" + identifier + "')/NFN"
        Request(self.network.spokes[0][0], name, on_intermediate=self.on_waypoint_intermediate).send()
        self.timer = threading.Timer(1, self.timer_fired)
        self.timer.start()
        signal.signal(signal.SIGINT, self.sigint_handler)

    def sigint_handler(self, *args):
        if self.timer is not None:
            self.timer.cancel()

    def on_waypoint_intermediate(self, request, index, data):
        self.current_prefix = data.getContent().toRawStr()
        if not self.current_prefix.endswith("/"):
            self.current_prefix += "/"

    def timer_fired(self):
        if self.current_prefix is not None:
            self.send_interest()
        self.timer = threading.Timer(1, self.timer_fired)
        self.timer.start()

    def send_interest(self):
        word_count = randint(1, LoremIpsum.max_length - 1)
        words = LoremIpsum.random_words(word_count)
        name = self.current_prefix + "(@x call 2 x '" + words + "')/NFN"
        Request(self.network.spokes[0][0], name, on_data=self.on_mobile_data, on_timeout=self.on_mobile_timeout).send()

    def on_mobile_data(self, request, data):
        # Util.log_on_data(request.interest, data)
        pass

    def on_mobile_timeout(self, request):
        Log.warn("Interest to mobile server timed out!")
