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

# Tests:
#from tests.test_clientagent import test_clientagent

try: # 1.8.1 support
	base.run()
except:
	run()