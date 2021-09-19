"""Temporary module while doing the replacement on constraints.py.

.. todo::
    Function to remove a space.


"""
__all__ = ("buildConstraint",
           "CONSTRAINT_TYPES",
           "CONSTRAINT_ATTR_NAME",
           "hasConstraint",
           "iterConstraints",
           "findConstraint")

import json

from maya.api import OpenMaya as om2
from maya import cmds
from zoo.libs.maya.utils import mayaenv
from zoo.libs.maya.api import nodes, attrtypes
from zoo.libs.maya.zapi import base, nodecreation

# constant mapping between maya api constraint types and maya cmds string types
CONSTRAINT_TYPES = ("parent",
                    "point",
                    "orient",
                    "scale",
                    "aim",
                    "matrix")

CONSTRAINT_ATTR_NAME = "zooConstraint"

# zoo constraint compound indices
ZOOCONSTRAINT_TYPE_IDX = 0
ZOOCONSTRAINT_KWARGS_IDX = 1
ZOOCONSTRAINT_CONTROLLER_IDX = 2
ZOOCONSTRAINT_CONTROLATTRNAME_IDX = 3
ZOOCONSTRAINT_TARGETS_IDX = 4
ZOOCONSTRAINT_SPACELABEL_IDX = 0
ZOOCONSTRAINT_SPACETARGET_IDX = 1
ZOOCONSTRAINT_NODES_IDX = 5


def buildConstraint(driven, drivers,
                    constraintType="parent", **kwargs):
    """This function builds a space switching constraint.

    Currently Supporting types of
        kParentConstraint
        kPointConstraint
        kOrientConstraint

    :param driven: The transform to drive
    :param driven: :class:`zapi.DagNode`
    :param drivers: A dict containing the target information(see below example)
    :param drivers: dict or None
    :param constraintType: The constraint type :see above: `CONSTRAINT_TYPES`
    :type constraintType: str
    :param kwargs: The constraint extra arguments to use ie. maintainOffset etc
    :type kwargs: dict

    .. code-block: python

        targets = []
        for n in ("locator1", "locator2", "locator3"):
            targets.append((n, nodes.createDagNode(n, "locator")))
        spaceNode =nodes.createDagNode("control", "locator")
        drivenNode = nodes.createDagNode("driven", "locator")
        spaces = {"spaceNode": spaceNode,
                    "attributeName": "parentSpace", "targets": targets}
        constraint, conditions = build(drivenNode, targets=spaces)

        # lets add to the existing system
        spaces = {"spaceNode": spaceNode, "attributeName": "parentSpace", "targets": (
                 ("locator8", nodes.createDagNode("locator8", "locator")),)}

        constraint, conditions = buildConstraint(drivenNode, drivers=spaces)

      )


    """
    # make sure we support the constrainttype the user wants
    assert constraintType in CONSTRAINT_TYPES, "No Constraint of type: {}, supported".format(constraintType)
    constraintAttr = None
    for lastConstraintPlug in iterConstraints(driven):
        constraintAttr = lastConstraintPlug.plugElement
    if constraintAttr is None:
        constraintAttr = addConstraintAttribute(driven)[0]
    else:
        latestConstraintIndex = constraintAttr.logicalIndex()
        constraintAttr = driven.attribute(CONSTRAINT_ATTR_NAME)[latestConstraintIndex + 1]

    constraint = createConstraintFactory(constraintType,
                                         driven,
                                         constraintAttr)
    constraint.build(drivers, **kwargs)
    return constraint


