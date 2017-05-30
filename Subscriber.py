# from TestSuite import *
import sys
import signal
from Network import *
from Request import *

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def sigint_handler(*args):
    QApplication.quit()

def timer_fired():
    # print("Process timer fired.")
    # c = c + 1
    node.process_events()

def on_intermediate(request, index, data):
    content = data.getContent().toRawStr()
    print("New content (" + str(index) + "): " + content)

# Log.level = LogLevel.Error



default_broker = "/node4/nfn_service_PubSubBroker/"



ask_node_input = input("Ask node [9001]: ").strip()
broker = input("Broker prefix [" + default_broker + "]: ").strip()
identifier = input("Thread ID [thread]: ").strip()

if not ask_node_input:
    ask_node_input = "9001"

if not broker:
    broker = default_broker

if not identifier:
    identifier = "thread"

# print("ASK: (" + ask_node_input + ")")


node = NFNNode(int(ask_node_input), launch=False)
node.connect()

name = broker + "(@x call 2 x '" + identifier + "')/NFN"

# test = input("Test: ")

# app = QApplication(sys.argv)
# signal.signal(signal.SIGINT, sigint_handler)

# timer = QTimer()
# timer.timeout.connect(timer_fired)
# timer.start(1 * 1000)

request = Request(node, name, timeout=None, on_intermediate=on_intermediate)
request.send()

while True:
    timer_fired()
    time.sleep(1)
# app.exec_()

