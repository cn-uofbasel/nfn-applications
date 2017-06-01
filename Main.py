
from Tests.Tests import *
from Tests.NBodyTest import *
from Tests.IntermediateTest import *
from Tests.SimulationRenderTest import *
from Tests.PubSub.PubSubTest import *
from Tests.Mobility.MobileServerTest import *

# import Tests.ChainTest

# Util.compile_ccn_lite()
# Util.compile_nfn_scala()

# Config.ccn_log_level = CCNLogLevel.Error
# Config.nfn_log_level = NFNLogLevel.Normal

# Log.level = LogLevel.Error

# TestSuite([EchoTest(), SimpleTest(), SerialTest(), SimulationTest()]).start()

# StopTest().start()
# EchoTest().start()
# SimpleTest().start()
# SerialTest().start()
# FetchContentTest().start()
# NestedTest().start()
# FetchServiceTest().start()
# ChunkTest().start()
# ChainTest().start()
# RedirectTest().start()
# SimulationTest().start()
# IntermediateTest().start()
# NBodyTest().start()
# UITest().start()
# SimulationRenderTest(enable_ui=True).start()
# AddToCacheTest().start()
# GetFromLocalCacheTest().start()
# PubSubTest().start()
MobileServerTest().start()

# Util.clean_output_folder()

# Util.write_binary_content("/node6/PubSubMsg/0", "testdata".encode())


# node = NFNNode(9004, launch=False)
# node.connect()
# broker = "/node4/nfn_service_PubSubBroker"
# msg = "/node6/PubSubMsg"
# param = msg.replace("/", "%2F")
# name = broker + "/(@x call 2 x '" + param + "')/NFN"
# Request(node, name).send()


