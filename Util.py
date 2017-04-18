from subprocess import call
import os


class Util(object):
    @staticmethod
    def compile_ccnl(clean=False):
        src = os.path.expandvars("$CCNL_HOME/src")
        print("Compiling ccn-lite.")
        cmd = "make clean all" if clean else "make all"
        call(cmd.split(" "), cwd=src)
        print("Done.\n")

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