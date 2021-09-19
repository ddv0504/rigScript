__all__ = ("DGNode",
           "DagNode",
           "Plug",
           "createDag",
           "createDG",
           "nodeByObject",
           "nodeByName",
           "nodesByNames",
           "plugByName",
           "lockNodeContext",
           "InvalidPlugPath",
           "ReferenceObjectError",
           "fullNames",
           "shortNames",
           "alphabetizeDagList",
           "selected",
           "select",
           "selectByNames",
           "ContainerAsset",
           "Matrix",
           "TransformationMatrix",
           "Vector",
           "Quaternion",
           "EulerRotation",
           "dgModifier",
           "dagModifier",
           "kTransform",
           "kDependencyNode",
           "kDagNode",
           "kControllerTag",
           "kJoint",
           "kWorldSpace",
           "kTransformSpace",
           "kObjectSpace",
           "kRotateOrder_XYZ",
           "kRotateOrder_YZX",
           "kRotateOrder_ZXY",
           "kRotateOrder_XZY",
           "kRotateOrder_YXZ",
           "kRotateOrder_ZYX",
           "attrtypes"
           )

import logging
from functools import wraps

from maya.api import OpenMaya as om2
from maya.api import OpenMayaAnim as om2Anim
from maya import cmds
from zoovendor.six.moves import range

from zoo.libs.maya.api import plugs
from zoo.libs.maya.api import attrtypes
from zoo.libs.maya.api import generic
from zoo.libs.maya.api import scene
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import constants as apiconstants

Matrix = om2.MMatrix
TransformationMatrix = om2.MTransformationMatrix
Vector = om2.MVector
Quaternion = om2.MQuaternion
EulerRotation = om2.MEulerRotation
kTransform = om2.MFn.kTransform
kDependencyNode = om2.MFn.kDependencyNode
kDagNode = om2.MFn.kDagNode
kControllerTag = om2.MFn.kControllerTag
kJoint = om2.MFn.kJoint
kWorldSpace = om2.MSpace.kWorld
kTransformSpace = om2.MSpace.kTransform
kObjectSpace = om2.MSpace.kObject
dgModifier = om2.MDGModifier
dagModifier = om2.MDagModifier
kRotateOrder_XYZ = apiconstants.kRotateOrder_XYZ
kRotateOrder_YZX = apiconstants.kRotateOrder_YZX
kRotateOrder_ZXY = apiconstants.kRotateOrder_ZXY
kRotateOrder_XZY = apiconstants.kRotateOrder_XZY
kRotateOrder_YXZ = apiconstants.kRotateOrder_YXZ
kRotateOrder_ZYX = apiconstants.kRotateOrder_ZYX

logger = logging.getLogger(__name__)


class ObjectDoesntExist(Exception):
    pass


class InvalidPlugPath(Exception):
    """Raised when Provided path doesn't contain '.'
    """
    pass


class ReferenceObjectError(Exception):
    """Raised when a object is a reference and the requested operation is
    not allowed on a reference
    """
    pass


class InvalidTypeForPlug(Exception):
    """Raised anytime an operation happens on a plug which isn't
    compatible with the datatype, ie. setting fields on non Enum type.
    """
    pass


def lockNodeContext(func):
    """Decorator function to lock and unlock the meta, designed purely for the metaclass
    """

    @wraps(func)
    def locker(*args, **kwargs):
        node = args[0]
        setLocked = False
        if node.isLocked:
            if node.isReferenced():
                raise ReferenceObjectError("Unable to unlock a referenced node: {}".format(node.fullPathName()))
            node.lock(False)
            setLocked = True
        try:
            return func(*args, **kwargs)
        finally:
            if node.exists() and setLocked:
                node.lock(True)

    return locker


def lockNodePlugContext(func):
    @wraps(func)
    def locker(*args, **kwargs):
        plug = args[0]
        node = plug.node()

        setLocked = False
        if node.isLocked:
            if node.isReferenced():
                raise ReferenceObjectError("Unable to unlock a referenced node: {}".format(node.fullPathName()))
            node.lock(False)
            setLocked = True
        try:
            return func(*args, **kwargs)
        finally:
            if node.exists() and setLocked:
                node.lock(True)

    return locker


