from Test import *
from TestSuite import *
from Network import *
from Util import *
from Config import *
from Request import *

from IntermediateTest import IntermediateTest
from NBodyTest import NBodyTest
from SimulationRenderTest import SimulationRenderTest

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer

class App(object):
    app = None
    # @staticmethod
    # def setup():
    #     App.app = QApplication(sys.argv)


class SimpleTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        self.network.nodes[0].send_interest("/node4/nfn_service_WordCount/(@x call 2 x 'foo bar lorem ipsum dolor')/NFN", on_data=self.on_data)
    def on_data(self, interest, data):
        Util.log_on_data(interest, data)
        result = TestResult.Success if int(data.getContent().toRawStr()) is 5 else TestResult.Failure
        self.finish_with_result(result)


class SerialTest(Test):
    def setup(self):
        self.network = SerialNetwork(6)
        self.network.nodes[0].send_interest("/node6/nfn_service_WordCount/(@x call 2 x 'foo bar')/NFN", on_data=self.on_data)
    def on_data(self, interest, data):
        Util.log_on_data(interest, data)
        result = TestResult.Success if int(data.getContent().toRawStr()) is 2 else TestResult.Failure
        self.finish_with_result(result)


class EchoTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        basename = "/node4/nfn_service_Echo/(@x call 2 x 'foo bar')"
        self.network.nodes[0].send_interest(basename + "/NFN", on_data=self.on_data)
    def on_data(self, interest, data):
        Util.log_on_data(interest, data)
        result = TestResult.Success if int(data.getContent().toRawStr()) is "foo bar" else TestResult.Failure
        self.finish_with_result(result)


class FetchContentTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        self.network.nodes[0].send_interest("/node4/nfn_service_FetchContentTest/(@x call 2 x 'foo bar')/NFN", on_data=self.on_data)
    def on_data(self, interest, data):
        Util.log_on_data(interest, data)
        result = TestResult.Success if 1 is 2 else TestResult.Failure
        self.finish_with_result(result)


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
        nbody = "/node6/nfn_service_NBody_SimulationService/(@x call 1 x)/NFN"
        render = "/node6/nfn_service_NBody_RenderService/(@x call 2 x ())/NFN"
        nbody_escaped = nbody.replace("/", "%2F")
        render_escaped = render.replace("/", "%2F")
        name = "/node4/nfn_service_ChainIntermediates/(@x call 3 x '{0}' '{1}')/NFN".format(nbody_escaped, nbody_escaped)
        self.network.nodes[0].send_interest(name)


class RedirectTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_ChunkTest/(@x call 1 x)/NFN"
        Request(self.network.nodes[0], name, on_data=self.on_data, on_timeout=self.on_timeout).send()

    def on_data(self, request, data):
        self.finish_with_result(TestResult.Success)
        pass

    def on_timeout(self, request):
        self.finish_with_result(TestResult.Failure)
        pass


class SimulationTest(Test):
    def setup(self):
        self.network = SerialNetwork(6)
        name = "/node6/nfn_service_NBody_SimulationService/(@x call 2 x 'foo bar')/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_data)
    def on_data(self, interest, data):
        Util.log_on_data(interest, data)
        result = TestResult.Success
        self.finish_with_result(result)


class AddToCacheTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/SimpleContentTest"
        data = "this is a test content".encode()
        time.sleep(1)
        self.network.nodes[3].add_content(name, data)
        time.sleep(1)
        Request(self.network.nodes[0], name, on_data=self.on_data).send()
    def on_data(self, request, data):
        self.finish_with_result(TestResult.Success)


class PubSubTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        name = "/node4/nfn_service_PubSubBroker/(@x call 2 x '%2Fnode6%2FPubSubMsg')/NFN"
        Request(self.network.nodes[0], name, on_data=self.on_data, on_intermediate=self.on_intermediate).send()
    def on_intermediate(self, request, index, data):
        print("Received intermediate {}".format(index))
        Util.log_on_data(request.interest, data)
    def on_data(self, request, data):
        Util.log_on_data(request.interest, data)
        self.finish_with_result(TestResult.Success)


# Util.compile_ccn_lite()
# Util.compile_nfn_scala()

# Config.ccn_log_level = CCNLogLevel.Error

# TestSuite([EchoTest(), SimpleTest(), SerialTest(), SimulationTest()]).start()

# StopTest().start()
# EchoTest().start()
# SimpleTest().start()
# SerialTest().start()
# FetchContentTest().start()
# NestedTest().start()
# FetchServiceTest().start()
# ChunkTest().start()
# ChainTest().start()
# RedirectTest().start()
# SimulationTest().start()
# IntermediateTest().start()
# NBodyTest().start()
# UITest().start()
# SimulationRenderTest(enable_ui=True).start()
AddToCacheTest().start()
# PubSubTest().start()

# Util.clean_output_folder()

# Util.write_binary_content("/node6/PubSubMsg/0", "testdata".encode())
