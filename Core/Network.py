import time

from Core.ComputeServer import ComputeServer
from Core.NFNNode import NFNNode
from Util.Log import *


class Network(object):
    def __init__(self):
        self.nodes = []
        self.compute_servers = []

    def process_events(self):
        for node in self.nodes:
            node.process_events()
        for cs in self.compute_servers:
            cs.process_events()

    def shutdown(self):
        for node in self.nodes:
            node.shutdown()
        for node in self.compute_servers:
            node.shutdown()


class SimpleNetwork(Network):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.setup()

    def setup(self):
        for i in range(1, self.n + 1):
            self.nodes.append(NFNNode(port=9000 + i, prefix='/node' + str(i), launch=True))

        for i in range(0, self.n - 1):
            self.nodes[i].add_forwarding_rule("/node" + str(self.n), self.nodes[i + 1])

        self.compute_servers.append(ComputeServer(port=9999, node=self.nodes[self.n-1], launch=True))
        Log.info("Waiting for compute server to launch.")
        time.sleep(5)
        Log.info("")

class SerialNetwork(Network):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.setup()

    def setup(self):
        for i in range(1, self.n + 1):
            self.nodes.append(NFNNode(port=9000 + i, prefix='/node' + str(i), launch=True))

        for i in range(0, self.n - 1):
            for j in range(i + 1, self.n):
                self.nodes[i].add_forwarding_rule("/node" + str(j + 1), self.nodes[i + 1])

        for i in range(1, self.n + 1):
            self.compute_servers.append(ComputeServer(port=9990 + i, node=self.nodes[i - 1], launch=True))

        Log.info("Waiting for compute servers to launch.")
        time.sleep(5)
        Log.info("")


class ThesisNetwork(Network):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        n = 6
        s = 4
        for i in range(1, n + 1):
            self.nodes.append(NFNNode(port=9000 + i, prefix='/node' + str(i), launch=True))

        for i in range(0, s - 1):
            self.nodes[i].add_forwarding_rule("/node" + str(s), self.nodes[i + 1])

        for i in range(0, n - 1):
            self.nodes[i].add_forwarding_rule("/node" + str(n), self.nodes[i + 1])

        self.compute_servers.append(ComputeServer(port=9994, node=self.nodes[s - 1], launch=True))
        self.compute_servers.append(ComputeServer(port=9996, node=self.nodes[n - 1], launch=True))
        Log.info("Waiting for compute server to launch.")
        time.sleep(5)
        Log.info("")


class ForkNetwork(Network):
    def __init__(self, stem_length, branch_count, branch_length):
        super().__init__()
        self.stem_length = stem_length
        self.branch_count = branch_count
        self.branch_length = branch_length
        self.branches = []
        self.setup()

    def setup(self):
        # launch the stem/trunk nodes
        for i in range(0, self.stem_length):
            self.nodes.append(NFNNode(port=9000 + i + 1, prefix='/node' + str(i + 1), launch=True))

        for b in range(0, self.branch_count):
            letter = chr(ord('A') + b)
            branch = []

            # launch the nodes of the current branch
            for i in range(0, self.branch_length):
                id = "S" if i == self.branch_length - 1 else str(i + 1)
                branch.append(NFNNode(port=9000 + (b + 1) * 100 + i + 1, prefix='/node' + letter + id, launch=True))
            self.branches.append(branch)
            self.nodes.extend(branch)

            # launch compute server at the end of the branch
            self.compute_servers.append(ComputeServer(port=9000 + (b + 1) * 100 + 99, node=branch[self.branch_length - 1], launch=True))

            # setup forwarding rules in the current branch that forward packets to the compute server
            for i in range(0, self.branch_length - 1):
                branch[i].add_forwarding_rule("/node" + letter + "S", branch[i + 1])

            # setup forwarding rules that forward packets from the root of the network to the current branch
            for i in range(0, self.stem_length - 1):
                self.nodes[i].add_forwarding_rule("/node" + letter + "S", self.nodes[i + 1])
            self.nodes[self.stem_length - 1].add_forwarding_rule("/node" + letter + "S", branch[0])

            # setup forwarding rules that forward packets back to the branching point for every other branch
            for j in range(0, self.branch_count):
                if j != b:
                    prefix = "/node" + chr(ord('A') + j) + "S"
                    for i in range(1, self.branch_length):
                        branch[i].add_forwarding_rule(prefix, branch[i - 1])
                    branch[0].add_forwarding_rule(prefix, self.nodes[self.stem_length - 1])

        Log.info("Waiting for compute servers to launch.")
        time.sleep(5)
        Log.info("")

class StarNetwork(Network):
    def __init__(self, spoke_count, spoke_length, server_on_hub=True, server_on_spokes=True):
        super().__init__()
        self.spoke_count = spoke_count
        self.spoke_length = spoke_length
        self.server_on_hub = server_on_hub
        self.server_on_spokes = server_on_spokes
        self.spokes = []
        self.hub = None
        self.setup()

    def setup(self):
        # launch hub
        self.hub = NFNNode(port=9000, prefix='/hub', launch=True)
        self.nodes.append(self.hub)
        if self.server_on_hub:
            server = ComputeServer(port=9999, node=self.hub, launch=True)
            self.compute_servers.append(server)

        for s in range(0, self.spoke_count):

            # launch the nodes of the current branch
            branch = []
            for n in range(0, self.spoke_length):
                node = NFNNode(port=9000+(s+1)*100+n+1, prefix='/hub/branch'+str(s+1)+'/node'+str(n+1), launch=True)
                branch.append(node)
            self.nodes.extend(branch)
            self.spokes.append(branch)

            # launch compute server at the end of the branch
            if self.server_on_spokes:
                server = ComputeServer(port=9000+(s+1)*100+99, node=branch[self.spoke_length - 1], launch=True)
                self.compute_servers.append(server)

            # setup forwarding rules in the current branch that forward packets from the center to the compute server
            self.hub.add_forwarding_rule('/hub/branch'+str(s+1)+'/node'+str(self.spoke_length), branch[0])
            for n in range(0, self.spoke_length - 1):
                branch[n].add_forwarding_rule('/hub/branch'+str(s+1)+'/node'+str(self.spoke_length), branch[n + 1])

            # setup forwarding rules that forward packets from the current branch to the center of the network
            branch[0].add_forwarding_rule('/hub', self.hub)
            for n in range(1, self.spoke_length):
                branch[n].add_forwarding_rule('/hub', branch[n - 1])

        Log.info("Waiting for compute servers to launch.")
        time.sleep(10)
        Log.info("")

