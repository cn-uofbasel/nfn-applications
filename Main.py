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

    def on_data(self, interest, data):
        self.finish_with_result(TestResult.Success)
        pass

    def on_timeout(self, interest):
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

# class UITest(Test):
#     def setup(self):
#         self.process_interval = 0
#         self.update_interval = 0
#         self.network = SerialNetwork(6)
#         app = QApplication(sys.argv)
#         w = QWidget()
#         w.resize(250, 150)
#         w.move(300, 300)
#         w.setWindowTitle('Simple')
#         w.show()
#         QTimer.singleShot(1000, self.timer_fired)
#         sys.exit(app.exec_())
#     def timer_fired(self):
#         print("Timer")
#         QTimer.singleShot(1000, self.timer_fired)
#         self.network.process_events()

# Util.compile_ccn_lite()
# Util.compile_nfn_scala()

Config.ccn_log_level = CCNLogLevel.Error

# App.setup()
# App.app = QApplication(sys.argv)

# def tick():
#     print("Tick")
#
# app = QApplication(sys.argv)
# process_timer = QTimer()
# process_timer.timeout.connect(tick)
# process_timer.start(1000)
# app.exec_()


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
RedirectTest().start()
# SimulationTest().start()
# IntermediateTest().start()
# NBodyTest().start()
# UITest().start()

# SimulationRenderTest(enable_ui=True).start()

# Util.clean_output_folder()

# def timer_fired():
#     print("Timer fired!")




# asyncio.get_event_loop().close()