class Constraint(object):
    id = ""

    def __init__(self, driven=None, plugElement=None):
        if driven and not plugElement or (plugElement and not driven):
            raise ValueError("if driven or plugElement is specified then both need to be specified")

        self._driven = driven
        self.plugElement = plugElement

    def build(self, drivers, **constraintKwargs):
        raise NotImplementedError("Build method must be implemented in subclasses")

    def delete(self):

        for targetPlug in self.plugElement.child(ZOOCONSTRAINT_NODES_IDX):
            sourcePlug = targetPlug.source()
            if not sourcePlug:
                continue
            utilNode = sourcePlug.node()
            # disconnect connections from utilties
            for sourcePlug, destPlug in utilNode.iterConnections(True, False):
                sourcePlug.disconnect(destPlug)
            # delete utilities
            utilNode.delete()
        # remove multi instance element plug
        self.plugElement.delete()
        return True

    def driven(self):
        return self._driven

    def setDriven(self, node, plugElement):
        self._driven = node
        self.plugElement = plugElement

    def utilityNodes(self):
        for targetPlug in self.plugElement.child(ZOOCONSTRAINT_NODES_IDX):
            sourcePlug = targetPlug.source()
            if not sourcePlug:
                continue
            utilNode = sourcePlug.node()
            if utilNode is None:
                continue
            yield utilNode

    def drivers(self):
        for targetElement in self.plugElement.child(ZOOCONSTRAINT_TARGETS_IDX):
            sourceNode = targetElement.child(ZOOCONSTRAINT_SPACETARGET_IDX).sourceNode()
            if sourceNode:
                yield targetElement.child(ZOOCONSTRAINT_SPACELABEL_IDX).value(), sourceNode

    def controller(self):
        sourcePlug = self.plugElement.child(ZOOCONSTRAINT_CONTROLLER_IDX).source()
        if sourcePlug is None:
            return {"node": None, "attr": None}
        controller = sourcePlug.node()
        return {
            "node": controller,
            "attr": sourcePlug.node().attribute(self.plugElement.child(ZOOCONSTRAINT_CONTROLATTRNAME_IDX).value())
        }

    def serialize(self):
        sources = self.plugElement[ZOOCONSTRAINT_TARGETS_IDX]
        kwargsStr = self.plugElement[ZOOCONSTRAINT_KWARGS_IDX].value()
        try:
            kwargs = json.loads(kwargsStr)
        except ValueError:
            kwargs = {}
        targets = []
        for source in sources:
            label = source.child(ZOOCONSTRAINT_SPACELABEL_IDX).value()
            target = source.child(ZOOCONSTRAINT_SPACETARGET_IDX).sourceNode()
            if not target:
                continue
            targets.append((label, target))
        if not targets:
            return {}
        controllerSource = self.plugElement.child(ZOOCONSTRAINT_CONTROLLER_IDX).source()
        controllerNode = None
        if controllerSource is not None:
            controllerNode = controllerSource.node()
        mapping = {"targets": targets,
                   "kwargs": kwargs,
                   "controller": (controllerNode,
                                  self.plugElement.child(ZOOCONSTRAINT_CONTROLATTRNAME_IDX).value()),
                   "type": self.id}
        return mapping


class ParentConstraint(Constraint):
    id = "parent"
    constraintTargetIndex = 1
    _constraintFunc = "parentConstraint"

    def build(self, drivers, **constraintKwargs):

        spaceNode = drivers.get("spaceNode")
        attrName = drivers.get("attributeName", "parent")
        targetInfo = drivers["targets"]
        targetLabels, targetNodes = zip(*targetInfo)
        driverLabels = [driverLabel for driverLabel, _ in self.drivers()]
        resultingTargets = []
        for targetLabel, targetNode in targetInfo:
            if targetLabel in driverLabels:
                continue
            resultingTargets.append((targetLabel, targetNode))
        if not resultingTargets:
            return False
        driven = self.driven()
        # create the constraint
        cmdsFunc = getattr(cmds, self._constraintFunc)
        constraintKwargs = {str(k): v for k, v in constraintKwargs.items()}
        constraint = cmdsFunc([target.fullPathName() for _, target in resultingTargets],
                              driven.fullPathName(),
                              **constraintKwargs)[0]
        constraint = base.nodeByName(constraint)
        # in this case no space switching is needed to we exit early
        if not spaceNode:
            addConstraintMap(resultingTargets, driven,
                             None, "",
                             [constraint], self.id, kwargsMap=constraintKwargs)
            return True

        # if we have been provided a spaceNode, which will contain our switch, otherwise ignore the setup of a switch
        # and just return the constraint
        if spaceNode.hasAttribute(attrName):
            spaceAttr = spaceNode.attribute(attrName)
            spaceAttr.addEnumFields(targetLabels)
        else:
            spaceAttr = spaceNode.addAttribute(attrName, Type=base.attrtypes.kMFnkEnumAttribute,
                                               keyable=True,
                                               channelBox=True, locked=False,
                                               enums=targetLabels
                                               )

        targetArray = constraint.target
        sourceShortName = constraint.fullPathName(partialName=True, includeNamespace=False)
        conditions = []
        constraintTargetWeightIndex = self.constraintTargetIndex
        # # first iterate over the target array on the constraint
        for targetElement in targetArray:
            targetElementWeight = targetElement.child(constraintTargetWeightIndex)
            targetWeightSource = targetElementWeight.source()
            # just in case the target weight plug is disconnected
            if targetWeightSource is None:
                targetWeightSource = targetElementWeight
            else:
                # lets make sure that we're not already connected to a condition node
                # if so skip
                weightSourceNode = targetWeightSource.node()
                # if we connected to the constraint i.e spaceWO1
                if weightSourceNode == constraint:
                    upstreamWeight = targetWeightSource.source()
                    if upstreamWeight and upstreamWeight.node().apiType() == om2.MFn.kCondition:
                        continue
                else:
                    if weightSourceNode.apiType() == om2.MFn.kCondition:
                        continue

            targetNode = targetElement.child(0).source().node()
            targetShortName = targetNode.fullPathName(partialName=True, includeNamespace=False)
            # create the condition node and do the connections
            condition = nodecreation.conditionVector(firstTerm=spaceAttr,
                                                     secondTerm=float(targetElement.logicalIndex()),
                                                     colorIfTrue=(1.0, 0.0, 0.0),
                                                     colorIfFalse=(0.0, 0.0, 0.0), operation=0,
                                                     name="_".join([targetShortName, sourceShortName, "space"]))
            condition.outColorR.connect(targetWeightSource)
            conditions.append(condition)
        addConstraintMap(resultingTargets, driven,
                         spaceNode, attrName,
                         conditions + [constraint], self.id, kwargsMap=constraintKwargs)


