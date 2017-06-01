import os
import urllib
import uuid
from subprocess import Popen, PIPE, call

from Core.Config import *
from Util.Log import *


class Util(object):
    @staticmethod
    def compile_ccn_lite(clean=False):
        Log.info("")
        wd = "$CCNL_HOME/src"
        src = os.path.expandvars(wd)
        if src == wd or not src:
            Log.error("$CCNL_HOME not set!")
            return
        Log.info("Compiling ccn-lite.")
        cmd = "make clean all" if clean else "make all"
        call(cmd.split(" "), cwd=src)
        Log.info("Done.")

    @staticmethod
    def compile_nfn_scala(assembly=True, clean=False):
        Log.info("")
        wd = "$NFNSCALA_HOME"
        src = os.path.expandvars(wd)
        if src == wd or not src:
            Log.error("$NFNSCALA_HOME not set!")
            return
        Log.info("Compiling nfn-scala.")
        cmd = "sbt clean" if clean else "sbt"
        cmd = cmd + (" assembly" if assembly else " compile")
        call(cmd.split(" "), cwd=src)
        Log.info("Done.")

    @staticmethod
    def clean_output_folder():
        folder = Config.output_path
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception as e:
                Log.error(e)

    @staticmethod
    def get_intermediate_index(interest):
        name = interest.getName()
        for i in range(0, name.size() - 1):
            comp = name.get(i).getValue().toRawStr()
            # print("comp: " + comp)
            if comp.startswith("GIM"):
                return int(comp.split(" ")[1])
        return -1

    @staticmethod
    def interest_to_string(interest):
        uri = interest.getName().toUri()
        cmps = uri.split("/")
        last_component = cmps[-1]
        is_segment = last_component.startswith("%00")
        if is_segment:
            cmps.pop()
        string = urllib.parse.unquote("/".join(cmps))
        if is_segment:
            string += "/" + last_component
        return string

    @staticmethod
    def find_segment_number(name):
        for i in range(0, name.size()):
            component = name.get(i)
            if component.isSegment():
                return component.toSegment()
        return -1

    @staticmethod
    def log_on_data(interest, data):
        content = data.getContent().toRawStr()
        Log.info("Received data for interest '{}':\n{}".format(Util.interest_to_string(interest),
                                                            urllib.parse.unquote(content)))

    @staticmethod
    def ccnl_home():
        ccnl_home = os.path.expandvars("$CCNL_HOME").strip()
        if not ccnl_home or ccnl_home == "$CCNL_HOME":
            Log.error("$CCNL_HOME not set!")
            return None
        return ccnl_home

    @staticmethod
    def nfn_home():
        nfn_home = os.path.expandvars("$NFNSCALA_HOME").strip()
        if not nfn_home or nfn_home == "$NFNSCALA_HOME":
            Log.error("$NFNSCALA_HOME not set!")
            return None
        return nfn_home

    @staticmethod
    def temp_folder():
        content_dir = './temp'
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)
        return content_dir

    @staticmethod
    def write_binary_content(name, data):
        ccnl_home = Util.ccnl_home()
        if ccnl_home is None:
            return
        path = Util.temp_folder() + "/" + str(uuid.uuid4()) + ".ndn2013"
        executable = ccnl_home + "/bin/ccn-lite-mkC"
        command = [executable, '-s', 'ndn2013', '-o', path, name]
        mkc = Popen(command, stdin=PIPE)
        mkc.communicate(input=data)
        return path
