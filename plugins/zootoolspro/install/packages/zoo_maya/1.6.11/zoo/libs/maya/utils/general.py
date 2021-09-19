import os
from contextlib import contextmanager
import functools

from maya import cmds
from maya.OpenMaya import MGlobal
from maya.api import OpenMaya as om2
from zoo.libs.utils import zlogging
from zoo.libs.maya.utils import mayaenv

logger = zlogging.zooLogger


def mayaUpVector():
    """Gets the current world up vector

    :rtype: om1.MVector
    """
    return MGlobal.upAxis()


def upAxis():
    """Returns the current world up axis in str form.

    :return: returns x,y or z
    :rtype: str
    """
    if isYAxisUp():
        return "y"
    elif isZAxisUp():
        return "z"
    return "x"


def isYAxisUp():
    """Returns True if y is world up

    :return: bool
    """
    return MGlobal.isYAxisUp()


def isZAxisUp():
    """Returns True if Z is world up

    :return: bool
    """
    return MGlobal.isZAxisUp()


def isXAxisUp():
    """Returns True if x is world up

    :return: bool
    """
    return not isYAxisUp() and not isZAxisUp()


def loadPlugin(pluginPath):
    """Loads the given maya plugin path can be .mll or .py

    :param pluginPath: the absolute fullpath file path to the plugin
    :type pluginPath: str
    :rtype: bool
    """
    try:
        if not isPluginLoaded(pluginPath):
            cmds.loadPlugin(pluginPath)
    except RuntimeError:
        logger.debug("Could not load plugin->{}".format(pluginPath))
        return False
    return True


def unloadPlugin(pluginPath):
    """unLoads the given maya plugin name can be .mll or .py

    :param pluginPath: Maya plugin name
    :type pluginPath: str
    :rtype: bool
    """
    try:
        if isPluginLoaded(pluginPath):
            cmds.unloadPlugin(pluginPath)
    except RuntimeError:
        logger.debug("Could not load plugin->{}".format(pluginPath))
        return False
    return False


def isPluginLoaded(pluginPath):
    """Returns True if the given plugin name is loaded
    """
    return cmds.pluginInfo(pluginPath, q=True, loaded=True)


def getMayaPlugins():
    location = mayaenv.getMayaLocation(mayaenv.mayaVersion())
    plugins = set()
    for path in [i for i in mayaenv.mayaPluginPaths() if i.startswith(location) and os.path.isdir(i)]:
        for x in os.listdir(path):
            if os.path.isfile(os.path.join(path, x)) and isPluginLoaded(path):
                plugins.add(x)
    return list(plugins)


def loadAllMayaPlugins():
    logger.debug("loading All plugins")
    for plugin in getMayaPlugins():
        loadPlugin(plugin)
    logger.debug("loaded all plugins")


def unLoadMayaPlugins():
    logger.debug("unloading All plugins")
    for plugin in getMayaPlugins():
        unloadPlugin(plugin)
    logger.debug("unloaded all plugins")


def removeUnknownPlugins(message=True):
    """Removes unknown plugins from the scene.

    :param message: report the message to the user
    :type message: bool
    :return removedPlugins: A set of the removed plugins
    :rtype removedPlugins: set(str)
    """
    removedPlugins = set()
    for pluginName in cmds.unknownPlugin(query=True, list=True) or []:
        cmds.unknownPlugin(pluginName, remove=True)
        removedPlugins.add(pluginName)
    if message and removedPlugins:
        om2.MGlobal.displayInfo("Success Plugin/s Deleted: {}".format(removedPlugins))
    if message and not removedPlugins:
        om2.MGlobal.displayWarning("No Unknown Plugin/s Found")
    return removedPlugins


def deleteUnknownNodes(message=True):
    """Deletes nodes of unknown type, usually plugins that are missing or not installed.

    Also see removeUnknownPlugins()

    :param message: Report a message to the user?
    :type message: bool
    :return nodesDeleted: Unknown nodes that were deleted
    :rtype nodesDeleted: list(str)
    :return nodesNotDeleted: Unknown nodes that could not be deleted
    :rtype nodesNotDeleted: list(str)
    """
    unknownNodes = cmds.ls(type="unknown")
    nodesDeleted = list()
    nodesNotDeleted = list()
    for node in unknownNodes:
        if not cmds.objExists(node):
            continue
        cmds.lockNode(node, lock=False)
        try:
            cmds.delete(node)
            nodesDeleted.append(node)
        except ValueError:
            nodesNotDeleted.append(node)
    if message:
        if not nodesNotDeleted and nodesDeleted:
            om2.MGlobal.displayInfo("Success Nodes Deleted: {}".format(nodesDeleted))
        elif not nodesDeleted and nodesNotDeleted:
            om2.MGlobal.displayWarning("Warning nodes couldn't be deleted: {}".format(nodesDeleted))
        elif nodesDeleted and nodesNotDeleted:
            om2.MGlobal.displayInfo("Nodes Deleted: {}".format(nodesDeleted))
            om2.MGlobal.displayWarning("Nodes couldn't be deleted: {}".format(nodesDeleted))
            om2.MGlobal.displayWarning("Warning Some nodes couldn't be deleted see script editor")
        else:
            om2.MGlobal.displayInfo("No Nodes Were Deleted")
    return nodesDeleted, nodesNotDeleted


