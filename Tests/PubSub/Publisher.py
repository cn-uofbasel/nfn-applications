import sys

from Core.Network import *
from Core.Request import *

Log.level = LogLevel.Warning

default_broker = "/node4/nfn_service_PubSubBroker/"

try:
    publish_node_input = input("Publish to node [9006]: ").strip()
    notify_node_input = input("Notify node [9001]: ").strip()
    broker = input("Broker prefix [" + default_broker + "]: ").strip()
    identifier = input("Thread ID [thread]: ").strip()

    if not publish_node_input:
        publish_node_input = "9006"

    if not notify_node_input:
        notify_node_input = "9001"

    if not broker:
        broker = default_broker

    if not identifier:
        identifier = "thread"

    default_prefix = "/node6/PubSubMsg/" + identifier + "/"
    message_prefix = input("Message prefix [" + default_prefix + "]: ").strip()

    if not message_prefix:
        message_prefix = default_prefix

    firstNode = NFNNode(int(notify_node_input), launch=False)
    firstNode.connect()

    publishNode = NFNNode(int(publish_node_input), launch=False)
    publishNode.connect()

    print("Starting PubSub broker service.")
    notification = broker + "(@x call 2 x '" + identifier + "')/NFN"
    Request(firstNode, notification).send()

    print()
    print("Enter content to publish:")

    for line in sys.stdin:
        print("Publishing content: " + line)
        name = message_prefix + str(uuid.uuid4())
        data = line.encode()
        publishNode.add_content(name, data)

        param = name.replace("/", "%2F")
        notification = broker + "(@x call 2 x '" + identifier + "')/R2C/CTRL " + param + "/NFN"
        request = Request(firstNode, notification).send()

except (KeyboardInterrupt, SystemExit):
    Log.error("\nQuitting.")

