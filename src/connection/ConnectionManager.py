from direct.directnotify import DirectNotifyGlobal
from direct.task.TaskManagerGlobal import *
from direct.task.Task import Task
from pandac.PandaModules import *
from panda3d.core import *

class ConnectionManager(QueuedConnectionManager):
    notify = DirectNotifyGlobal.directNotify.newCategory("ConnectionManager")

    dcFile = DCFile()
    dcSuffix = ''

    def __init__(self, port_address=None, host_address=None, ip_address=None, backlog=1000):
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.port_address = port_address
        self.host_address = host_address
        self.ip_address = ip_address
        self.backlog = backlog

        if port_address != None:
            self.setup()

        if ip_address != None:
            self.connect(timeout=5000)

    def serverStarted(self, port):
        pass # can be overidden by sub class
    
    def setup(self):
        self.socket = self.cManager.openTCPServerRendezvous(self.port_address, self.backlog)
        if self.socket:
            self.cListener.addConnection(self.socket)
            self.serverStarted(self.port_address)
            taskMgr.add(self.socketListener, 'Poll the connection listener')
            taskMgr.add(self.socketReader, 'Poll the connection reader')

    def connect(self, timeout):
        self.connection = self.cManager.openTCPClientConnection(self.ip_address, self.host_address, timeout)
        if self.connection:
            self.cReader.addConnection(self.connection)
            taskMgr.add(self.socketReader, 'Poll the datagram reader')
            self.registerChannel()
    
    def socketListener(self, task):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection)
                self.cReader.addConnection(newConnection)

        return Task.cont
    
    def socketReader(self, task):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()

            if self.cReader.getData(datagram):
                self.handleDatagram(datagram)

        return Task.cont
    
    def handleDatagram(self, datagram):
        pass

    def importModule(self, dcImports, moduleName, importSymbols):
        module = __import__(moduleName, globals(), locals(), importSymbols)

        if importSymbols:
            if importSymbols == ['*']:
                if hasattr(module, "__all__"):
                    importSymbols = module.__all__
                else:
                    importSymbols = module.__dict__.keys()

            for symbolName in importSymbols:
                if hasattr(module, symbolName):
                    dcImports[symbolName] = getattr(module, symbolName)

                else:
                    raise StandardError, 'Symbol %s not defined in module %s.' % (symbolName, moduleName)

        else:
            components = moduleName.split('.')
            dcImports[components[0]] = module

    def readDCFile(self, dcFileNames = None):
        dcFile = self.dcFile
        dcFile.clear()
        self.dclassesByName = {}
        self.dclassesByNumber = {}
        self.hashVal = 0

        dcImports = {}
        if dcFileNames == None:
            readResult = dcFile.readAll()
            if not readResult:
                self.notify.error("Could not read dc file.")
        else:
            searchPath = getModelPath().getValue()
            for dcFileName in dcFileNames:
                pathname = Filename(dcFileName)
                vfs.resolveFilename(pathname, searchPath)
                readResult = dcFile.read(pathname)
                if not readResult:
                    self.notify.error("Could not read dc file: %s" % (pathname))

        self.hashVal = dcFile.getHash()

        for n in range(dcFile.getNumImportModules()):
            moduleName = dcFile.getImportModule(n)
            suffix = moduleName.split('/')
            moduleName = suffix[0]
            if self.dcSuffix and self.dcSuffix in suffix[1:]:
                moduleName += self.dcSuffix

            importSymbols = []
            for i in range(dcFile.getNumImportSymbols(n)):
                symbolName = dcFile.getImportSymbol(n, i)
                suffix = symbolName.split('/')
                symbolName = suffix[0]
                if self.dcSuffix and self.dcSuffix in suffix[1:]:
                    symbolName += self.dcSuffix

                importSymbols.append(symbolName)

            self.importModule(dcImports, moduleName, importSymbols)

        for i in range(dcFile.getNumClasses()):
            dclass = dcFile.getClass(i)
            number = dclass.getNumber()
            className = dclass.getName() + self.dcSuffix
            classDef = dcImports.get(className)

            if classDef == None:
                className = dclass.getName()
                classDef = dcImports.get(className)

            if classDef == None:
                self.notify.debug("No class definition for %s." % (className))
            else:
                if type(classDef) == types.ModuleType:
                    if not hasattr(classDef, className):
                        self.notify.error("Module %s does not define class %s." % (className, className))
                    classDef = getattr(classDef, className)

                if type(classDef) != types.ClassType and type(classDef) != types.TypeType:
                    self.notify.error("Symbol %s is not a class name." % (className))
                else:
                    dclass.setClassDef(classDef)

            self.dclassesByName[className] = dclass
            if number >= 0:
                self.dclassesByNumber[number] = dclass