class PointConstraint(ParentConstraint):
    id = "point"
    constraintTargetIndex = 4
    _constraintFunc = "pointConstraint"


class OrientConstraint(ParentConstraint):
    id = "orient"
    constraintTargetIndex = 4
    _constraintFunc = "orientConstraint"


class ScaleConstraint(ParentConstraint):
    id = "scale"
    constraintTargetIndex = 2
    _constraintFunc = "scaleConstraint"


class AimConstraint(ParentConstraint):
    id = "aim"
    constraintTargetIndex = 4
    _constraintFunc = "aimConstraint"


class MatrixConstraint(Constraint):
    id = "matrix"
    if mayaenv.mayaVersion() >= 2020:
        # todo matrix space switching
        def build(self, drivers, **constraintKwargs):
            maintainOffset = constraintKwargs.get("maintainOffset", False)
            skipScale = constraintKwargs.get("skipScale", [False, False, False])
            skipRotate = constraintKwargs.get("skipRotate", [False, False, False])
            skipTranslate = constraintKwargs.get("skipTranslate", [False, False, False])
            driven = self.driven()
            name = driven.fullPathName(partialName=True, includeNamespace=False)
            targetInfo = drivers["targets"]
            targetLabels, targetNodes = zip(*targetInfo)
            driver = targetNodes[0]  # temp
            composename = "_".join([name, "pickMtx"])
            skipScale = any(i for i in skipScale)
            skipTranslate = any(i for i in skipTranslate)
            skipRotate = any(i for i in skipRotate)
            utilties = []
            currentWorldMatrix = driven.worldMatrix()
            if any((skipScale, skipTranslate, skipRotate)):
                mat = base.createDG(composename, "pickMatrix")
                driver.attribute("worldMatrix")[0].connect(mat.inputMatrix)

                mat.useRotate = not skipRotate
                mat.useScale = not skipScale
                mat.useTranslate = not skipTranslate
                mat.outputMatrix.connect(driven.offsetParentMatrix)
                utilties.append(mat)
            else:
                driver.attribute("worldMatrix")[0].connect(driven.offsetParentMatrix)

            if maintainOffset:
                driven.setMatrix(currentWorldMatrix * driven.offsetParentMatrix.value().inverse())
            else:
                driven.resetTransform(translate=True, rotate=True, scale=True)
            addConstraintMap(targetInfo, driven,
                             None, "",
                             utilties, self.id, kwargsMap=constraintKwargs)
            return True
    else:
        def build(self, drivers, **constraintKwargs):
            maintainOffset = constraintKwargs.get("maintainOffset", False)
            skipScale = constraintKwargs.get("skipScale")
            skipRotate = constraintKwargs.get("skipRotate")
            skipTranslate = constraintKwargs.get("skipTranslate")
            driven = self.driven()
            name = driven.fullPathName(partialName=True, includeNamespace=False)
            targetInfo = drivers["targets"]
            targetLabels, targetNodes = zip(*targetInfo)
            driver = targetNodes[0]  # temp
            composename = "_".join([name, "wMtxCompose"])

            utilties = []
            if maintainOffset:
                offset = nodes.getOffsetMatrix(driver.object(), driven.object())
                offsetname = "_".join([name, "wMtxOffset"])
                multMatrix = nodecreation.createMultMatrix(offsetname,
                                                           inputs=(offset, driver.attribute("worldMatrix")[0],
                                                                   driven.parentInverseMatrix()),
                                                           output=None)
                multMatrix = base.nodeByObject(multMatrix)
                outputPlug = multMatrix.matrixSum
                utilties.append(multMatrix)
            else:
                outputPlug = driver.attribute("worldMatrix")[0]

            decompose = nodecreation.createDecompose(composename, destination=driven,
                                                     translateValues=skipTranslate or (),
                                                     scaleValues=skipScale or (), rotationValues=skipRotate or ())
            utilties.append(decompose)
            driver.rotateOrder.connect(decompose.inputRotateOrder)
            outputPlug.connect(decompose.inputMatrix)
            addConstraintMap(targetInfo, driven,
                             None, "",
                             utilties, self.id, kwargsMap=constraintKwargs)
            return True


