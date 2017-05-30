from Test import *
# from Log import *

class TestSuite(object):
    def __init__(self, tests=[]):
        self.tests = tests

    def start(self):
        for test in self.tests:
            test.start()
        self.print_summary()

    def print_summary(self):
        Log.info("Test summary:")
        Log.info("-------------")
        count = 0
        for test in self.tests:
            if test.result == TestResult.Success:
                count += 1
                print(test.name + " passed.")
            else:
                print(test.name + " failed.")
        Log.info("-------------")
        Log.info(str(count) + "/" + str(len(self.tests)) + " tests passed.\n")


