from subprocess import *

from Core.Node import Node
from Util.Util import *


class NFNNode(Node):
    def __init__(self, port, prefix=None, launch=False):
        self.mgmt = '/tmp/mgmt-nfn-relay-' + str(port) + '.sock'
        self.prefix = prefix
        self.faces = {}
        super().__init__(port, launch)

    def launch(self):
        super().launch()
        relay = os.path.expandvars("$CCNL_HOME/bin/ccn-nfn-relay")
        command = [relay, '-v', Config.ccn_log_level.value, '-u', str(self.port), '-x', self.mgmt]
        output_dir = Config.output_path
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(Config.output_path + '/' + str(self.port) + '.log', 'wb') as out:
            self.process = Popen(command, stdout=out, stderr=out)
        Log.info("Launched node " + self.description + " " + self.prefix)

    def get_face(self, node):
        for faceid in self.faces:
            if self.faces[faceid] == node:
                return faceid
        return None

    def add_face(self, node):
        ctrl_path = os.path.expandvars("$CCNL_HOME/bin/ccn-lite-ctrl")
        xml_path = os.path.expandvars("$CCNL_HOME/bin/ccn-lite-ccnb2xml")
        command = [ctrl_path, '-x', self.mgmt, 'newUDPface', 'any', node.ip, str(node.port)]
        ctrl = Popen(command, stdout=PIPE)
        xml = Popen([xml_path], stdin=ctrl.stdout, stdout=PIPE)
        grep = Popen(['grep', 'FACEID'], stdin=xml.stdout, stdout=PIPE)
        faceid = check_output(['sed', '-E', 's/^[^0-9]*([0-9]+).*/\\1/'], stdin=grep.stdout).decode("utf-8").strip()
        Log.info("Added face " + self.description + " (face " + faceid + ") -> " + node.description)
        return faceid

    def add_forwarding_rule(self, prefix, node):
        faceid = self.get_face(node)
        if faceid is None:
            faceid = self.add_face(node)
        ctrl_path = os.path.expandvars("$CCNL_HOME/bin/ccn-lite-ctrl")
        command = [ctrl_path, '-x', self.mgmt, 'prefixreg', prefix, str(faceid), 'ndn2013']
        check_output(command)
        Log.info("Added rule " + self.description + " (" + prefix + ") -> " + node.description)

    def add_content(self, name, data):
        ccnl_home = Util.ccnl_home()
        if ccnl_home is None:
            return
        path = Util.write_binary_content(name, data)
        ctrl_path = ccnl_home + "/bin/ccn-lite-ctrl"
        command = [ctrl_path, '-x', self.mgmt, 'addContentToCache', path]
        check_output(command)
        Log.info("Added content to cache of node " + self.description + " with name " + name)
