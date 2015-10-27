from pandac.PandaModules import ConfigVariableString
ConfigVariableString('window-type', 'none').setValue('none')

from direct.showbase.ShowBase import ShowBase
base = ShowBase()

if base:
	from src.messagedirector.MessageDirector import MessageDirector
	base.md = MessageDirector()

	from src.clientagent.ClientAgent import ClientAgent
	base.ca = ClientAgent()

	from src.stateserver.StateServer import StateServer
	base.ss = StateServer()

try:
	base.run()
except:
	run()