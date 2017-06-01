import signal
import threading

from Util.Log import *


class TestResult(Enum):
    Success = 0
    Failure = 1


class Test(object):
    # app = QApplication(sys.argv)

    def __init__(self, name=None, network=None):
        self.name = name if name is not None else type(self).__name__
        self.network = network
        # self.loop = None
        # self.app = None
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
        self.update_timer = threading.Timer(self.update_interval, self.update_timer_fired)
        self.update_timer.start()
        # self.update_handle = self.loop.call_later(self.update_interval, self.process_update)

    def events_timer_fired(self):
        self.network.process_events()
        self.events_timer = threading.Timer(self.process_interval, self.events_timer_fired)
        self.events_timer.start()
        # self.process_handle = self.loop.call_later(self.process_interval, self.process_events)

    def timeout_timer_fired(self):
        if self.result is None:
            self.finish_with_result(TestResult.Failure)

    def sigint_handler(self, *args):
        self.stop()
        # self.app.exit()

    def start(self):
        try:
            Log.info("\nTest started (" + self.name + ")\n")

            # self.app = QApplication(sys.argv)
            signal.signal(signal.SIGINT, self.sigint_handler)

            self.setup()

            self.events_timer = threading.Timer(self.process_interval, self.events_timer_fired)
            self.events_timer.start()
            self.update_timer = threading.Timer(self.update_interval, self.update_timer_fired)
            self.update_timer.start()
            if self.max_duration > 0:
                self.timeout_timer = threading.Timer(self.max_duration, self.timeout_timer_fired)
                self.timeout_timer.start()


        except (KeyboardInterrupt, SystemExit):
            Log.error("\nAborting.")

    def stop(self):
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
        if self.events_timer is not None:
            self.events_timer.cancel()
        if self.update_timer is not None:
            self.update_timer.cancel()

    def finish_with_result(self, result):
        # if self.timeout_timer is not None:
        #     self.timeout_timer.stop()
        # if self.events_timer is not None:
        #     self.events_timer.stop()
        # if self.update_timer is not None:
        #     self.update_timer.stop()
        self.stop()
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


        # self.app.exit()

