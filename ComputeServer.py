from Node import Node
import os
from subprocess import Popen, check_output, PIPE

class ComputeServer(Node):
    def __init__(self, port, node, launch=False):
        self.nfn_node = node
        super().__init__(port, launch)

    def launch(self):
        super().launch()
        scala_home = os.path.expandvars("$NFNSCALA_HOME").strip()
        if not scala_home or scala_home == "$NFNSCALA_HOME":
            print("$NFNSCALA_HOME not set!")
            return
        jar = scala_home + "/target/scala-2.10/nfn-assembly-0.2.0.jar"
        command = ['java', '-jar', jar,
                   '--mgmtsocket', self.nfn_node.mgmt,
                   '--ccnl-port', str(self.nfn_node.port),
                   '--cs-port', str(self.port),
                   # '--debug',
                   '--ccnl-already-running',
                   self.nfn_node.prefix]

        # arg = " ".join(['runMain', 'runnables.production.ComputeServerStarter',
        #        '--mgmtsocket', self.nfn_node.mgmt,
        #        '--ccnl-port', str(self.nfn_node.port),
        #        '--cs-port', str(self.port),
        #        '--debug',
        #        '--ccnl-already-running',
        #        self.nfn_node.prefix])
        # # command = ['sbt', arg]

        print("Launching compute server " + self.description + " attached to " + self.nfn_node.description)
        print("  " + " ".join(command))

        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open('./output/' + str(self.port) + '.log', 'wb') as out:
            self.process = Popen(command, cwd=scala_home, stdout=out, stderr=out)