class BlendMatrixConstraint(Constraint):
    id = "blendMatrix"

    def build(self, drivers, **constraintKwargs):
        pass


# temp
def createConstraintFactory(constraintType, drivenNode, constraintMetaPlug):
    constObj = CONSTRAINT_PLUGINS.get(constraintType)
    if constObj is None:
        raise NotImplementedError("Constraint Type : {} not supported".format(constraintType))
    instance = constObj()
    instance.setDriven(drivenNode, constraintMetaPlug)
    return instance


def findConstraint(node, constraintType):
    """Searches the upstream graph one level  in search for the corresponding kConstraintType

    :param node: The node to search upstream from
    :type node: :class:`base.DagNode`
    :param constraintType:
    :type constraintType: str
    :return: Constraint class instance.
    :rtype: :class:`Constraint`
    """
    for plugElement in node.zooConstraint:
        typeValue = plugElement.child(0).value()
        if typeValue != constraintType:
            continue
        return createConstraintFactory(constraintType, node, plugElement)


def hasConstraint(node):
    """Determines if this node is constrained by another, this is done by checking the constraints compound attribute

    :param node: the node to search for attached constraints
    :type node: :class:`base.DagNode`
    :rtype: bool
    """
    # exit early when iterConstraints returns something
    for i in iterConstraints(node):
        return True
    return False


def iterConstraints(node):
    """Generator function that loops over the attached constraints, this is done
    by iterating over the compound array attribute `constraints`.

    :param node: The node to iterate, this node should already have the compound attribute
    :type node: :class:`base.DagNode`
    :return: First element is a list a driven transforms, the second is a list of \
    utility nodes used to create the constraint.
    :rtype: generator(:class:`Constraint`)
    """
    array = node.attribute(CONSTRAINT_ATTR_NAME)  # type: base.Plug or None
    if array is None:
        return
    for plugElement in array:
        typeValue = plugElement.child(0).value()
        if not typeValue:
            continue
        yield createConstraintFactory(typeValue, node, plugElement)


