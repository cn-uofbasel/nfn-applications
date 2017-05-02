from Test import *
from Network import *

from IntermediateTest import IntermediateTest
from NBodyTest import NBodyTest

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


class FetchServiceTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_NBody_SimulationService"
        self.network.nodes[0].send_interest(name)


class ChunkTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_ChunkTest/(@x call 1 x)/NFN"
        self.network.nodes[0].send_interest(name)


class ChainTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        name = "/node4/nfn_service_ChainIntermediates/(@x call 3 x '%2Fnode6%2Fnfn_service_IntermediateTest(@x call 1 x)' '%2Fnode6%2Fnfn_service_IntermediateTest(@x call 1 x)')/NFN"
        self.network.nodes[0].send_interest(name)


class SimulationTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        basename = "/node4/nfn_service_Echo/(@x call 2 x (call 1 %2Fnode6%2Fnfn_service_NBody_SimulationService))"
        self.network.nodes[0].send_interest(basename + "/NFN")



#Util.compile_ccn_lite()
#Util.compile_nfn_scala()

# StopTest().start()
# EchoTest().start()
# SimpleTest().start()
# NestedTest().start()
# FetchServiceTest().start()
# ChunkTest().start()
ChainTest().start()
# IntermediateTest().start()
# NBodyTest().start()


# Util.clean_output_folder()




