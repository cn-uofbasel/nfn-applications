from Test import *
from Network import *
from Util import *
import urllib


class SimpleTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        self.network.nodes[0].send_interest("/node4/nfn_service_WordCount/(@x call 2 x 'foo bar')/NFN")


class EchoTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        basename = "/node4/nfn_service_Echo/(@x call 2 x 'foo bar')"
        self.network.nodes[0].send_interest(basename + "/NFN")


class StopTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        basename = "/node4/nfn_service_IntermediateTest/(@x call 2 x 'foo bar')"
        self.network.nodes[0].send_interest(basename + "/NFN")
        self.network.nodes[0].send_interest_later(3, basename + "/R2C/CANCEL/NFN")


class NestedTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        basename = "call 2 %2Fnode4%2Fnfn_service_WordCount (call 2 %2Fnode6%2Fnfn_service_WordCount 'foo bar')"
        self.network.nodes[0].send_interest(basename + "/NFN")


class NBodyTest(Test):
    def setup(self):
        self.network = ForkNetwork(stem_length=3, branch_count=3, branch_length=3)
        basename = "/nodeAS/nfn_service_NBody_SimulationService/(@x call 1 x)"
        self.network.nodes[0].send_interest(basename + "/NFN", on_data=self.on_sim_data)

    def on_sim_data(self, interest, data):
        content = urllib.parse.unquote(data.getContent().toRawStr())
        print("Simulation data received.")
        print(content)
        echo = "/nodeBS/nfn_service_Echo/(@x call 2 x (call 1 %2FnodeAS%2Fnfn_service_NBody_SimulationService))"
        self.network.nodes[0].send_interest(echo + "/NFN", on_data=self.on_render_data)

    def on_render_data(self, interest, data):
        content = urllib.parse.unquote(data.getContent().toRawStr())
        print("Render data received.")
        print(content)



Util.compile_ccnl()

# StopTest().start()
# EchoTest().start()
# SimpleTest().start()
NestedTest().start()
# NBodyTest().start()



Util.clean_output_folder()


