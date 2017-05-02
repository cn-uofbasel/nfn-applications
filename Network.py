from NFNNode import NFNNode
from ComputeServer import ComputeServer
import time


class Network(object):
    def __init__(self):
        self.nodes = []
        self.compute_servers = []

    def process_events(self):
        for node in self.nodes:
            node.process_events()
        for cs in self.compute_servers:
            cs.process_events()


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
        print("Waiting for compute server to launch.")
        time.sleep(10)
        print("")


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
        print("Waiting for compute server to launch.")
        time.sleep(15)
        print("")


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

        print("Waiting for compute servers to launch.")
        time.sleep(20)
        print("")