def deleteTurtlePluginScene(removeShelf=True, message=True):
    """Kills the Turtle plugin:

        Removes Turtle from the scene, unloads the plugin and deletes the shelf too.

    :param removeShelf: If True delete the Turtle shelf
    :type removeShelf: bool
    :param message: report a message to the user?
    :type message: bool
    :return turtleDeleted: If True Turtle was removed
    :rtype turtleDeleted: bool
    """
    turtleDeleted = False

    if isPluginLoaded("Turtle"):
        # Delete turtle nodes
        types = cmds.pluginInfo('Turtle', dependNode=True, q=True)
        nodes = cmds.ls(type=types, long=True)
        if nodes:
            cmds.lockNode(nodes, lock=False)
            cmds.delete(nodes)
        cmds.flushUndo()

        # unload will remove other turtle nodes, though should be sorted by the mel eval
        turtleDeleted = True
        cmds.unloadPlugin("Turtle", force=True)

    if removeShelf:  # kill the TURTLE shelf
        if deleteShelf('TURTLE'):
            turtleDeleted = True

    if message:
        if turtleDeleted:
            om2.MGlobal.displayInfo("Success Turtle has been removed")
        else:
            om2.MGlobal.displayWarning("Turtle not found")
    return turtleDeleted


def deleteShelf(name):
    """ Deletes maya shelf

    :param name: Name of shelf
    :type name: str
    :return: Returns true if deleted, False otherwise
    """
    shelves = cmds.tabLayout("ShelfLayout", query=True, childArray=True)
    if name in shelves:
        cmds.deleteUI(name, layout=True)
        return True
    return False



def lockSelectedNodes(unlock=False, message=True):
    """Locks or unlocks the selected nodes, Maya locked nodes are nodes that can't be deleted.

    :param unlock: unlock the nodes instead of locking?
    :type unlock: bool
    :param message: Report a message to the user?
    :type message: bool
    :return nodes: nodes that were unlocked
    :rtype nodes: list(str)
    """
    nodes = cmds.ls(selection=True)
    for node in nodes:
        cmds.lockNode(node, lock=not unlock)
    if message:
        if unlock:
            om2.MGlobal.displayInfo("Nodes Unlocked: {}".format(nodes))
        else:
            om2.MGlobal.displayInfo("Nodes locked: {}".format(nodes))
    return nodes


@contextmanager
def namespaceContext(namespace):
    currentNamespace = om2.MNamespace.currentNamespace()
    existingNamespaces = om2.MNamespace.getNamespaces(currentNamespace, True)
    if currentNamespace != namespace and namespace not in existingNamespaces and namespace != om2.MNamespace.rootNamespace():
        try:
            om2.MNamespace.addNamespace(namespace)
        except RuntimeError:
            logger.error("Failed to create namespace: {}, existing namespaces: {}".format(namespace,
                                                                                          existingNamespaces),
                         exc_info=True)
            om2.MNamespace.setCurrentNamespace(currentNamespace)
            raise
    om2.MNamespace.setCurrentNamespace(namespace)
    try:
        yield
    finally:
        om2.MNamespace.setCurrentNamespace(currentNamespace)


@contextmanager
def isolatedNodes(nodes, panel):
    """Context manager for isolating `nodes` in maya model `panel`

    :param nodes: A list of node fullpaths to isolate
    :type nodes: seq(str)
    :param panel: The maya model panel
    :type panel: str
    """

    cmds.isolateSelect(panel, state=True)
    for obj in nodes:
        cmds.isolateSelect(panel, addDagObject=obj)
    yield
    cmds.isolateSelect(panel, state=False)


def undoDecorator(func):
    """ Allows all cmds,mel commands perform by the  the wrapped `func` into
    a single undo operation

    @undoDecorator
    def myoperationFunc():
        pass
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True, chunkName=func.__name__)
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)

    return inner


@contextmanager
def undoContext(name=None):
    """Context manager for maya undo

    with undoContext:
        cmds.polyCube()
        cmds.sphere()

    """
    try:
        cmds.undoInfo(openChunk=True, chunkName=name or "")
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


def openUndoChunk(name=None):
    """Opens a Maya undo chunk
    """
    cmds.undoInfo(openChunk=True, chunkName=name or "")


def closeUndoChunk():
    """Opens a Maya undo chunk
    """
    cmds.undoInfo(closeChunk=True)


def userShelfDir():
    """ Path to shelf

    :return:
    """
    return cmds.internalVar(userShelfDir=1)


def mayaAppDir():
    """ The Maya preference folder

    Windows Vista, Windows 7, and Windows 8

    \\Users\\<username>\\Documents\\Maya
    Mac OS X

    ~<username>/Library/Preferences/Autodesk/Maya
    Linux (64-bit)

    ~<username>/Maya


    :return:
    """
    return cmds.internalVar(userAppDir=1)