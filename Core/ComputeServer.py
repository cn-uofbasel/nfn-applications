import os
from subprocess import Popen

from Core.Config import *
from Core.Node import Node
from Util.Log import *


class ComputeServer(Node):
    def __init__(self, port, node, launch=False):
        self.nfn_node = node
        super().__init__(port, launch)

    def launch(self):
        super().launch()
        scala_home = os.path.expandvars("$NFNSCALA_HOME").strip()
        if not scala_home or scala_home == "$NFNSCALA_HOME":
            Log.error("$NFNSCALA_HOME not set!")
            return
        jar = scala_home + "/target/scala-2.10/nfn-assembly-0.2.0.jar"
        command = ['java', '-jar', jar,
                   '--mgmtsocket', self.nfn_node.mgmt,
                   '--ccnl-port', str(self.nfn_node.port),
                   '--cs-port', str(self.port),
                   Config.nfn_log_level.value,
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

        Log.info("Launching compute server " + self.description + " attached to " + self.nfn_node.description)
        Log.info("  " + " ".join(command))

        output_dir = Config.output_path
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(Config.output_path + '/' + str(self.port) + '.log', 'wb') as out:
            self.process = Popen(command, cwd=scala_home, stdout=out, stderr=out)