class DGNode(object):
    """Base Maya node class for Dependency graph nodes , subclasses should implement create()
    and serializeFromScene() methods, can be instantiated directly.

    The intention with the class is to create a thin layer around maya MObject for DGNodes to allow working with the
    maya api 2.0 easier. Much of the code here calls upon `zoo.libs.maya.api` helper functions.

    Any method which returns a node will always return a DGNode, any method that returns an attribute will return a
    om2.MPlug.

    .. code-block:: python

        from zoo.libs.maya.api import plugs
        multi = DGNode()
        multi.create(name="testNode", Type="multipleDivide")
        # set the input1 Vector by using the zoo lib helpers
        plugs.setPlugValue(multi.input1, om2.MVector(10,15,30))
        multi2 = DGNode()
        multi2.create(name="dest", Type="plusMinusAverage")
        # connect the output plug to unconnected elementPlug of the plusminuxaverage node
        multi.connect("output", plugs.nextAvailableElementPlug(multi2.input3D))

    """

    def __init__(self, node=None):
        """

        :param node: The maya node that this class will operate on, if None then you are expected to call create()
        :type node: om2.MObject, None

        """
        self._node = om2.MObjectHandle(node) if node is not None else node
        self._mfn = None  # type: om2.MFnContainerNode
        # this will initialize self._mfn to have a functionSet
        self.mfn()

    def __getitem__(self, item):
        fn = self._mfn
        try:
            return Plug(self, fn.findPlug(item, False))
        except RuntimeError:
            raise KeyError("{} has no attribute by the name: {}".format(self.name(), item))

    def __getattr__(self, name):
        """Attempts to retrieve the MPlug for this node. Falls back to the super class __getattribute__ otherwise.

        :param name: The attribute name
        :type name: str
        :rtype: om2.MPlug
        """
        attr = self.attribute(name)
        if attr is not None:
            return attr
        return super(DGNode, self).__getattribute__(name)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super(DGNode, self).__setattr__(key, value)
            return
        if self.hasAttribute(key) is not None:
            if isinstance(value, Plug):
                self.connect(key, value)
                return
            self.setAttribute(key, value)
            return
        super(DGNode, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        if key.startswith("_"):
            super(DGNode, self).__setitem__(key, value)
            return
        if self.hasAttribute(key) is not None:
            if isinstance(value, Plug):
                self.connect(key, value)
                return
            self.setAttribute(key, value)
            return
        else:
            raise RuntimeError("Node: {} has no attribute called: {}".format(self.name(), key))

    def __hash__(self):
        return self._node.hashCode()

    def __repr__(self):
        return "<{}>{}".format(self.__class__.__name__, self.name())

    def __str__(self):
        return self.name()

    def __ne__(self, other):
        """ Compares the nodes with  != .

        :param other:
        :type other: :class:`DGNode` or :class:`DagNode`
        :rtype: bool
        """
        if not isinstance(other, DGNode):
            return False
        return self._node != other.handle()

    def __eq__(self, other):
        """ Compares the two nodes with == .

        :param other:
        :type other: :class:`DGNode` or :class:`DagNode`
        :rtype: bool
        """
        if not isinstance(other, DGNode) or (isinstance(other, DGNode) and other.handle() is None):
            return False

        return self._node == other.handle()

    def __contains__(self, key):
        return self.hasAttribute(key)

    def __delitem__(self, key):
        self.deleteAttribute(key)

    def setObject(self, mObject):
        """Set's the MObject For this :class:`DGNode` instance

        :param mObject: The maya api om2.MObject representing a MFnDependencyNode
        :type mObject: om2.MObject
        """
        if not mObject.hasFn(om2.MFn.kDependencyNode):
            raise ValueError("Invalid MObject Type {}".format(om2.MFnDependencyNode(mObject).apiTypeStr))
        self._node = om2.MObjectHandle(mObject)
        self._mfn = om2.MFnDependencyNode(mObject)

    def object(self):
        """Returns the object of the node

        :rtype: cmds.MObject
        """
        if self.exists():
            return self._node.object()

    def handle(self):
        """Returns the MObjectHandle instance attached to the class. Client of this function is responsible for
        dealing with object existence.

        :rtype: om2.MObjectHandle
        """
        return self._node

    def typeId(self):
        """Returns the maya typeId from the functionSet

        :return: The type id or -1. if -1 it's concerned a invalid node.
        :rtype: int
        """
        if self.exists():
            return self._mfn.typeId
        return -1

    def hasFn(self, fnType):
        return self._node.object().hasFn(fnType)

    def apiType(self):
        """Returns the maya apiType int

        :rtype: int
        """
        return self._node.object().apiType()

    @property
    def typeName(self):
        """Returns the maya apiType int

        :rtype: int
        """
        return self._mfn.typeName

    def exists(self):
        """ Returns True if the node is currently valid in the maya scene

        :rtype: bool
        """
        node = self._node
        if node is None:
            return False
        return node.isValid() and node.isAlive()

    def fullPathName(self, partialName=False, includeNamespace=True):
        """returns the nodes scene name, this result is dependent on the arguments, by default
        always returns the full path

        :param partialName: the short name of the node
        :type partialName: bool
        :param includeNamespace: True if the return name includes the namespace, default True
        :type includeNamespace: bool
        :return: the nodes Name
        :rtype: str
        """
        if self.exists():
            return nodes.nameFromMObject(self.object(), partialName, includeNamespace)

        import traceback
        traceback.print_stack()
        raise RuntimeError("Current node doesn't exist!")

    def name(self, includeNamespace=True):
        """Returns the name for the node which is achieved by the name or id  use self.fullPathName for the
        nodes actually scene name
        """
        if self.exists():
            if includeNamespace:
                return self.mfn().name()
            return om2.MNamespace.stripNamespaceFromName(self.mfn().name())
        return ""

    @lockNodeContext
    def rename(self, name, maintainNamespace=False, mod=None):
        """Renames this node, If


        :param name: the new name
        :type name: str
        :param maintainNamespace: If True then the current namespace if applicable will be maintained \
        on rename eg namespace:newName
        :type maintainNamespace: bool
        :param mod: Modifier to add the operation to
        :type mod: om2.MDGModifier
        :return: True if succeeded
        :rtype: bool
        """
        if maintainNamespace:
            currentNamespace = self.namespace()
            name = ":".join([currentNamespace, name])
        try:
            nodes.rename(self.object(), name, modifier=mod)
        except RuntimeError:
            logger.error("Failed to rename attribute: {}-{}".format(self.name(), name), exc_info=True)
            return False
        return True

    @property
    def isLocked(self):
        """Returns True if the current node is locked, calls upon om2.MFnDependencyNode().isLocked

        :rtype: bool
        """
        return self.mfn().isLocked

    def lock(self, state, mod=None):
        """Sets the lock state for this node

        :param state: the lock state to change too.
        :type state: bool
        :return: True if the node was set
        :rtype: bool
        """
        return nodes.lockNode(self._node.object(), state, modifier=mod)

    def isReferenced(self):
        """ Returns true if this node is referenced

        """
        return self._mfn.isFromReferencedFile

    def isDefaultNode(self):
        return self._mfn.isDefaultNode

    def mfn(self):
        """Returns the Function set for the node

        :return: either the dagnode or dependencyNode depending on the types node
        :rtype: om2.MDagNode or om2.MDependencyNode
        """
        # if not self.exists():
        #     logger.warn("Error: Object doesn't exist")
        #     #raise ObjectDoesntExist("Error: Object doesn't exist")
        #     return None

        if self._mfn is None and self._node is not None:
            mfn = om2.MFnDependencyNode(self.object())
            self._mfn = mfn
            return mfn

        return self._mfn

    def renameNamespace(self, namespace):
        """Renames the current namespace to the new namespace

        :param namespace: the new namespace eg. myNamespace:subnamespace
        :type namespace: str
        """
        currentNamespace = self.namespace()
        if not currentNamespace:
            return
        parentNamespace = self.parentNamespace()
        # we are at the root namespace so add a new namespace and add our node
        if currentNamespace == ":":
            om2.MNamespace.addNamespace(namespace)
            self.rename(":".join([namespace, self.name()]))
            return
        om2.MNamespace.setCurrentNamespace(parentNamespace)
        om2.MNamespace.renameNamespace(currentNamespace, namespace)
        om2.MNamespace.setCurrentNamespace(namespace)

    def setNotes(self, notes):
        """Sets the note attributes value, if the note attribute doesn't exist it'll be created.

        :param notes: The notes to add.
        :type notes: str
        :return: The note plug.
        :rtype: :class:`Plug`
        """
        note = self.attribute("notes")
        if not note:
            return self.addAttribute("notes", attrtypes.kMFnDataString, value=notes)
        note.setString(notes)
        return note

    def namespace(self):
        """Returns the current namespace for the node

        :return: the nodes namespace
        :rtype: str
        """
        name = om2.MNamespace.getNamespaceFromName(self.fullPathName()).split("|")[-1]
        root = om2.MNamespace.rootNamespace()
        if not name.startswith(root):
            name = root + name
        return name

    def parentNamespace(self):
        """returns the parent namespace from the node

        :return: The parent namespace
        :rtype: str
        """
        namespace = self.namespace()
        if namespace == ":":
            return namespace
        om2.MNamespace.setCurrentNamespace(namespace)
        parent = om2.MNamespace.parentNamespace()

        om2.MNamespace.setCurrentNamespace(namespace)
        return parent

    def removeNamespace(self):
        """Removes the namespace from the node

        :return: True if the namespace was removed
        :rtype: bool
        """
        namespace = self.namespace()
        if namespace:
            om2.MNamespace.moveNamespace(namespace, om2.MNamespace.rootNamespace(), True)
            om2.MNamespace.removeNamespace(namespace)
            return True
        return False

    def delete(self, mod=None):
        """Deletes the node from the scene, subclasses should implement this method if the class creates multiple nodes

        :param mod: Modifier to add the delete to
        :type mod: :class:`om2.MDGModifier` or :class:`om2.MDagModifier`
        :return: True if the node gets deleted successfully
        :rtype: bool
        """
        if self.exists():
            if self.isLocked:
                self.lock(False)
            try:
                if mod:
                    mod.commandToExecute('delete {}'.format(self.fullPathName()))
                    mod.doIt()
                else:
                    cmds.delete(self.fullPathName())

                self._mfn = None
                self._node = None
                return True
            except RuntimeError:
                logger.error("Failed node deletion,{}".format(self.mfn().name()),
                             exc_info=True)
                raise
        return False

    def hasAttribute(self, attributeName):
        """ Returns True or False if the attribute exist's on this node

        :param attributeName: the attribute Name
        :type attributeName: str
        :rtype: bool
        """
        # arrays don't get picked up by hasAttribute unfortunately
        if "[" in attributeName:
            sel = om2.MSelectionList()
            try:
                sel.add(attributeName)
                return True
            except RuntimeError:
                return False
        return self.mfn().hasAttribute(attributeName)

    @lockNodeContext
    def addAttribute(self, name, Type=attrtypes.kMFnNumericDouble, mod=None, **kwargs):
        """Helper function to add an attribute to this node

        :param name: the attributeName
        :type name: str
        :param Type: for full support list of types see module zoo.libs.maya.api.attrtypes.py or None for compound type
        :type Type: int or None
        :return: the MPlug for the new attribute
        :rtype: om2.MPlug

        """
        if self.hasAttribute(name):
            return self.attribute(name)
        children = kwargs.get("children")
        if children:

            plug = self.addCompoundAttribute(name, attrMap=children, mod=mod, **kwargs)
        else:
            node = self.object()
            attr = nodes.addAttribute(node, name, name, Type, mod=mod, **kwargs)
            plug = Plug(self, om2.MPlug(node, attr.object()))

        return plug

    @lockNodeContext
    def addProxyAttribute(self, sourcePlug, name):
        if self.hasAttribute(name):
            return
        plugData = plugs.serializePlug(sourcePlug)
        plugData["longName"] = name
        plugData["shortName"] = name
        return Plug(self,
                    om2.MPlug(self.object(),
                              nodes.addProxyAttribute(self.object(), sourcePlug.plug(), **plugData).object())
                    )

    def createAttributesFromDict(self, data):
        """Creates an attribute on the node given a dict of attribute data

        Data is in the form::

                    {
                        "channelBox": true,
                        "default": 3,
                        "isDynamic": true,
                        "keyable": false,
                        "locked": false,
                        "max": 9999,
                        "min": 1,
                        "name": "jointCount",
                        "softMax": null,
                        "softMin": null,
                        "Type": 2,
                        "value": 3
                    }

        :param data: The serialized form of the attribute
        :type data: dict
        :return: A list of created MPlugs
        :rtype: list(om2.MPlug)
        """
        created = []
        for name, attrData in iter(data.items()):
            plug = self.addAttribute(name, attrData["Type"],
                                     value=attrData["value"],
                                     default=attrData["default"],
                                     keyable=attrData["keyable"],
                                     channelBox=attrData["channelBox"])

            plugs.setLockState(plug, attrData["locked"])
            plugs.setMin(plug, attrData["min"])
            plugs.setMax(plug, attrData["max"])
            plugs.setSoftMin(plug, attrData["softMin"])
            plugs.setSoftMax(plug, attrData["softMax"])
            created.append(Plug(self, plug))
        return created

    @lockNodeContext
    def addCompoundAttribute(self, name, attrMap, isArray=False, mod=None, **kwargs):
        """Creates a Compound attribute with the given children attributes

        :param name: the compound longName
        :type name: str
        :param attrMap: [{"name":str, "type": attrtypes.kType, "isArray": bool}]
        :type attrMap: list(dict())
        :param isArray: Is this compound attribute an array
        :type isArray: bool
        :return: the Compound MPlug
        :rtype: :class:`om2.MPlug` or :class:`zoo.libs.maya.zapi.base.Plug`

        .. code-block:: python

            >>>attrMap = [{"name": "something", "type": attrtypes.kMFnMessageAttribute, "isArray": False}]
            print attrMap
            # result <OpenMaya.MObject object at 0x00000000678CA790> #

        """
        node = self.object()
        compound = nodes.addCompoundAttribute(self.object(), name, name, attrMap, isArray=isArray, mod=mod, **kwargs)
        return Plug(self, om2.MPlug(node, compound.object()))

    def renameAttribute(self, name, newName):
        try:
            plug = self.attribute(name)
        except RuntimeError:
            raise AttributeError("No attribute named {}".format(name))
        plug.rename(newName)
        return True

    def deleteAttribute(self, name, mod=None):
        """Remove's the attribute for this node given the attribute name

        :param name: The attribute name
        :type name: str
        :rtype: bool
        """
        attr = self.attribute(name)
        if attr is not None:
            attr.delete(modifier=mod)
            return True
        return False

    def setAttribute(self, name, value, mod=None, apply=True):
        """Sets the value of the attribute if it exists

        :param name: The attribute name to set
        :type name: str
        :param value: The value to for the attribute, see zoo.libs.maya.api.plugs.setPlugValue
        :type value: maya value type
        :param mod:
        :type mod: om2.MDGModifier

        """
        attr = self.attribute(name)
        if attr is not None:
            attr.set(value, mod=mod, apply=apply)
            return True
        return False

    def attribute(self, name):
        """Finds the attribute 'name' on the node if it exists

        :param name: the attribute Name
        :type name: str
        :rtype: :class:`Plug` or list[:class:`Plug`]
        """
        fn = om2.MFnDependencyNode(self.object())
        if fn.hasAttribute(name):
            return Plug(self, fn.findPlug(name, False))

    def setLockStateOnAttributes(self, attributes, state=True):
        """Locks and unlocks the given attributes

        :param attributes: a list of attribute name to lock
        :type attributes: seq(str)
        :param state: True to lock and False to unlcck
        :type state: bool
        :return: True is successful
        :rtype: bool
        """
        nodes.setLockStateOnAttributes(self.object(), attributes, state)

    def showHideAttributes(self, attributes, state=True):
        """Shows or hides and attribute in the channel box

        :param attributes: attribute names on the given node
        :type attributes: seq(str)
        :param state: True for show False for hide, defaults to True
        :type state: bool
        :return: True if successful
        :rtype: bool
        """
        nodes.showHideAttributes(self.object(), attributes, state)

    def iterAttributes(self):
        """Generator function to iterate over all the attributes on this node,
        calls on zoo.libs.maya.api.nodes.iterAttributes

        :return: A generator function containing MPlugs
        :rtype: Generator(:class:`Plug`)
        """
        for a in nodes.iterAttributes(self.object()):
            yield Plug(self, a)

    def iterExtraAttributes(self, skip=None, filteredTypes=None, includeAttributes=None):
        """Generator function that loops all extra attributes of the node

        :rtype: Generator(:class:`Plug`)
        """
        for a in nodes.iterExtraAttributes(self.object(),
                                           skip=skip,
                                           filteredTypes=filteredTypes,
                                           includeAttributes=includeAttributes):
            yield Plug(self, a)

    def iterConnections(self, source=True, destination=True):
        """
        :param source: if True then return all nodes downstream of the node
        :type source: bool
        :param destination: if True then return all nodes upstream of this node
        :type destination: bool
        :return:
        :rtype: generator
        """
        for sourcePlug, destinationPlug in nodes.iterConnections(self.object(), source, destination):
            yield Plug(self, sourcePlug), Plug(nodeByObject(destinationPlug.node()), destinationPlug)

    def sources(self):
        """Generator Function that returns a tuple of connected MPlugs.

        :return: First element is the Plug on this node instance, the second if the connected MPlug
        :rtype: Generator(tuple(:class:`Plug`, :class:`Plug`))
        """
        for source, destination in nodes.iterConnections(self.object(), source=True, destination=False):
            yield Plug(self, source), Plug(self, destination)

    def destinations(self):
        """Generator Function that returns a tuple of connected MPlugs.

        :return: First element is the Plug on this node instance, the second if the connected MPlug
        :rtype: Generator(tuple(:class:`Plug`, :class:`Plug`))
        """
        for source, destination in nodes.iterConnections(self.object(),
                                                         source=False,
                                                         destination=True):
            yield Plug(self, source), Plug(self, destination)

    def connect(self, attributeName, destinationPlug):
        """Connects the attribute on this node as the source to the destination plug

        :param attributeName: the attribute name that will be used as the source
        :type attributeName: str
        :param destinationPlug: the destinationPlug
        :type destinationPlug: :class:`Plug`
        :return: True if the connection was made
        :rtype: bool
        """
        source = self.attribute(attributeName)
        if source is not None:
            return source.connect(destinationPlug)
        return False

    def connectDestinationAttribute(self, attributeName, sourcePlug):
        """Connects the attribute on this node as the destination to the source plug

        :param attributeName: the attribute name that will be used as the source
        :type attributeName: str
        :param sourcePlug: the sourcePlug to connect to
        :type sourcePlug: :class:`Plug`
        :return: True if the connection was made
        :rtype: bool
        """
        attr = self.attribute(attributeName)
        if attr is not None:
            return sourcePlug.connect(attr)
        return False

    def create(self, name, Type, mod=None):
        """Each subclass needs to implement this method to build the node into the application scene
        The default functionality is to create a maya dependencyNode

        :param name: The name of the new node
        :type name: str
        :param Type: the maya node type to create
        :type Type: str
        """
        self.setObject(nodes.createDGNode(name, nodeType=Type, mod=mod))
        return self

    def serializeFromScene(self, skipAttributes=(),
                           includeConnections=True,
                           extraAttributesOnly=False):
        """This method is to return a dict that is compatible with JSON

        :param extraAttributesOnly: If True then only extra attributes will be serialized
        :type extraAttributesOnly: bool
        :rtype: dict
        """
        try:
            return nodes.serializeNode(self.object(),
                                       skipAttributes=skipAttributes,
                                       includeConnections=includeConnections,
                                       extraAttributesOnly=extraAttributesOnly)
        # to protect against maya standard errors
        except RuntimeError:
            return dict()

    def sourceNode(self, plug):
        """ Source node of the plug

        :param plug: Plug to return the source node of
        :type plug: zoo.libs.maya.zapi.base.Plug
        :return:
        :rtype: DagNode
        """
        source = plug.source()
        return source.node() if source is not None else None

    def sourceNodeByName(self, plugName):
        """ Source Node by name

        :param plugName: Name of the plug to return the source node of
        :type plugName: str
        :return:
        :rtype:
        """
        plug = self.attribute(plugName)
        if plug is not None:
            return self.sourceNode(plug)


class DagNode(DGNode):
    """Base node for DAG nodes, contains functions for parenting, iterating the Dag etc
    """

    def serializeFromScene(self, skipAttributes=(),
                           includeConnections=True,
                           includeAttributes=(),
                           extraAttributesOnly=True):
        """This method is to return a dict that is compatible with JSON

        :rtype: dict
        """
        rotationOrder = self.rotationOrder()
        worldMatrix = nodes.getWorldMatrix(self.object())
        trans, rot, scale = nodes.decomposeMatrix(worldMatrix,
                                                  generic.intToMTransformRotationOrder(rotationOrder)
                                                  )
        try:

            data = nodes.serializeNode(self.object(),
                                       skipAttributes=skipAttributes,
                                       includeConnections=includeConnections,
                                       includeAttributes=includeAttributes,
                                       extraAttributesOnly=extraAttributesOnly)
            data.update({"rotate": tuple(rot),
                         "translate": tuple(trans),
                         "scale": tuple(scale),
                         "rotateOrder": rotationOrder,
                         "matrix": list(self.matrix()),
                         "worldMatrix": list(worldMatrix)})
            return data
        # to protect against maya standard errors
        except RuntimeError:
            return dict()

    def create(self, name, Type, parent=None):
        """Each subclass needs to implement this method to build the node into the application scene
        The default functionality is to create a maya DagNode

        :param name: The name of the new node
        :type name: str
        :param Type: the maya node type to create
        :type Type: str
        :param parent: The parent object
        :type parent: :class:`om2.MObject`

        """
        if isinstance(parent, DagNode):
            parent = parent.object()
        n = nodes.createDagNode(name, nodeType=Type, parent=parent)
        self.setObject(n)
        return self

    def dagPath(self):
        """Returns the MDagPath of this node. Calls upon om2.MFnDagNode().getPath()

        :rtype: om2.MDagPath
        """
        return self.mfn().getPath()

    def depth(self):
        """Returns the depth level this node sits within the hierarchy.

        :rtype: int
        """
        return self.fullPathName().count("|") - 1

    def setObject(self, mObject):
        """Set's the MObject For this :class:`DagNode` instance

        :param mObject: The maya api om2.MObject representing a MFnDagNode
        :type mObject: om2.MObject
        """
        if not mObject.hasFn(om2.MFn.kDagNode):
            raise TypeError("Invalid MObject type {}".format(om2.MFnDependencyNode(mObject).typeName))
        self._node = om2.MObjectHandle(mObject)
        self._mfn = om2.MFnDagNode(mObject)

    def mfn(self):
        """Returns the maya api Dag function set

        :rtype: om2.MFnDagNode
        """
        if self._mfn is None and self._node is not None:
            mfn = om2.MFnDagNode(self.object())
            self._mfn = mfn
            return mfn
        return self._mfn

    def parent(self):
        """Returns the parent nodes as an MObject

        :rtype: om2.MObject or DagNode or None
        """
        obj = self.object()
        if obj is not None:
            parent = nodes.getParent(obj)
            if parent:
                return DagNode(parent)
            return parent

    def root(self):
        """Returns the Root DagNode Parent from this node instance

        :rtype: :class:`DagNode`
        """
        return DagNode(nodes.getRoot(self.object))

    def child(self, index, nodeTypes=()):
        """Finds the immediate child object given the child index

        :param index: the index of the child to find
        :type index: int
        :param nodeTypes: Node mfn type eg. om2.MFn.kTransform
        :type nodeTypes: tuple(om2.MFn.kType)
        :return: Returns the object as a TreeNode instance
        :rtype: TreeNode
        """

        path = self.dagPath()
        currentIndex = 0
        for i in range(path.childCount()):
            child = path.child(i)
            if (not nodeTypes or child.apiType() in nodeTypes) and currentIndex == index:
                return DagNode(child)

    def children(self, nodeTypes=()):
        """Returns all the children nodes immediately under this node

        :return: A list of mobjects representing the children nodes
        :rtype: list(:class:`DagNode`)
        """
        path = self.dagPath()
        children = []
        for i in range(path.childCount()):
            child = path.child(i)
            if not nodeTypes or child.apiType() in nodeTypes:
                children.append(DagNode(child))
        return children

    def shapes(self):
        """Finds and returns all shape nodes under this dagNode instance

        :rtype: list(:class:`DagNode`)
        """
        path = self.dagPath()
        shapeCount = path.numberOfShapesDirectlyBelow()
        paths = [None] * shapeCount
        for i in range(shapeCount):
            dagPath = om2.MDagPath(path)
            dagPath.extendToShape(i)
            paths[i] = DagNode(dagPath.node())
        return paths

    def deleteShapeNodes(self):
        for shape in self.shapes():
            shape.delete()

    def iterParents(self):
        """Generator function to iterate each parent until to root has been reached.

        :rtype: Generator(:class`DagNode`)
        """
        for parent in nodes.iterParents(self.object()):
            yield DagNode(parent)

    def iterChildren(self, node=None, recursive=True, nodeTypes=None):
        """kDepthFirst generator function that loops the Dag under this node

        :param node: The maya object to loop under , if none then this node will be used,
        :type node: :class:`DagNode`
        :param recursive: If true then will recursively loop all children of children
        :type recursive: bool
        :param nodeTypes:
        :type nodeTypes: tuple(om2.MFn.kType)
        :return:
        :rtype: collections.Iterable[DagNode or DGNode]
        """
        nodeTypes = nodeTypes or ()
        selfObject = node.object() if node is not None else self.object()

        fn = om2.MDagPath.getAPathTo(selfObject)
        path = fn.getPath()
        for i in range(path.childCount()):
            child = path.child(i)
            if not nodeTypes or child.apiType() in nodeTypes:
                yield DagNode(child)
            if recursive:
                for c in self.iterChildren(DagNode(child), recursive, nodeTypes):
                    yield c

    def addChild(self, node):
        """Child object to reparent to this node

        :param: node: the child node
        :type node: :class:`DagNode`
        """
        node.setParent(self)

    def siblings(self, nodeTypes=(kTransform,)):
        """Generator function to return all sibling nodes of the current node.
        This requires this node to have a parent node.

        :param nodeTypes: A tuple of om2.MFn.kConstants
        :type nodeTypes: tuple
        :return:
        :rtype: Generator(:class:`DagNode`)
        """
        parent = self.parent()
        if parent is None:
            return
        for child in parent.iterChildren(recursive=False, nodeTypes=nodeTypes):
            if child != self:
                yield child

    @lockNodeContext
    def setParent(self, parent, maintainOffset=True, mod=None, apply=True):
        """Sets the parent of this dag node

        :param parent: the new parent node
        :type parent: :class:`DagNode` or None
        :param maintainOffset: Whether or not to maintain it's current position in world space.
        :type maintainOffset: bool
        :param mod: The MDagModifier to add to, if none it will create one
        :type mod: om2.MDagModifier
        :param apply: Apply the modifier immediately if true, false otherwise
        :type apply: bool
        :return: The maya MDagModifier either provided via mod argument or a new instance.
        :rtype: :class:`dagModifier`
        """
        parentLock = False
        setLocked = False
        newParent = None
        if parent is not None:
            newParent = parent.object()
            parentLock = parent.isLocked
            if parentLock:
                setLocked = True
                parent.lock(False)
        try:
            result = nodes.setParent(self.object(), newParent,
                                     maintainOffset=maintainOffset, mod=mod, apply=apply)
        finally:
            if setLocked:
                parent.lock(parentLock)
        return result

    def hide(self, mod=None, apply=True):
        """ Sets the current node visibility to 0.0

        :param mod: The mdg modifier to use
        :type mod: :class:`om2.MDGModifier` or :class:`om2.MDagModifier`
        :param apply: Apply instantly if true, false otherwise
        :type apply: bool
        :return:
        :rtype: bool
        """
        self.setVisible(False, mod, apply)

    def isHidden(self):
        """Returns whether this node is visible
        :rtype: bool
        """
        vis = self._mfn.findPlug("visibility", False).asFloat()
        return vis < 1.0

    def show(self, mod=None, apply=True):
        """ Sets the current node visibility to 1.0

        :param mod: The mdg modifier to use
        :type mod: :class:`om2.MDGModifier` or :class:`om2.MDagModifier`
        :param apply: Apply instantly if true, false otherwise
        :type apply: bool
        :return:
        :rtype: bool
        """
        return self.setVisible(True, mod=mod, apply=apply)

    def setVisible(self, vis, mod=None, apply=True):
        """ Set visibility of node

        :param vis: Set visibility on or off
        :type vis: bool
        :param mod: MDG Modifier
        :type mod: :class:`om2.MDGModifier` or :class:`om2.MDagModifier`
        :param apply: Apply immediately or later
        :type apply: bool
        :return:
        :rtype:
        """

        visPlug = self._mfn.findPlug("visibility", False)
        if visPlug.isLocked:
            return False
        visFloat = 1.0 if vis else 0.0
        plugs.setPlugValue(visPlug, visFloat, mod, apply=apply)
        return True

    @lockNodeContext
    def delete(self, mod=None):
        """ Removes this node from the scene starting from the leaf child then recursively deletes

        :param mod: Modifier to add the delete to
        :type mod: :class:`om2.MDGModifier` or `om2.MDagModifier`
        """
        if not self.exists():
            self._node = None
            self._mfn = None
            return
        try:

            if mod:
                mod.commandToExecute('delete {}'.format(self.fullPathName()))
                mod.doIt()
            else:
                cmds.delete(self.fullPathName())
            self._node = None
            self._mfn = None

        except Exception:
            logger.error("Failed to delete nodes", exc_info=True)
            raise

    def translation(self, space=om2.MSpace.kWorld):
        """Returns the translation for this node

        :param space: The coordinate system to use
        :type space: om2.MFn.type
        :return: the object translation in the form om2.MVector
        :rtype: om2.MVector
        """
        return nodes.getTranslation(self.object(), space)

    def rotation(self, space=kTransformSpace, asQuaternion=True):
        """Returns the rotation for the node

        :param space: The coordinate system to use
        :type space: om2.MFn.type
        :param asQuaternion: If True then rotations will be return in Quaternion form
        :type asQuaternion: bool
        :return: the rotation in the form of euler rotations
        :rtype: om2.MEulerRotation or om2.MQuaternion
        """
        return nodes.getRotation(self.dagPath(), space, asQuaternion=asQuaternion)

    def scale(self):
        """Return the scale for this node in the form of a MVector

        :return: The object scale
        :rtype: om2.MVector
        """
        return om2.MVector(plugs.getPlugValue(self._mfn.findPlug("scale", False)))

    def setWorldMatrix(self, matrix, mod=None):
        """Sets the world matrix of this node.

        :param mod:
        :type mod: :class:`om2.MDagModifier or om2.MDGModifier`
        :param matrix: The world matrix to set
        :type matrix: MMatrix
        """
        nodes.setMatrix(self.object(), matrix, space=om2.MSpace.kWorld)

    def worldMatrix(self):
        """Returns the world matrix of this node in the form of MMatrix.

        :return: The world matrix
        :rtype: MMatrix
        """
        return nodes.getWorldMatrix(self.object())

    def matrix(self):
        """Returns the local MMatrix for this node.

        :rtype: :class:`MMatrix`
        """
        return nodes.getMatrix(self.object())

    def setMatrix(self, matrix):
        """Sets the local matrix for this node.

        :param matrix: The local matrix to set.
        :type matrix: :class:`om2.MMatrix`
        """
        nodes.setMatrix(self.object(), matrix, space=om2.MSpace.kTransform)

    def parentInverseMatrix(self):
        """Returns the parent inverse matrix

        :return: the parent inverse matrix
        :rtype: om2.MMatrix
        """
        return nodes.getParentInverseMatrix(self.object())

    def offsetMatrix(self, targetNode, space=kWorldSpace):
        """Returns the offset
        """
        return nodes.getOffsetMatrix(self.object(), targetNode.object(), space=space)

    def decompose(self):
        """Returns the world matrix decomposed for this node.

        :rtype tuple(om2.MVector, om2.MQuaternion, tuple(float, float, float))
        """
        return nodes.decomposeMatrix(self.worldMatrix(),
                                     generic.intToMTransformRotationOrder(self.rotationOrder()),
                                     space=om2.MSpace.kWorld)

    def resetTransform(self, translate=True, rotate=True, scale=True):
        if translate:
            self.setTranslation((0, 0, 0))
        if rotate:
            self.setRotation(Quaternion(), space=kTransformSpace)
        if scale:
            self.setScale((1, 1, 1))

    def setTranslation(self, translation, space=None):
        """Sets the translation component of this control, if cvs is True then translate the cvs instead

        :param translation: The MVector that represent the position based on the space given.
        :type translation: MVector
        :param space: the space to work on eg.MSpace.kObject or MSpace.kWorld
        :type space: int
        """
        space = space or kTransformSpace
        nodes.setTranslation(self.object(), om2.MVector(translation), space)

    def setRotation(self, rotation, space=kWorldSpace):
        """Set's the rotation on the transform control using the space.

        :param rotation: the eulerRotation to rotate the transform by
        :type rotation: om.MEulerRotation or MQuaternion or seq
        :param space: the space to work on
        :type space: om.MSpace
        """
        trans = om2.MFnTransform(self._mfn.getPath())
        if isinstance(rotation, Quaternion):
            trans.setRotation(rotation, space)
            return
        elif isinstance(rotation, (tuple, list)):
            if space == kWorldSpace and len(rotation) > 3:
                rotation = om2.MQuaternion(rotation)
            else:
                rotation = om2.MEulerRotation(rotation)
        if space != kTransformSpace and isinstance(rotation, EulerRotation):
            space = kTransformSpace

        trans.setRotation(rotation, space)

    def setScale(self, scale):
        """Applies the specified scale vector to the transform or the cvs

        :type scale: sequence
        """
        trans = om2.MFnTransform(self._mfn.getPath())
        trans.setScale(scale)

    def rotationOrder(self):
        """Returns the rotation order for this node

        :return: The rotation order
        :rtype: int
        """
        return generic.intToMTransformRotationOrder(self.rotateOrder.value()) - 1

    def setRotationOrder(self, rotateOrder=None):
        """Sets rotation order for the control

        :param rotateOrder: zoo.libs.maya.api.constants.kRotateOrder*
        :type rotateOrder: int
        """
        if rotateOrder is None:
            rotateOrder = apiconstants.kRotateOrder_XYZ
        rotateOrder = generic.intToMTransformRotationOrder(rotateOrder)
        trans = om2.MFnTransform(self._mfn.getPath())
        trans.setRotationOrder(rotateOrder, True)

    def setPivot(self, vec, type_=("t", "r", "s"), space=None):
        """Sets the pivot point of the object given the MVector

        :param vec: float3
        :type vec: om.MVector
        :param type_: t for translate, r for rotation, s for scale
        :type type_: sequence(str)
        :param space: the coordinate space
        :type space: om2.MSpace
        """
        space = space or om2.MSpace.kObject
        transform = om2.MFnTransform(self._mfn.getPath())
        if "t" in type_:
            transform.setScalePivotTranslation(vec, space)
        if "r" in type_:
            transform.setRotatePivot(vec, space)
        if "s" in type_:
            transform.setScalePivot(vec, space)

    def connectLocalTranslate(self, driven, axis=(True, True, True), force=True):
        """Connect's the local translate plugs to the driven node.

        :param driven: The node that will be driven by the current instance
        :type driven:  :class:`DGNode`
        :param axis: A 3Tuple consisting of bool if True then the translate(element) will be connected
        :type axis: tuple(bool)
        :param force: IF True the connections will be forced by first disconnecting any existing connections.
        :type force: bool
        """
        self.attribute("translate").connect(driven.attribute("translate"), axis, force=force)

    def connectLocalRotate(self, driven, axis=(True, True, True), force=True):
        """Connect's the local Rotate plugs to the driven node.

        :param driven: The node that will be driven by the current instance
        :type driven:  :class:`DGNode`
        :param axis: A 3Tuple consisting of bool if True then the rotate(element) will be connected
        :type axis: tuple(bool)
        :param force: IF True the connections will be forced by first disconnecting any existing connections.
        :type force: bool
        """
        self.attribute("rotate").connect(driven.attribute("rotate"), axis, force=force)

    def connectLocalScale(self, driven, axis=(True, True, True), force=True):
        """Connect's the local scale plugs to the driven node.

        :param driven: The node that will be driven by the current instance
        :type driven:  :class:`DGNode`
        :param axis: A 3Tuple consisting of bool if True then the scale (element) will be connected
        :type axis: tuple(bool)
        :param force: IF True the connections will be forced by first disconnecting any existing connections.
        :type force: bool
        """
        self.attribute("scale").connect(driven.attribute("scale"), axis, force=force)

    def connectLocalSrt(self, driven, scaleAxis=(True, True, True),
                        rotateAxis=(True, True, True), translateAxis=(True, True, True), force=True):
        """Connect's the local translate, rotate, scale plugs to the driven node.

        :param driven: The node that will be driven by the current instance
        :type driven: :class:`DGNode`
        :param translateAxis: A 3Tuple consisting of bool if True then the translate(element) will be connected
        :type translateAxis: tuple(bool)
        :param rotateAxis: A 3Tuple consisting of bool if True then the rotate(element) will be connected
        :type rotateAxis: tuple(bool)
        :param scaleAxis: A 3Tuple consisting of bool if True then the rotate(element) will be connected
        :type scaleAxis: tuple(bool)
        :param force: IF True the connections will be forced by first disconnecting any existing connections.
        :type force: bool
        """
        self.connectLocalTranslate(driven, axis=translateAxis, force=force)
        self.connectLocalRotate(driven, axis=rotateAxis, force=force)
        self.connectLocalScale(driven, axis=scaleAxis, force=force)

    def aimToChild(self, aimVector, upVector):
        child = self.child(0, nodeTypes=(om2.MFn.kTransform,))
        # if its the leaf then set the rotation to zero, is this ideal?
        if child is None:
            self.setRotation(om2.MQuaternion())
            return
        scene.aimNodes(targetNode=child.object(),
                       driven=[self.object()],
                       aimVector=aimVector,
                       upVector=upVector)

    def boundingBox(self):
        return self._mfn.boundingBox

    def setShapeColour(self, colour, shapeIndex=None):
        """Sets the color of this node transform or the node shapes.  if shapeIndex is None
        then the transform colour will be set, if -1 then all shapes

        :param colour:
        :type colour: tuple(float)
        :param shapeIndex:
        :type shapeIndex: int or None
        """

        if shapeIndex is not None:
            # do all shapes
            if shapeIndex == -1:
                shapes = nodes.shapes(self.dagPath())
                for shape in iter(shapes):
                    nodes.setNodeColour(shape.node(), colour)
            else:
                shape = nodes.shapeAtIndex(self.object(), shapeIndex)
                nodes.setNodeColour(shape.node, colour)
            return
        if len(colour) == 3:
            nodes.setNodeColour(self.object(), colour)

    connectLocalTrs = connectLocalSrt


class ContainerAsset(DGNode):
    """Maya Asset container class
    """

    def members(self):
        return map(nodeByObject, self.mfn().getMembers())

    def isCurrent(self):
        return self._mfn.isCurrent()

    def makeCurrent(self, value):
        self._mfn.makeCurrent(value)

    @property
    def blackBox(self):
        """Returns the current black box attribute value

        :return: True if the contents of the container is public
        :rtype: bool
        """
        return self.attribute("blackBox").asBool()

    @blackBox.setter
    def blackBox(self, value):
        mfn = self.mfn()
        if not mfn:
            return
        self.attribute("blackBox").set(value)

    def mfn(self):
        if self._mfn is None and self._node is not None:
            mfn = om2.MFnContainerNode(self.object())
            self._mfn = mfn
            return mfn
        return self._mfn

    def setObject(self, mObject):
        """Set's the MObject For this :class:`DGNode` instance

        :param mObject: The maya api om2.MObject representing a MFnDependencyNode
        :type mObject: om2.MObject
        """
        if not mObject.hasFn(om2.MFn.kDependencyNode):
            raise ValueError("Invalid MObject Type {}".format(om2.MFnDependencyNode(mObject).apiTypeStr))
        self._node = om2.MObjectHandle(mObject)
        self._mfn = om2.MFnContainerNode(mObject)

    def create(self, name):
        """Create's the a MFn Container node and sets this instance MObject to the new node

        :param name: the name for the container
        :type name: str
        :return: Instance to self
        :rtype: :class:`ContainerAsset`
        """
        container = nodes.createDGNode(name, "container")
        self.setObject(container)
        return self

    def addNodes(self, objects):
        containerPath = self.fullPathName(False, True)

        for i in iter(objects):
            if i == self:
                continue
            cmds.container(containerPath, e=True, addNode=i.fullPathName(), includeHierarchyBelow=True)

    def addNode(self, node):
        mObject = node.object()
        if mObject != self._node.object():
            try:
                cmds.container(self.fullPathName(), e=True, addNode=node.fullPathName(),
                               includeHierarchyBelow=True)
            except RuntimeError:
                raise
            return True
        return False

    def publishAttributes(self, attributes):
        containerName = self.fullPathName()
        currentPublishes = self.publishedAttributes()
        for plug in attributes:
            # ignore already publish attributes and plugs which are children/elements
            if plug in currentPublishes or plug.isChild or plug.isElement:
                continue
            name = plug.name()
            try:
                cmds.container(containerName, edit=True, publishAndBind=[name, name.split(".")[-1]])
            except RuntimeError:
                pass

    def publishAttribute(self, plug):
        currentPublishes = self.publishedAttributes()
        if plug in currentPublishes:
            return
        name = plug.name()
        try:
            cmds.container(self.fullPathName(), edit=True, publishAndBind=[name, name.split(".")[-1]])
        except RuntimeError:
            logger.error("Failed to publish and bind attribute: {}".format(name))
            pass

    def publishNode(self, node):
        containerName = self.fullPathName()
        nodeName = node.fullPathName()
        shortName = nodeName.split("|")[-1].split(":")[-1]
        try:
            cmds.containerPublish(containerName, publishNode=[shortName,
                                                              node.mfn().typeName])
        except RuntimeError:
            pass
        try:
            cmds.containerPublish(containerName, bindNode=[shortName, nodeName])
        except RuntimeError:
            pass

    def publishNodes(self, publishNodes):
        containerName = self.fullPathName()
        for i in iter(publishNodes):
            nodeName = i.fullPathName()
            shortName = nodeName.split("|")[-1].split(":")[-1]
            try:
                cmds.containerPublish(containerName, publishNode=[shortName, i.mfn().typeName])

            except RuntimeError:
                pass
            try:
                cmds.containerPublish(containerName, bindNode=[shortName, nodeName])
            except RuntimeError:
                pass

    def publishNodeAsChildParentAnchor(self, node):
        nodeName = node.fullPathName()
        shortName = nodeName.split("|")[-1].split(":")[-1]
        parentName = "_".join([shortName, "parent"])
        childName = "_".join([shortName, "child"])
        containerName = self.fullPathName()
        cmds.container(containerName, e=True, publishAsParent=(nodeName, parentName))
        cmds.container(containerName, e=True, publishAsChild=(nodeName, childName))

    def setParentAncher(self, node):
        nodeName = node.fullPathName()
        shortName = nodeName.split("|")[-1].split(":")[-1]
        parentName = "_".join([shortName, "parent"])
        containerName = self.fullPathName()
        cmds.container(containerName, e=True, publishAsParent=(nodeName, parentName))

    def setChildAnchor(self, node):
        nodeName = node.fullPathName()
        shortName = nodeName.split("|")[-1].split(":")[-1]
        childName = "_".join([shortName, "child"])
        containerName = self.fullPathName()
        cmds.container(containerName, e=True, publishAsChild=(nodeName, childName))

    def childAnchor(self):
        child = cmds.container(self.fullPathName(), q=True, publishAsChild=True)
        if child:
            return nodeByName(child[1])

    def parentAnchor(self):
        parent = cmds.container(self.fullPathName(), q=True, publishAsParent=True)
        if parent:
            return nodeByName(parent[1])

    def unPublishAttributes(self):
        for p in self.publishedAttributes():
            self.unPublishAttribute(p.partialName(useLongNames=False))

    def unPublishAttribute(self, attributeName):
        """
        :param attributeName: attribute name excluding the node name
        :type attributeName: str
        :rtype: bool
        """
        containerName = self.fullPathName()
        try:
            cmds.container(containerName, e=True, unbindAndUnpublish=".".join([containerName, attributeName]))
        except Exception:
            logger.error("Failed to un-publish attribute: {}".format(attributeName), exc_info=True)
        return True

    def unPublishNode(self, node):
        messagePlug = node.attribute("message")
        containerName = self.fullPathName()
        for destPlug in messagePlug.destinations():
            node = destPlug.node().object()
            if node.hasFn(om2.MFn.kContainer):
                parentName = destPlug.parent().partialName(useAlias=True)
                cmds.containerPublish(containerName, unbindNode=parentName)
                cmds.containerPublish(containerName, unpublishNode=parentName)
                break

    def getSubContainers(self):
        return list(map(nodeByObject, self.mfn().getSubcontainers()))

    def publishedNodes(self):
        return [nodeByObject(node[1]) for node in self.mfn().getPublishedNodes(om2.MFnContainerNode.kGeneric) if
                not node[0].isNull()]

    def publishedAttributes(self):
        results = self.mfn().getPublishedPlugs()
        if results:
            return [Plug(self, i) for i in results[0]]
        return []

    def serializeFromScene(self, skipAttributes=(),
                           includeConnections=True,
                           includeAttributes=()):
        members = self.members()
        publishAttributes = self.publishedAttributes()
        publishedNodes = self.publishedNodes()
        if not members:
            return {}
        return {"graph": scene.serializeNodes(members),
                "attributes": publishAttributes,
                "nodes": publishedNodes}

    def delete(self, removeContainer=True):
        containerName = self.fullPathName()
        for i in self.iterAttributes():
            if i.isLocked:
                i.isLocked = False
        self.lock(False)
        cmds.container(containerName, edit=True, removeContainer=removeContainer)


class Plug(object):
    """Plug class which represents a maya MPlug but providing an easier solution to
    access connections and values
    """

    def __init__(self, node, mPlug):
        """

        :param node: The DGNode or DagNode instance for this Plug
        :type node: :class:`DGNode` or :class`DagNode`
        :param mPlug: The Maya plug
        :type mPlug: :class:`om2.MPlug`
        """
        self._mplug = mPlug
        self._node = node

    def __repr__(self):
        """ Returns the name
        """
        return self.name()

    def __eq__(self, other):
        return self._mplug == other.plug()

    def __ne__(self, other):
        return self._mplug != other.plug()

    def __getitem__(self, index):
        """ [0] syntax, The method indexes into the array or compound children by index.

        :param index: Element or child index to get
        :type index: int
        :rtype: :class:`Plug`
        """
        if self._mplug.isArray:
            return self.element(index)
        if self._mplug.isCompound:
            return self.child(index)

        raise TypeError(
            "{} does not support indexing".format(self.name())
        )

    def __getattr__(self, item):

        if hasattr(self._mplug, item):
            return getattr(self._mplug, item)
        return super(Plug, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super(Plug, self).__setattr__(key, value)
            return

        elif hasattr(self._mplug, key):
            return setattr(self._mplug, key, value)

        elif isinstance(value, Plug):
            value.connect(self)

        super(Plug, self).__setattr__(key, value)

    def __abs__(self):
        return abs(self.value())

    def __str__(self):
        return self._mplug.name()

    def __int__(self):
        return self._mplug.asInt()

    def __float__(self):
        return self._mplug.asFloat()

    def __neg__(self):
        return -self.value()

    def __bool__(self):
        return self.exists()

    # support py2
    __nonzero__ = __bool__

    def __rshift__(self, other):
        """ >> syntax, provides the ability to connect to downstream plug.

        :param other: The downstream plug ie. destination.
        :type other: :class:`Plug`
        """
        self.connect(other)

    def __lshift__(self, other):
        """ << syntax, provides the ability to connect to upstream plug.

        :param other: The upstream plug ie. destination.
        :type other: :class:`Plug`
        """
        other.connect(self)

    def __floordiv__(self, other):
        self.disconnect(other)

    def __iter__(self):
        """Loops the array or compound plug.

        :return: Each element within the generator is a plug.
        :rtype: Generator(:class:`Plug`)
        """
        mPlug = self._mplug
        if mPlug.isArray:
            for p in mPlug.getExistingArrayAttributeIndices():
                yield Plug(self._node, mPlug.elementByLogicalIndex(p))
        elif mPlug.isCompound:
            for p in range(mPlug.numChildren()):
                yield Plug(self._node, mPlug.child(p))

    def __len__(self):
        """Length of the compound or array, 0 is returned for non iterables.

        :return: The length of the array of compound.
        :rtype: int
        """
        if self._mplug.isArray:
            return self._mplug.evaluateNumElements()
        elif self._mplug.isCompound:
            return self._mplug.numChildren()
        return 0

    def exists(self):
        return not self._mplug.isNull

    def array(self):
        """Returns the plug array for this array element.

        :return:
        :rtype: :class:`Plug`
        """
        assert self._mplug.isElement, "Plug: {} is not an array element".format(self.name())
        return Plug(self._node, self._mplug.array())

    def parent(self):
        """Returns the parent Plug if this plug is a compound.

        :return: The parent Plug.
        :rtype: :class:`Plug`
        """
        assert self._mplug.isChild, "Plug {} is not a child".format(self.name())
        return Plug(self._node, self._mplug.parent())

    def children(self):
        """Returns all the child plugs of this compound plug.

        :return: A list of child plugs.
        :rtype: iterable(:class:`Plug`)
        """

        return [Plug(self._node, self._mplug.child(i)) for i in range(self._mplug.numChildren())]

    def child(self, index):
        """Returns the child plug by index.

        :param index: The child index
        :type index: int
        :return: The child plug.
        :rtype: :class:`Plug`
        """
        assert self._mplug.isCompound, "Plug: {} is not a compound".format(self.name())
        if index < 0:
            newIndex = max(0, len(self) + index)  # index is negative so it will minus from len
            return Plug(self._node, self._mplug.child(newIndex))
        return Plug(self._node, self._mplug.child(index))

    def element(self, index):
        """Returns the logical element plug if this plug is an array.

        :param index: The element index
        :type index: int
        :return: The Element Plug.
        :rtype: :class:`Plug`
        """
        assert self._mplug.isArray, "Plug: {} is not an array".format(self.name())
        if index < 0:
            newIndex = max(0, len(self) + index)  # index is negative so it will minus from len
            return Plug(self._node, self._mplug.elementByLogicalIndex(newIndex))

        return Plug(self._node, self._mplug.elementByLogicalIndex(index))

    def elementByPhysicalIndex(self, index):
        """Returns the element plug by the physical index if this plug is an array.

        :param index: the physical index.
        :type index: int
        :return: The element Plug.
        :rtype: :class:`Plug`
        """
        assert self._mplug.isArray, "Plug: {} is not an array".format(self.name())
        return Plug(self._node, self._mplug.elementByPhysicalIndex(index))

    def nextAvailableElementPlug(self):
        """Returns the next available output plug for this array.

        Availability is based and connections of element plyg and their children

        :rtype: :class:`Plug`
        """
        assert self._mplug.isArray, "Plug: {} is not an array".format(self.name())
        return Plug(self._node, plugs.nextAvailableElementPlug(self._mplug))

    def nextAvailableDestElementPlug(self):
        """Returns the next available input plug for this array.

        Availability is based and connections of element plyg and their children

        :rtype: :class:`Plug`
        """
        assert self._mplug.isArray, "Plug: {} is not an array".format(self.name())
        return Plug(self._node, plugs.nextAvailableDestElementPlug(self._mplug))

    def plug(self):
        """Returns the maya MPlug object.

        :return: The maya MPlug object
        :rtype: :class:`om2.MPlug`
        """
        return self._mplug

    def node(self):
        """Returns the attached Node class for this plug.

        :return: The DGNode class or DagNode for this Plug.
        :rtype: :class:`DagNode` or :class:`DGNode`
        """
        return self._node

    def apiType(self):
        """Returns the internal zoo attrtype constant

        :rtype: `int`
        """
        return plugs.plugType(self._mplug)

    @lockNodePlugContext
    def connect(self, plug, children=None, force=True, mod=None):
        if self.isCompound:
            children = children or []
            selfLen = len(self)
            childLen = len(children)

            if childLen == 0:
                plugs.connectPlugs(self._mplug, plug.plug(), force=force, mod=mod)
            if childLen > selfLen:
                children = children[:selfLen]
            elif childLen < selfLen:
                children += [False] * (selfLen - childLen)
            return plugs.connectVectorPlugs(self.plug(), plug.plug(), children, force, modifier=mod)
        return plugs.connectPlugs(self._mplug, plug.plug(), force=force, mod=mod)

    @lockNodePlugContext
    def disconnect(self, plug, modifier=None, apply=True):
        """ Disconnect destination plug

        :param plug: Destination
        :type plug: Plug or om2.MPlug
        :return:
        :rtype:
        """
        mod = modifier or om2.MDGModifier()
        mod.disconnect(self._mplug, plug.plug())
        if modifier is None and apply:
            mod.doIt()
        return mod

    @lockNodePlugContext
    def disconnectAll(self, source=True, destination=True, modifier=None):
        return plugs.disconnectPlug(self._mplug, source, destination, modifier)

    def source(self):
        """Returns the source plug from this plug or None if it's not connected

        :rtype: `Plug` or None
        """
        source = self._mplug.source()
        if source.isNull:
            return

        return Plug(nodeByObject(source.node()), source)

    def sourceNode(self):
        """Returns the source node from this plug or None if it's not connected

        :rtype: `DGNode` or None
        """
        source = self.source()
        if not source:
            return
        return source.node()

    def destinationNodes(self):
        dest = self.destinations()

        for d in dest:
            yield d.node()

    def destinations(self):
        """Returns all destination plugs connected to this plug

        :rtype: collections.Iterable[:class:`Plug`]
        """
        for dest in self._mplug.destinations():
            yield Plug(nodeByObject(dest.node()), dest)

    def mfn(self):
        """Returns the maya function set for this plug

        :return: Returns the subclass of of MFnBase for this attribute type ie. MFnTypeAttribute
        :rtype: :class:`om2.MFnBase`
        """
        return plugs.getPlugFn(self._mplug.attribute())(self._mplug.attribute())

    def mfnType(self):
        """Returns the maya MFn attribute type
        """
        return plugs.getPlugFn(self._mplug.attribute())

    def value(self):
        """ Get value of plug, if mObject is returned return the DG/Dag node

        :return: The value of the plug
        """
        value = plugs.getPlugValue(self._mplug)
        isMObject = type(value) == om2.MObject
        if isMObject and nodes.isValidMObject(value):
            return nodeByObject(value)
        elif isMObject and not nodes.isValidMObject(value):
            return None

        return value

    # temp alias
    get = value

    def setFromDict(self, **plugInfo):
        plugs.setPlugInfoFromDict(self._mplug, **plugInfo)

    @lockNodePlugContext
    def set(self, value, mod=None, apply=True):
        """Sets the value of this plug

        :param value: The om2 value type, bool, float,str, MMatrix, MVector etc
        :type value: maya data type.
        :param mod: The zapi.kModifier instance or None.
        :type mod: :class:`zapi.dgModifier` or :class:`zapi.dagModifier`
        :param apply: If True then the plugs value will be set immediately with the Modifier \
        if False it's the client responsibility to call modifier.doIt()
        :type apply: bool
        :raise: :class:`ReferenceObjectError`, in the case where the plug is not dynamic and is referenced.
        """
        if self.node().isReferenced() and self.isLocked:
            raise ReferenceObjectError("Plug: {} is a reference and locked".format(self.name()))
        return plugs.setPlugValue(self._mplug, value, mod=mod, apply=apply)

    def isAnimated(self):
        if not self.exists():
            raise ObjectDoesntExist("Current Plug doesn't exist")
        return om2Anim.MAnimUtil.isAnimated(self._mplug)

    def isFreeToChange(self):
        return self._mplug.isFreeToChange() == self._mplug.kFreeToChange

    @lockNodePlugContext
    def addEnumFields(self, fields):
        """Adds a list of field names to the plug, if a name already exists it will be skipped.
        Adding a field will always be added to the end.

        :param fields: A list of field names to add.
        :type fields: list[str]
        :raise: :class:`ReferenceObjectError`, in the case where the plug is not dynamic and is referenced.
        """
        if self.node().isReferenced() and self.isLocked:
            raise ReferenceObjectError("Plug: {} is a reference and locked".format(self.name()))
        plugType = self.apiType()

        if plugType != attrtypes.kMFnkEnumAttribute:
            raise InvalidTypeForPlug("Required type: 'Enum', current type: {}".format(attrtypes.typeToString(plugType)))
        mayaAttr = self.attribute()
        existingFieldNames = plugs.enumNames(self.plug())
        spaceAttr = om2.MFnEnumAttribute(mayaAttr)
        # add any missing fields to enumAttribute
        for field in fields:
            if field not in existingFieldNames:
                spaceAttr.addField(field, len(existingFieldNames))

    def enumFields(self):
        """Returns a list of the enum fields for this plug. A :class:`InvalidTypeForPlug`
        error will be raised if the plug isn't compatible.

        :raise: :class:`InvalidTypeForPlug` when the plug isn't a enum type.
        """
        plugType = self.apiType()

        if plugType != attrtypes.kMFnkEnumAttribute:
            raise InvalidTypeForPlug("Required type: 'Enum', current type: {}".format(attrtypes.typeToString(plugType)))
        return plugs.enumNames(self.attribute())

    @lockNodePlugContext
    def delete(self, modifier=None):
        """Deletes the plug from the attached Node. If batching is needed then use the modifier
        parameter to pass a base.MDGModifier, once all operations are done call modifier.doIt()

        :param modifier:
        :type modifier: base.dgModifier
        :return: Maya DGModifier
        :rtype: base.dgModifier
        :raise: :class:`ReferenceObjectError`, in the case where the plug is not dynamic and is referenced
        """
        if not self.isDynamic and self.node().isReferenced():
            raise ReferenceObjectError("Plug: {} is reference and locked".format(self.name()))
        if self.isLocked:
            self.lock(False)
        if self._mplug.isElement:
            logicalIndex = self._mplug.logicalIndex()
            mod = plugs.removeElementPlug(self._mplug.array(), logicalIndex,
                                          mod=modifier, apply=True)
        else:
            mod = modifier or om2.MDGModifier()
            mod.removeAttribute(self.node().object(), self.attribute())
            if modifier is None:
                mod.doIt()
        return mod

    @lockNodePlugContext
    def rename(self, name):
        """Renames the current plug.

        :param name: The new name of the plug
        :type name: str
        :return: True if renamed.
        :rtype: bool
        """
        with plugs.setLockedContext(self._mplug):
            mod = om2.MDGModifier()
            mod.renameAttribute(self.node().object(), self.attribute(), name, name)
            mod.doIt()
        return True

    def lockAndHide(self):
        """Locks the plug and  hides the attribute from the channelbox
        """
        self._mplug.locked = True
        self._mplug.channelBox = False

    def serializeFromScene(self):
        if not self.exists():
            return {}
        return plugs.serializePlug(self._mplug)


def createDG(name, nodeType):
    """Creates a maya dg node and returns a :class::`DGNode` instance

    :param name: The name for the node, must be unique
    :type name: str
    :param nodeType: The maya Dg node type
    :type nodeType: str
    :rtype: :class:`DGNode`
    """
    return DGNode().create(name, nodeType)


def createDag(name, nodeType, parent=None):
    """Creates a maya dag node and returns a :class::`DagNode` instance

    :param name: The name for the node, must be unique
    :type name: str
    :param nodeType: The maya Dag node type
    :type nodeType: str
    :rtype: :class:`DagNode`
    """
    return DagNode().create(name, nodeType, parent=parent)


def nodeByObject(node):
    """Given a MObject return the correct Hive base node class

    :param node:
    :type node: om2.MObject
    :return:
    :rtype: DagNode or DGNode
    """
    if node.hasFn(om2.MFn.kDagNode):
        return DagNode(node)
    return DGNode(node)


def nodeByName(nodeName):
    """Returns a dag node instance given the maya node name, expecting fullPathName.

    :param nodeName: The maya node name
    :type nodeName: str
    :rtype: :class:`DGNode` or :class:`DagNode`
    """
    mObj = nodes.asMObject(nodeName)
    if mObj.hasFn(om2.MFn.kDagNode):
        return DagNode(mObj)
    return DGNode(mObj)


def nodesByNames(nodeNameList):
    """ nodeByName except uses a list

    :param nodeNameList: List of maya node names
    :type nodeNameList: list[str]
    :return: a list of maya node paths to convert to zapi nodes
    :rtype: collections.Iterable[DagNode]
    """
    for n in nodeNameList:
        yield nodeByName(n)


def plugByName(path):
    """Returns the :class:`Plug` instance for the provide path to the plug

    :param path: The fullPath to the plug.
    :type path: str
    :raise: :class:`InvalidPlugPath`
    :return: The Plug instance matching the plug path.
    :rtype: :class:`Plug`
    """
    if "." not in path:
        raise InvalidPlugPath(path)
    plug = plugs.asMPlug(path)
    return Plug(plug.node(), plug)


def fullNames(dagNodes):
    """ Helper function to get full names of dagNodes

    :param dagNodes: DagNodes
    :type dagNodes: list[:class:`DagNode`] or Iterable[:class:`DagNode`]
    :return: a list of fullPaths
    :rtype: list[str]
    """
    return [d.fullPathName() for d in dagNodes if d.exists()]


def shortNames(dagNodes):
    """ Helper function to get the short names of DGNode

    :param dagNodes: An iterable of DGNodes/DagNodes.
    :type dagNodes: list[:class:`DGNode`] or collections.Iterable[:class:`DGNode`]
    :return: A list of short names for the provided nodes.
    :rtype: list[str]
    """
    return [d.name() for d in dagNodes if d.exists()]


def alphabetizeDagList(dagList):
    """Sorts a dag API object list by lowercase short names

    :param dagList: A list of API dag objects
    :type dagList: list[DagNode]
    :return: A list of API dag objects now sorted alphabetically
    :type dagList: list[DagNode]
    """
    if not dagList:
        return dagList
    names = shortNames(dagList)
    names = [x.lower() for x in names]  # lowercase for sorting later
    zippedList = sorted(zip(names, dagList))
    return [x for y, x in zippedList]  # now alphabetical


def selected(filterTypes=()):
    """ Get dag nodes from selected objects in maya

    :param filterTypes: a tuple of om2.MFn types to filter selected Nodes
    :type filterTypes: tuple(om2.MFn.kConstant)
    :return: A list of DGNode nodes
    :rtype: iterable[DGNode]
    """
    return map(nodeByObject, scene.getSelectedNodes(filterTypes))


def select(objects, mod=None, apply=True):
    """ Selects all nodes in `objects`, this uses cmds.select.

    :param objects: DG Nodes to select
    :type objects: iterable[:class:`DGNode`]
    :param mod: The Dag/DG modifier to run the command in
    :type mod: :class:`maya.api.OpenMaya.MDagModifier` or :class:`maya.api.OpenMaya.MDGModifier`
    :rtype mod: :class:`maya.api.OpenMaya.MDGModifier`
    """
    if not mod:
        mod = om2.MDGModifier()

    mod.pythonCommandToExecute("cmds.select({})".format([i.fullPathName() for i in objects]))
    if apply:
        mod.doIt()

    return mod


def selectByNames(names, mod=None, apply=True):
    """ Same as select(), except it uses the names instead

    :param names: Names of the nodes
    :type names: iterable[:class:`str`]
    :param apply: Apply the MDagModifier immediately
    :param mod: The Dag/DG modifier
    :type mod: :class:`maya.api.OpenMaya.MDagModifier` or :class:`maya.api.OpenMaya.MDGModifier`
    :rtype mod: :class:`maya.api.OpenMaya.MDGModifier`
    """
    if not mod:
        mod = om2.MDGModifier()

    mod.pythonCommandToExecute("cmds.select({})".format(names))
    if apply:
        mod.doIt()

    return mod
