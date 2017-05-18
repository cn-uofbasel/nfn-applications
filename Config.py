from enum import Enum


class CCNLogLevel(Enum):
    Fatal = "fatal"
    Error = "error"
    Warning = "warning"
    Info = "info"
    Debug = "debug"
    Verbose = "verbose"
    Trace = "trace"


class NFNLogLevel(Enum):
    Normal = ""
    Debug = "--debug"


class Config(object):
    ccn_log_level = CCNLogLevel.Trace
    nfn_log_level = NFNLogLevel.Debug

