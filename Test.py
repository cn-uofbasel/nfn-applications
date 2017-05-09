import sys
import asyncio
from enum import Enum


class TestResult(Enum):
    Success = 0
    Failure = 1


class Test(object):
    def __init__(self, name=None, network=None):
        self.name = name if name is not None else type(self).__name__
        self.network = network
        self.loop = None
        self.process_interval = 1
        self.update_interval = 1
        self.result = None
        self.max_duration = 0
        self.timeout_handle = None
        self.process_handle = None
        self.update_handle = None
        self.use_event_loop = True

    def setup(self):
        pass

    def update(self):
        pass

    def on_succeed(self):
        pass

    def on_fail(self):
        pass

    def process_update(self):
        self.update()
        self.update_handle = self.loop.call_later(self.update_interval, self.process_update)

    def process_events(self):
        self.network.process_events()
        self.process_handle = self.loop.call_later(self.process_interval, self.process_events)

    def finish_with_result(self, result):
        if self.timeout_handle is not None:
            self.timeout_handle.cancel()
        if self.process_handle is not None:
            self.process_handle.cancel()
        if self.update_handle is not None:
            self.update_handle.cancel()
        if self.network is not None:
            print()
            self.network.shutdown()
        self.loop.stop()
        self.result = result
        if result == TestResult.Success:
            print("\nTest succeeded (" + self.name + ")\n")
            self.on_succeed()
        if result == TestResult.Failure:
            print("\n❗ Test failed (" + self.name + ")\n")
            self.on_fail()

    def test_timeout(self):
        if self.result is None:
            self.finish_with_result(TestResult.Failure)

    def start(self):
        try:
            print("\nTest started (" + self.name + ")\n")
            self.setup()
            if self.use_event_loop:
                self.loop = asyncio.get_event_loop()
                self.process_handle = self.loop.call_soon(self.process_events)
                self.update_handle = self.loop.call_later(self.update_interval, self.process_update)
                if self.max_duration > 0:
                    self.timeout_handle = self.loop.call_later(self.max_duration, self.test_timeout)
                self.loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            print("\nAborting.")