def addConstraintAttribute(node):
    """ Creates and returns the 'constraints' compound attribute, which is used to store all incoming constraints
    no matter how they are created. If the attribute exists then that will be returned.

    :param node: The node to have the constraint compound attribute.
    :type node: :class:`base.DagNode`
    :return: Return's the constraint compound attribute.
    :rtype: :class:`om2.MPlug` or :class:`base.Plug`

    Resulting Attribute structure
    zooConstraint[]
                |- zooConstraintType  # str, constraintType ie. parent, matrix, scale, point etc
                |- zooConstraintKwargs # jsonstring , kwargs passed directly to the constraint class
                |- zooConstraintController # message attribute linked to the constraint switch controller
                |- zooConstraintControlAttrName # constraint controller attribute name , used for lookups
                |- zooConstraintTargets[]
                                |-constraintSpaceLabel # target label for the controller attribute enum
                                |-constraintSpaceTarget # message attribute linked to the target node ie. transform
                |- zooConstraintNodes[] # utility nodes, ie. parentConstraint node
    """

    if node.hasAttribute(CONSTRAINT_ATTR_NAME):
        return node.zooConstraint
    constraintPlug = node.addCompoundAttribute(name=CONSTRAINT_ATTR_NAME,
                                               Type=attrtypes.kMFnCompoundAttribute,
                                               isArray=True,
                                               attrMap=[{"name": "zooConstraintType", "Type": attrtypes.kMFnDataString},
                                                        {"name": "zooConstraintKwargs",
                                                         "Type": attrtypes.kMFnDataString,
                                                         "isArray": False},
                                                        {"name": "zooConstraintController",
                                                         "Type": attrtypes.kMFnMessageAttribute,
                                                         "isArray": False},
                                                        {"name": "zooConstraintControlAttrName",
                                                         "Type": attrtypes.kMFnDataString,
                                                         "isArray": False},
                                                        {"name": "zooConstraintTargets",
                                                         "Type": attrtypes.kMFnCompoundAttribute,
                                                         "isArray": True,
                                                         "children": [{"name": "zooConstraintSpaceLabel",
                                                                       "Type": attrtypes.kMFnDataString},
                                                                      {"name": "zooConstraintSpaceTarget",
                                                                       "Type": attrtypes.kMFnMessageAttribute}]},
                                                        {"name": "zooConstraintNodes",
                                                         "Type": attrtypes.kMFnMessageAttribute,
                                                         "isArray": True}

                                                        ])
    return constraintPlug


def addConstraintMap(drivers, driven,
                     controller,
                     controllerAttrName,
                     utilities, constraintType, kwargsMap=None):
    """Adds a mapping of drivers and utilities to the constraint compound array attribute

    """
    kwargsMap = kwargsMap or {}
    compoundPlug = addConstraintAttribute(driven)
    availPlug = None
    # find the next array element not used
    for element in compoundPlug:
        elementConstraintType = element.child(ZOOCONSTRAINT_TYPE_IDX).value()
        if elementConstraintType == constraintType or not elementConstraintType:
            availPlug = element
            break
        continue
    if availPlug is None:
        availPlug = compoundPlug[0]
    constraintTypePlug = availPlug.child(ZOOCONSTRAINT_TYPE_IDX)
    kwargsPlug = availPlug.child(ZOOCONSTRAINT_KWARGS_IDX)
    # connect to controller and name if it's specified
    if controller is not None:
        controllerPlug = availPlug.child(ZOOCONSTRAINT_CONTROLLER_IDX)
        controllerNamePlug = availPlug.child(ZOOCONSTRAINT_CONTROLATTRNAME_IDX)
        controller.message.connect(controllerPlug)
        controllerNamePlug.set(controllerAttrName)

    targetsPlug = availPlug.child(ZOOCONSTRAINT_TARGETS_IDX)
    constraintsPlug = availPlug.child(ZOOCONSTRAINT_NODES_IDX)
    constraintTypePlug.set(constraintType)
    kwargsPlug.set(json.dumps(kwargsMap))
    # connect the drivers and set the driver labels
    for driverLabel, driver in drivers:
        driverElement = targetsPlug.nextAvailableDestElementPlug()
        driverElement.child(ZOOCONSTRAINT_SPACELABEL_IDX).set(driverLabel)
        driver.message.connect(driverElement.child(ZOOCONSTRAINT_SPACETARGET_IDX))
    # connect to labels
    for constraintNode in utilities:
        constraintNode.message.connect(constraintsPlug.nextAvailableDestElementPlug())

    return compoundPlug


def serializeConstraints(node):
    """Serializes all attached zoo constraints to the provided node.

    :param node:
    :type node: :class:`base.DagNode`
    :return: A list of constraint dictionaries
    :rtype: list[dict]
    """
    constraints = []
    if not node.hasAttribute(CONSTRAINT_ATTR_NAME):
        return constraints
    for constraint in iterConstraints(node):
        constraintInfo = constraint.serialize()
        if not constraintInfo:
            continue
        constraints.append(constraintInfo)
    return constraints


CONSTRAINT_PLUGINS = {"parent": ParentConstraint,
                      "point": PointConstraint,
                      "scale": ScaleConstraint,
                      "orient": OrientConstraint,
                      "aim": AimConstraint,
                      "matrix": MatrixConstraint
                      }
