from Network import *
from Test import *
from Util import *


class SimulationRenderTest(Test):
    def __init__(self):
        super().__init__()
        self.highest_request = -1
        self.max_duration = 30
        self.basename = "/node4/nfn_service_NBody_SimulationRenderService/(@x call 1 x)"

    def setup(self):
        self.update_interval = 1
        self.network = ThesisNetwork()
        name = self.basename + "/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_data)

    def update(self):
        name = self.basename + "/R2C/CIM/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_cim)

    def on_cim(self, interest, data):
        content = data.getContent().toRawStr()
        if not content:
            print("No intermediate results available yet.")
            return
        highest_available = int(content)
        print("Highest available intermediate: " + str(highest_available))
        for i in range(self.highest_request + 1, highest_available + 1):
            self.request_intermediate(i)
        self.highest_request = highest_available

    def request_intermediate(self, index):
        name = self.basename + "/R2C/GIM " + str(index) + "/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_intermediate)

    def on_intermediate(self, interest, data):
        content = data.getContent().toRawStr()
        print("Received data for intermediate interest '{}':\n{}".format(Util.interest_to_string(interest),
                urllib.parse.unquote(content)))

    def on_data(self, interest, data):
        content = data.getContent().toRawStr()
        print("Received data for interest '{}':\n{}".format(Util.interest_to_string(interest),
                urllib.parse.unquote(content)))
        self.finish_with_result(TestResult.Success)
