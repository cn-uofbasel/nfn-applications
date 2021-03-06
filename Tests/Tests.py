from Core.Network import *
from Core.Request import *
from Core.TestSuite import *


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




