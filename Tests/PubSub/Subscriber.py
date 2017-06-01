import signal

from Core.Network import *
from Core.Request import *


def sigint_handler(*args):
    global timer
    global request
    if timer is not None:
        timer.cancel()
    if request is not None:
        request.cancel()

def timer_fired():
    global timer
    node.process_events()
    timer = threading.Timer(1, timer_fired)
    timer.start()

def on_intermediate(request, index, data):
    content = data.getContent().toRawStr()
    print("New content (" + str(index) + "): " + content)

Log.level = LogLevel.Warning


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


node = NFNNode(int(ask_node_input), launch=False)
node.connect()

name = broker + "(@x call 2 x '" + identifier + "')/NFN"


signal.signal(signal.SIGINT, sigint_handler)

request = Request(node, name, timeout=None, on_intermediate=on_intermediate)
request.send()

timer = threading.Timer(1, timer_fired)
timer.start()


