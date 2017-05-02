from Test import Test
from Network import *
import io
import urllib
from PIL import Image


class NBodyTest(Test):
    def setup(self):
        self.network = ThesisNetwork()
        basename = "/node6/nfn_service_NBody_RenderService/(@x call 2 x (call 3 %2Fnode6%2Fnfn_service_NBody_SimulationService '-c' 100))"
        self.network.nodes[0].send_interest(basename + "/NFN", timeout=100, on_data=self.on_data)


    def on_data(self, interest, data):
        content = data.getContent()
        text = urllib.parse.unquote(content.toRawStr())
        bytes = content.toBytes()

        img_file = open("/Users/Bazsi/Desktop/nbody.png", "wb")
        img_file.write(bytearray(bytes))

        img = Image.open(io.BytesIO(bytes))
        img.show()

        # content = data.getContent().toRawStr()
        # print("Received data for interest '{}':\n{}".format(self.interest_to_string(interest),
        #                                                     urllib.parse.unquote(content)))

        print("Simulation data received.")
        print(text)

        # echo = "/nodeBS/nfn_service_Echo/(@x call 2 x (call 1 %2FnodeAS%2Fnfn_service_NBody_SimulationService))"
        # self.network.nodes[0].send_interest(echo + "/NFN", on_data=self.on_render_data)
        #
        # def on_render_data(self, interest, data):
        #     content = urllib.parse.unquote(data.getContent().toRawStr())
        #     print("Render data received.")
        #     print(content)