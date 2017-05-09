from enum import Enum


class CCNLogLevel(Enum):
    Fatal = "fatal"
    Error = "error"
    Warning = "warning"
    Info = "info"
    Debug = "debug"
    Verbose = "verbose"
    Trace = "trace"


class Config(object):
    ccn_log_level = CCNLogLevel.Error

