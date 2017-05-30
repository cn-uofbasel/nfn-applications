import sys
import signal
from Log import *

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


class TestResult(Enum):
    Success = 0
    Failure = 1


class Test(object):
    app = QApplication(sys.argv)

    def __init__(self, name=None, network=None):
        self.name = name if name is not None else type(self).__name__
        self.network = network
        # self.loop = None
        self.app = None
        self.process_interval = 1
        self.update_interval = 1
        self.result = None
        self.max_duration = 0
        self.timeout_timer = None
        self.events_timer = None
        self.update_timer = None
        # self.use_event_loop = True

    def setup(self):
        pass

    def update(self):
        pass

    def on_complete(self):
        pass

    def on_succeed(self):
        pass

    def on_fail(self):
        pass

    def update_timer_fired(self):
        self.update()
        # self.update_handle = self.loop.call_later(self.update_interval, self.process_update)

    def events_timer_fired(self):
        self.network.process_events()
        # self.process_handle = self.loop.call_later(self.process_interval, self.process_events)

    def timeout_timer_fired(self):
        if self.result is None:
            self.finish_with_result(TestResult.Failure)

    def sigint_handler(self, *args):
        self.app.exit()

    def start(self):
        try:
            Log.info("\nTest started (" + self.name + ")\n")

            self.app = QApplication(sys.argv)
            signal.signal(signal.SIGINT, self.sigint_handler)

            self.setup()

            self.events_timer = QTimer()
            self.events_timer.timeout.connect(self.events_timer_fired)
            self.events_timer.start(self.process_interval * 1000)

            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_timer_fired)
            self.update_timer.start(self.update_interval * 1000)

            if self.max_duration > 0:
                self.timeout_timer = QTimer()
                self.timeout_timer.timeout.connect(self.timeout_timer_fired)
                self.timeout_timer.start(self.max_duration * 1000)

            self.app.exec_()

            # if self.use_event_loop:
            # self.loop = asyncio.get_event_loop()
            # self.process_handle = self.loop.call_soon(self.process_events)
            # self.update_handle = self.loop.call_later(self.update_interval, self.process_update)
            # if self.max_duration > 0:
            #     self.timeout_handle = self.loop.call_later(self.max_duration, self.test_timeout)
            # self.loop.run_forever()

        except (KeyboardInterrupt, SystemExit):
            Log.error("\nAborting.")

    def finish_with_result(self, result):
        if self.timeout_timer is not None:
            self.timeout_timer.stop()
        if self.events_timer is not None:
            self.events_timer.stop()
        if self.update_timer is not None:
            self.update_timer.stop()
        if self.network is not None:
            print()
            self.network.shutdown()
        # if self.use_event_loop:
        #     self.loop.stop()

        self.result = result
        self.on_complete()
        if result == TestResult.Success:
            Log.info("\nTest succeeded (" + self.name + ")\n")
            self.on_succeed()
        if result == TestResult.Failure:
            Log.warn("\nTest failed (" + self.name + ")\n")
            self.on_fail()

        self.app.exit()

