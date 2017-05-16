import io
import sys
import signal

from Network import *
from Test import *
from Util import *
from Request import *
from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage

class SimulationRenderTest(Test):
    def __init__(self, enable_ui=False):
        super().__init__()
        self.max_duration = 30
        self.basename = "/node4/nfn_service_NBody_SimulationRenderService/(@x call 1 x)"
        self.enable_ui = enable_ui
        self.widget = None
        self.image_label = None

    def setup(self):
        self.update_interval = 0.1
        self.process_interval = 0.1
        self.network = SerialNetwork(6)
        name = self.basename + "/NFN"
        Request(self.network.nodes[0], name, on_data=self.on_data, on_intermediate=self.on_intermediate).send()
        if self.enable_ui:
            self.start_ui()

    def on_complete(self):
        QApplication.quit()

    def sigint_handler(self, *args):
        QApplication.quit()

    def start_ui(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        self.widget = QWidget()
        self.widget.resize(500, 500)
        self.widget.move(300, 300)
        self.widget.setWindowTitle('N-body Render')
        self.image_label = QLabel(self.widget)
        self.image_label.resize(500, 500)
        self.widget.show()

    def on_intermediate(self, request, index, data):
        img_bytes = data.getContent().toBytes()

        img_file = open("./output/nbody/" + str(index) + ".png", "wb")
        img_file.write(bytearray(img_bytes))

        # img = Image.open(io.BytesIO(img_bytes))
        # img.show()

        if self.image_label is not None:
            image = QImage.fromData(img_bytes)
            pix = QPixmap.fromImage(image)
            self.image_label.setPixmap(pix)


    def on_data(self, request, data):
        self.finish_with_result(TestResult.Success)
