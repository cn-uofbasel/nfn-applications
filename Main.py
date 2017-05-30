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


class SimpleTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        Request(self.network.nodes[0], "/node4/nfn_service_WordCount/(@x call 2 x 'foo bar lorem ipsum dolor')/NFN", on_data=self.on_data).send()
    def on_data(self, request, data):
        result = TestResult.Success if int(data.getContent().toRawStr()) is 5 else TestResult.Failure
        self.finish_with_result(result)


class SerialTest(Test):
    def setup(self):
        self.network = SerialNetwork(6)
        Request(self.network.nodes[0], "/node6/nfn_service_WordCount/(@x call 2 x 'foo bar')/NFN", on_data=self.on_data).send()
    def on_data(self, request, data):
        result = TestResult.Success if int(data.getContent().toRawStr()) is 2 else TestResult.Failure
        self.finish_with_result(result)


class EchoTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        basename = "/node4/nfn_service_Echo/(@x call 2 x 'foo bar')"
        Request(self.network.nodes[0], basename + "/NFN", on_data=self.on_data).send()
    def on_data(self, request, data):
        result = TestResult.Success if int(data.getContent().toRawStr()) is "foo bar" else TestResult.Failure
        self.finish_with_result(result)


class FetchContentTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        Request(self.network.nodes[0], "/node4/nfn_service_FetchContentTest/(@x call 2 x 'foo bar')/NFN", on_data=self.on_data).send()
    def on_data(self, request, data):
        result = TestResult.Success if 1 is 2 else TestResult.Failure
        self.finish_with_result(result)


class StopTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        basename = "/node4/nfn_service_IntermediateTest/(@x call 2 x 'foo bar')"
        Request(self.network.nodes[0], basename + "/NFN").send()

        # TODO: implement send later with requests
        self.network.nodes[0].send_interest_later(3, basename + "/R2C/CANCEL/NFN")


class NestedTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        basename = "call 2 %2Fnode4%2Fnfn_service_WordCount (call 2 %2Fnode6%2Fnfn_service_WordCount 'foo bar')"
        Request(self.network.nodes[0], basename + "/NFN").send()


class FetchServiceTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_NBody_SimulationService"
        Request(self.network.nodes[0], name).send()


class ChunkTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_ChunkTest/(@x call 1 x)/NFN"
        Request(self.network.nodes[0], name).send()


class ChainTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        nbody = "/node6/nfn_service_NBody_SimulationService/(@x call 1 x)/NFN"
        render = "/node6/nfn_service_NBody_RenderService/(@x call 2 x ())/NFN"
        nbody_escaped = nbody.replace("/", "%2F")
        render_escaped = render.replace("/", "%2F")
        name = "/node4/nfn_service_ChainIntermediates/(@x call 3 x '{0}' '{1}')/NFN".format(nbody_escaped, nbody_escaped)
        Request(self.network.nodes[0], name).send()


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
        Request(self.network.nodes[0], name, on_data=self.on_data).send()
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


class GetFromLocalCacheTest(Test):
    def setup(self):
        self.network = SimpleNetwork(4)
        name = "/node4/nfn_service_ControlRequestTest/(@x call 2 x 'test')/NFN"
        Request(self.network.nodes[0], name).send()
        name = "/node4/nfn_service_ControlRequestTest/(@x call 2 x 'test')/R2C/CTRL 1/NFN"
        Request(self.network.nodes[0], name).send_later(3)
        name = "/node4/nfn_service_ControlRequestTest/(@x call 2 x 'test')/R2C/CTRL 3/NFN"
        Request(self.network.nodes[0], name).send_later(5)


class PubSubTest(Test):
    def __init__(self):
        super().__init__()
        self.broker = "/node4/nfn_service_PubSubBroker"
        self.msg = "/node6/PubSubMsg"
        self.msg_count = 0
    def setup(self):
        self.network = SerialNetwork(6)
        identifier = "thread"
        #param = self.msg.replace("/", "%2F")
        name = self.broker + "/(@x call 2 x '" + identifier + "')/NFN"
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




# Util.compile_ccn_lite()
# Util.compile_nfn_scala()

# Config.ccn_log_level = CCNLogLevel.Error
# Config.nfn_log_level = NFNLogLevel.Normal

# Log.level = LogLevel.Error

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
# AddToCacheTest().start()
# GetFromLocalCacheTest().start()
PubSubTest().start()

# Util.clean_output_folder()

# Util.write_binary_content("/node6/PubSubMsg/0", "testdata".encode())


# node = NFNNode(9004, launch=False)
# node.connect()
# broker = "/node4/nfn_service_PubSubBroker"
# msg = "/node6/PubSubMsg"
# param = msg.replace("/", "%2F")
# name = broker + "/(@x call 2 x '" + param + "')/NFN"
# Request(node, name).send()


