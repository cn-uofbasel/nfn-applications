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


def sigint_handler(*args):
    QApplication.quit()

def timer_fired():
    node.process_events()

def on_intermediate(request, data):
    content = data.getContent().toRawStr()
    print("New content: " + content)

# Log.level = LogLevel.Error

node = NFNNode(9001, launch=False)
node.connect()

broker = "/node4/nfn_service_PubSubBroker"
msg = "/node6/PubSubMsg"
param = msg.replace("/", "%2F")
name = broker + "/(@x call 2 x '" + param + "')/NFN"

app = QApplication(sys.argv)
signal.signal(signal.SIGINT, sigint_handler)

timer = QTimer()
timer.timeout.connect(timer_fired)
timer.start(1 * 1000)

Request(node, name, on_intermediate=on_intermediate).send()

app.exec_()

