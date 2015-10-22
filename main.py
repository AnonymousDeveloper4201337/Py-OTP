from pandac.PandaModules import ConfigVariableString
ConfigVariableString('window-type', 'none').setValue('none')

import __builtin__
from direct.showbase import ShowBase
__builtin__.base = ShowBase.ShowBase()

# MessageDirector:
from src.messagedirector.MessageDirector import MessageDirector
__builtin__.base.md = MessageDirector()

# ClientAgent:
from src.clientagent.ClientAgent import ClientAgent
__builtin__.base.ca = ClientAgent()

# StateServer:
from src.stateserver.StateServer import StateServer
__builtin__.base.ss = StateServer()

# EventLogger:
from src.eventlogger.EventLogger import EventLogger
__builtin__.base.el = EventLogger()

# DatabaseStateServer:
from src.databasestateserver.DatabaseStateServer import DatabaseStateServer
__builtin__.base.dbss = DatabaseStateServer()

# DatabaseServer
from src.databaseserver.DatabaseServer import DatabaseServer
__builtin__.base.db = DatabaseServer()

# Tests:
#from tests.test_clientagent import test_clientagent

try: # 1.8.1 support
	base.run()
except:
	run()