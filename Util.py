from subprocess import call
import os
import urllib

class Util(object):
    @staticmethod
    def compile_ccn_lite(clean=False):
        print("")
        wd = "$CCNL_HOME/src"
        src = os.path.expandvars(wd)
        if src == wd or not src:
            print("$CCNL_HOME not set!")
            return
        print("Compiling ccn-lite.")
        cmd = "make clean all" if clean else "make all"
        call(cmd.split(" "), cwd=src)
        print("Done.")

    @staticmethod
    def compile_nfn_scala(clean=False):
        print("")
        wd = "$NFNSCALA_HOME"
        src = os.path.expandvars(wd)
        if src == wd or not src:
            print("$NFNSCALA_HOME not set!")
            return
        print("Compiling nfn-scala.")
        cmd = "sbt clean compile" if clean else "sbt compile"
        call(cmd.split(" "), cwd=src)
        print("Done.")

    @staticmethod
    def clean_output_folder():
        folder = './output'
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception as e:
                print(e)

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