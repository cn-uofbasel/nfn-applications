import io
import sys
import signal

from Network import *
from Test import *
from Util import *
from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage

class SimulationRenderTest(Test):
    def __init__(self, enable_ui=False):
        super().__init__()
        self.highest_request_sent = -1
        self.max_duration = 30
        self.basename = "/node4/nfn_service_NBody_SimulationRenderService/(@x call 1 x)"
        self.enable_ui = enable_ui
        self.image_label = None
        self.highest_request_received = -1

    def setup(self):
        self.update_interval = 0.1
        self.process_interval = 0.1
        self.network = SerialNetwork(6)
        name = self.basename + "/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_data)
        self.use_event_loop = not self.enable_ui
        if self.enable_ui:
            self.start_ui()

    def on_complete(self):
        QApplication.quit()

    def sigint_handler(self, *args):
        QApplication.quit()

    def start_ui(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        app = QApplication(sys.argv)
        w = QWidget()
        w.resize(500, 500)
        w.move(300, 300)
        w.setWindowTitle('N-body Render')
        label = QLabel(w)
        label.resize(500, 500)
        w.show()
        self.image_label = label
        QTimer.singleShot(self.update_interval * 1000, self.update_timer_fired)
        QTimer.singleShot(self.process_interval * 1000, self.process_timer_fired)
        sys.exit(app.exec_())

    def update_timer_fired(self):
        # print("Update timer fired.")
        self.update()
        QTimer.singleShot(self.update_interval * 1000, self.update_timer_fired)

    def process_timer_fired(self):
        # print("Process timer fired.")
        self.network.process_events()
        QTimer.singleShot(self.process_interval * 1000, self.process_timer_fired)

    def update(self):
        name = self.basename + "/R2C/CIM/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_cim)

    def on_cim(self, interest, data):
        content = data.getContent().toRawStr()
        if not content:
            print("No intermediate results available yet.")
            return
        highest_available = int(content)
        # print("Highest available intermediate: " + str(highest_available))
        for i in range(self.highest_request_sent + 1, highest_available + 1):
            self.request_intermediate(i)
        self.highest_request_sent = highest_available

    def request_intermediate(self, index):
        name = self.basename + "/R2C/GIM " + str(index) + "/NFN"
        self.network.nodes[0].send_interest(name, on_data=self.on_intermediate)

    def on_intermediate(self, interest, data):
        content = data.getContent().toRawStr()
        name = Util.interest_to_string(interest)
        # print("Received data for intermediate interest '{}':\n{}".format(name, urllib.parse.unquote(content)))

        index = Util.get_intermediate_index(interest)
        if index < 0:
            print("Invalid intermediate result.")
            return

        if index < self.highest_request_received:
            print("Received old intermediate out of order. Ignore.")
            return

        self.highest_request_received = index

        img_bytes = data.getContent().toBytes()

        img_file = open("./output/nbody/" + str(index) + ".png", "wb")
        img_file.write(bytearray(img_bytes))
        # print("Saved: ")

        # img = Image.open(io.BytesIO(img_bytes))
        # img.show()

        if self.image_label is not None:
            image = QImage.fromData(img_bytes)
            pix = QPixmap.fromImage(image)
            self.image_label.setPixmap(pix)


    def on_data(self, interest, data):
        content = data.getContent().toRawStr()
        print("Received data for interest '{}':\n{}".format(Util.interest_to_string(interest),
                urllib.parse.unquote(content)))
        self.finish_with_result(TestResult.Success)
