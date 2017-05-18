from Network import *
from Test import *
from Util import *


class IntermediateTest(Test):
    def __init__(self):
        super().__init__()
        self.highest_request = -1

    def setup(self):
        self.update_interval = 1
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_IntermediateTest/(@x call 1 x)/NFN"
        self.network.nodes[0].send_interest(name)

    def update(self):
        name = "/node4/nfn_service_IntermediateTest/(@x call 1 x)/R2C/CIM/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_cim)

    def on_cim(self, interest, data):
        content = data.getContent().toRawStr()
        highest_available = int(content)
        Log.info("Highest available intermediate: " + str(highest_available))
        for i in range(self.highest_request + 1, highest_available + 1):
            self.request_intermediate(i)
        self.highest_request = highest_available

    def request_intermediate(self, index):
        name = "/node4/nfn_service_IntermediateTest/(@x call 1 x)/R2C/GIM " + str(index) + "/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_intermediate)

    def on_intermediate(self, interest, data):
        content = data.getContent().toRawStr()
        Log.info("Received data for intermediate interest '{}':\n{}".format(Util.interest_to_string(interest),
                urllib.parse.unquote(content)))