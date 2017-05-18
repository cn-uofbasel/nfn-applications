from enum import Enum

class LogLevel(Enum):
    Error = 4
    Warning = 3
    Info = 2
    Debug = 1

class Log(object):
    level = LogLevel.Debug

    @staticmethod
    def log(lvl, msg):
        if lvl.value >= Log.level.value:
            print(msg)

    @staticmethod
    def debug(msg):
        Log.log(LogLevel.Debug, msg)

    @staticmethod
    def info(msg):
        Log.log(LogLevel.Info, msg)

    @staticmethod
    def warn(msg):
        Log.log(LogLevel.Warning, msg)

    @staticmethod
    def error(msg):
        Log.log(LogLevel.Error, msg)
