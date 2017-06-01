from Core.Network import *
from Core.Request import *
from Core.TestSuite import *


class PubSubTest(Test):
    def setup(self):
        broker = "/node4/nfn_service_PubSubBroker"
        self.network = ThesisNetwork()
        identifier = "thread"
        name = broker + "/(@x call 2 x '" + identifier + "')/NFN"
        Request(self.network.nodes[0], name).send()
    # def update(self):
    #     name = self.msg + "/" + str(self.msg_count)
    #     data = "this is published data #" + str(self.msg_count)
    #     self.network.nodes[5].add_content(name, data.encode())
    #     self.msg_count += 1
    # def on_intermediate(self, request, index, data):
    #     Log.info("Received intermediate {}".format(index))
    # def on_data(self, request, data):
    #     self.finish_with_result(TestResult.Success)