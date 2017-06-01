from Core.Network import *
from Core.Request import *


# Log.level = LogLevel.Warning


try:

    notify_node_input = input("Notify node [9000]: ").strip()
    if not notify_node_input:
        notify_node_input = "9000"

    waypoint_prefix = input("Waypoint prefix [/hub/nfn_service_Waypoint]: ").strip()
    if not waypoint_prefix:
        waypoint_prefix = "/hub/nfn_service_Waypoint"

    node = NFNNode(int(notify_node_input), launch=False)
    node.connect()

    while True:
        print()
        new_prefix = input("Move server to prefix: ").strip()
        if not new_prefix:
            break

        new_prefix = new_prefix.replace("/", "%2F")
        identifier = "test"
        name = waypoint_prefix + "/(@x call 2 x '" + identifier + "')/R2C/CTRL " + new_prefix + "/NFN"
        request = Request(node, name).send()

except (KeyboardInterrupt, SystemExit):
    Log.error("\nQuitting.")
