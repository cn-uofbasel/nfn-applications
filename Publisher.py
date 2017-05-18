import sys

from Network import *

node = NFNNode(9006, launch=False)
node.connect()

counter = 0

for line in sys.stdin:
    name = "/node6/PubSubMsg/" + str(counter)
    data = line.encode()
    print("Publishing content: " + line)
    node.add_content(name, data)
    counter += 1

