__all__ = (
    "distanceBetween",
    "multiplyDivide",
    "blendColors",
    "floatMath",
    "blendTwoAttr",
    "pairBlend",
    "conditionVector",
    "logicFloat",
    "conditionFloat",
    "createAnnotation",
    "createMultMatrix",
    "createDecompose",
    "createReverse",
    "createSetRange",
    "createPlusMinusAverage1D",
    "createPlusMinusAverage2D",
    "createPlusMinusAverage3D",
    "createControllerTag",
    "createIkHandle",
    "createDisplayLayer"
)

from maya import cmds
from maya.api import OpenMaya as om2

from zoo.libs.maya.utils import general, mayaenv
from zoo.libs.maya.zapi import base


def distanceBetween(firstNode, secondNode, name):
    """Creates a distance between node and connects the 'firstNode' and 'secondNode' world space
    matrices.

    :param firstNode: The start transform node
    :type firstNode: MObject
    :param secondNode: The second transform node
    :type secondNode: MObject
    :return:  the Three nodes created by the function in the form of a tuple, the first element \
    is the distance between node, the second is the start node decompose matrix, the third element \
    is the second node decompose matrix.
    :rtype: tuple(om2.MObject, om2.MObject, om2.MObject)  
    """
    distanceBetweenNode = base.createDG(name, "distanceBetween")
    firstNode.attribute("worldMatrix")[0].connect(distanceBetweenNode.inMatrix1)
    secondNode.attribute("worldMatrix")[0].connect(distanceBetweenNode.inMatrix2)
    return distanceBetweenNode


def multiplyDivide(input1, input2, operation, name):
    """Creates a multiply divide node with the given and setups the input connections.

    List of operations::

        no operation = 0,
        multipy = 1,
        divide = 2,
        power = 3

    :param input1:the node attribute to connect to the input1 value or use int for value
    :type input1: MPlug or MVector
    :param input2:the node attribute to connect to the input2 value or use int for value
    :type input2: MPlug or MVector
    :param operation: the int value for operation
    :type operation: int
    :return, the multiplyDivide node MObject
    :rtype: MObject
    """
    mult = base.createDG(name, "multiplyDivide")
    # assume connection type
    if isinstance(input1, base.Plug):
        input1.connect(mult.input1)
    # plug set
    else:
        mult.input1.set(input1)
    if isinstance(input2, base.Plug):
        input2.connect(mult.input2)
    else:
        mult.input2.set(input1)
    mult.operation.set(operation)

    return mult.object()


def blendColors(color1, color2, name, blender):
    """Creates a blend colors node.

    :param color1: If the type is a MPlug then the color1 plug on the new node\
    will be connected the given plug.
    :type color1: om2.MColor or om2.MPlug
    :param color2: If the type is a MPlug then the color2 plug on the new node\
    will be connected the given plug.
    :type color2: om2.MColor or om2.MPlug
    :param name: The new floatMath node name.
    :type name: str
    :param blender: If the type is a MPlug then the blender plug on the new node\
    will be connected the given plug.
    :type blender: float or om2.MPlug
    :return: The new colorBlend node as a MObject
    :rtype: om2.MObject
    """
    blendFn = base.createDG(name, "blendColors")
    if isinstance(color1, base.Plug):
        color1.connect(blendFn.color1)
    else:
        blendFn.color1.set(color1)
    if isinstance(color2, base.Plug):
        color2.connect(blendFn.color2)
    else:
        blendFn.color2.set(color2)
    if isinstance(blender, base.Plug):
        blender.connect(blendFn.blender)
    else:
        blendFn.blender.set(blender)
    return blendFn.object()


def floatMath(floatA, floatB, operation, name):
    """Creates a floatMath node from the lookdev kit builtin plugin

    :param floatA: If the type is a MPlug then the floatA plug on the new node\
    will be connected the given plug.
    :type floatA: float or om2.MPlug
    :param floatB: If the type is a MPlug then the floatB plug on the new node\
    will be connected the given plug.
    :type floatB: float or om2.MPlug
    :param operation: The operation attributes value
    :type operation: int
    :param name: The new floatMath node name.
    :type name: str
    :return: The floatMath node MObject
    :rtype: om2.MObject
    """
    floatMathFn = base.createDG(name, "floatMath")
    if isinstance(floatA, base.Plug):
        floatA.connect(floatMathFn.floatA)
    else:
        floatMathFn.floatA.set(floatA)

    if isinstance(floatB, base.Plug):
        floatB.cocnnect(floatMathFn.floatB)
    else:
        floatMathFn.floatB.set(floatB)
    floatMathFn.operation.set(operation)
    return floatMathFn


def blendTwoAttr(input1, input2, blender, name):
    fn = base.createDG(name, "blendTwoAttr")
    inputArray = fn.input
    input1.connect(inputArray.element(0))
    input2.connect(inputArray.element(1))
    blender.connect(fn.attributesBlender)
    return fn


def pairBlend(name, inRotateA=None, inRotateB=None, inTranslateA=None, inTranslateB=None, weight=None,
              rotInterpolation=None):
    blendPairNode = base.createDG(name, "pairBlend")
    if inRotateA is not None:
        inRotateA.connect(blendPairNode.inRotate1)
    if inRotateB is not None:
        inRotateB.connect(blendPairNode.inRotate2)
    if inTranslateA is not None:
        inTranslateA.connect(blendPairNode.inTranslate1)
    if inTranslateB is not None:
        inTranslateB.connect(blendPairNode.inTranslate2)
    if weight is not None:
        if isinstance(weight, base.Plug):
            weight.connect(blendPairNode.weight)
        else:
            blendPairNode.weight.set(weight)
    if rotInterpolation is not None:
        if isinstance(rotInterpolation, base.Plug):
            rotInterpolation.connect(blendPairNode.rotInterpolation)
        else:
            blendPairNode.rotInterpolation.set(rotInterpolation)
    return blendPairNode


def conditionFloat(floatA, floatB, condition, outFloat, name):
    """Creates a floatCondition node and sets connections/values.

    :param floatA:
    :type floatA: :class:`base.Plug` or float
    :param floatB:
    :type floatB: :class:`base.Plug` or float
    :param condition:
    :type condition: :class:`base.Plug` or bool
    :param outFloat:
    :type outFloat: :class:`base.Plug` or None
    :param name: The name for the node
    :type name: str
    :return:
    :rtype: :class:`base.DGNode`
    """
    condNode = base.createDG(name, "floatCondition")

    if isinstance(floatA, float):
        condNode.floatA.set(floatA)
    else:
        floatA.connect(condNode.floatA)

    if isinstance(floatB, float):
        condNode.floatB.set(floatB)
    else:
        floatB.connect(condNode.floatB)
    if isinstance(condition, bool):
        condNode.condition.set(condition)
    else:
        condition.connect(condNode.condition)
    if outFloat is not None:
        condNode.outFloat(outFloat)
    return condNode


def logicFloat(floatA, floatB, operation, outBool, name):
    """Creates a floatLogic node and sets connections/values.

    :param floatA:
    :type floatA: :class:`base.Plug` or float
    :param floatB:
    :type floatB: :class:`base.Plug` or float
    :param operation:
    :type operation: :class:`base.Plug` or int
    :param outBool:
    :type outBool: :class:`base.Plug` or None
    :param name: The name for the node
    :type name: str
    :return:
    :rtype: :class:`base.DGNode`
    """
    condNode = base.createDG(name, "floatLogic")
    if isinstance(operation, base.Plug):
        operation.connect(condNode.operation)
    else:
        condNode.operation.set(operation)
    if isinstance(floatA, float):
        condNode.floatA.set(floatA)
    else:
        floatA.connect(condNode.floatA)

    if isinstance(floatB, float):
        condNode.floatB.set(floatB)
    else:
        floatB.connect(condNode.floatB)
    if outBool is not None:
        condNode.outFloat(outBool)
    return condNode


def conditionVector(firstTerm, secondTerm, colorIfTrue, colorIfFalse, operation, name):
    """
    :param firstTerm: 
    :type firstTerm: om2.MPlug or float
    :param secondTerm: 
    :type secondTerm: om2.MPlug or float 
    :param colorIfTrue: seq of MPlugs or a single MPlug(compound) 
    :type colorIfTrue: om2.MPlug or list(om2.Plug) or om2.MVector
    :param colorIfFalse: seq of MPlugs or a single MPlug(compound)
    :type colorIfFalse: om2.MPlug or list(om2.Plug) or om2.MVector 
    :param operation: the comparsion operator
    :type operation: int
    :param name: the new name for the node
    :type name: str
    :return: 
    :rtype: om2.MObject
    """
    condNode = base.createDG(name, "condition")
    if isinstance(operation, base.Plug):
        operation.connect(condNode.operation)
    else:
        condNode.operation.set(operation)

    if isinstance(firstTerm, float):
        condNode.firstTerm.set(firstTerm)
    else:
        firstTerm.connect(condNode.firstTerm)

    if isinstance(secondTerm, float):
        condNode.secondTerm.set(secondTerm)
    else:
        secondTerm.connect(condNode.secondTerm)
    if isinstance(colorIfTrue, base.Plug):
        colorIfTrue.connect(condNode.colorIfTrue)
    elif isinstance(colorIfTrue, base.Vector):
        condNode.colorIfTrue.set(colorIfTrue)
    else:
        color = condNode.colorIfTrue
        # expecting seq of plugs
        for i, p in enumerate(colorIfTrue):
            if p is None:
                continue
            child = color.child(i)
            if isinstance(p, base.Plug):
                p.connect(child)
                continue
            child.set(p)
    if isinstance(colorIfFalse, base.Plug):
        colorIfFalse.connect(condNode.colorIfFalse)
    elif isinstance(colorIfFalse, base.Vector):
        condNode.colorIfFalse.set(colorIfFalse)
    else:
        color = condNode.colorIfFalse
        # expecting seq of plugs
        for i, p in enumerate(colorIfFalse):
            if p is None:
                continue
            child = color.child(i)
            if isinstance(p, base.Plug):
                p.connect(child)
                continue
            child.set(p)
    return condNode


if mayaenv.mayaVersion() < 2020:
    def createAnnotation(rootObj, endObj, text=None, name=None, parent=None):
        newparent = parent or base.createDag("_".join([name, "ann_hrc"]), "transform")
        name = name or "annotation"
        locator = base.createDag("_".join([name, "loc"]), "locator", newparent)

        annotationNode = base.nodeByName(cmds.annotate(locator.fullPathName(), tx=text))
        annParent = annotationNode.parent()
        annParent.rename(name)
        annParent.setParent(newparent, maintainOffset=False)
        extras = [newparent]

        decompose = createDecompose("_".join([endObj.name(includeNamespace=False),
                                              locator.name(includeNamespace=False),
                                              "decompose"]),
                                    destination=locator,
                                    inputMatrixPlug=endObj.attribute("worldMatrix")[0]
                                    )
        extras.append(decompose)
        decompose = createDecompose("_".join([rootObj.name(includeNamespace=False),
                                              annParent.name(includeNamespace=False),
                                              "decompose"]),
                                    destination=annParent,
                                    inputMatrixPlug=rootObj.attribute("worldMatrix")[0]
                                    )

        extras.append(decompose)
        cmds.select(cl=True) # todo : delete, should handle cmds.annote via api, damn cmds
        return annParent, locator, extras
else:
    def createAnnotation(rootObj, endObj, text=None, name=None, parent=None):
        newparent = parent or base.createDag("_".join([name, "ann_hrc"]), "transform")
        name = name or "annotation"
        locator = base.createDag("_".join([name, "loc"]), "locator", newparent)

        annotationNode = base.nodeByName(cmds.annotate(locator.fullPathName(), tx=text))
        annParent = annotationNode.parent()
        annParent.rename(name)
        annParent.setParent(newparent, maintainOffset=False)
        extras = [newparent]
        endObj.attribute("worldMatrix")[0].connect(locator.offsetParentMatrix)
        rootObj.attribute("worldMatrix")[0].connect(annParent.offsetParentMatrix)
        cmds.select(cl=True)  # todo : delete, should handle cmds.annote via api, damn cmds
        return annParent, locator, extras


def createMultMatrix(name, inputs, output):
    multMatrix = base.createDG(name, "multMatrix")
    compound = multMatrix.matrixIn
    for i in range(1, len(inputs)):
        inp = inputs[i]
        if isinstance(inp, base.Plug):
            inp.connect(compound.element(i))
            continue
        compound.element(i).set(inp)
    inp = inputs[0]
    if isinstance(inp, base.Plug):
        inp.connect(compound.element(0))
    else:
        compound.element(0).set(inp)
    if output is not None:
        multMatrix.matrixSum.connect(output)

    return multMatrix


def createDecompose(name, destination,
                    translateValues=(True, True, True),
                    scaleValues=(True, True, True),
                    rotationValues=(True, True, True),
                    inputMatrixPlug=None):
    """Creates a decompose node and connects it to the destination node.

    :param name: the decompose Matrix name.
    :type name: str
    :param destination: the node to connect to
    :type destination: om2.MObject
    :param translateValues: the x,y,z to apply must have all three if all three are true then the compound will be \
    connected.
    :type translateValues: list(str)
    :param scaleValues: the x,y,z to apply must have all three if all three are true then the compound will be \
    connected.
    :type scaleValues: list(str)
    :param rotationValues: the x,y,z to apply must have all three if all three are true then the compound will be \
    connected.
    :type rotationValues: list(str)
    :param inputMatrixPlug: The input matrix plug to connect from.
    :type inputMatrixPlug: om2.MPlug
    :return: the decompose node
    :rtype: om2.MObject
    """
    decompose = base.createDG(name, "decomposeMatrix")
    if inputMatrixPlug is not None:
        inputMatrixPlug.connect(decompose.inputMatrix)
    if destination:
        decompose.outputTranslate.connect(destination.translate, children=translateValues)
        decompose.outputRotate.connect(destination.rotate, children=rotationValues)
        decompose.outputScale.connect(destination.attribute("scale"), children=scaleValues)
    return decompose


def createReverse(name, inputs, outputs):
    """ Create a Reverse Node

    :param name: The name for the reverse node to have, must be unique
    :type name: str
    :param inputs: If Plug then the plug must be a compound.
    :type inputs: :class:`base.Plug` or tuple
    :param outputs: If Plug then the plug must be a compound.
    :type outputs: :class:`base.Plug` or tuple
    :return: base.DGNode representing the reverse node
    :rtype: :class:`base.DGNode`
    :raises: ValueError if the inputs or outputs is not an om2.MPlug
    """
    rev = base.createDG(name, "reverse")
    inPlug = rev.input
    ouPlug = rev.output

    if isinstance(inputs, base.Plug):
        if inputs.isCompound:
            inputs.connect(inPlug)
            return rev
        raise ValueError("Inputs Argument must be a compound when passing a single plug")
    elif isinstance(outputs, base.Plug):
        if outputs.isCompound:
            outputs.connect(ouPlug)
            return rev
        raise ValueError("Outputs Argument must be a compound when passing a single plug")
    # passed the dealings with om2.MPlug so deal with seq type
    for childIndex in range(len(inputs)):
        inA = inputs[childIndex]
        if inA is None:
            continue
        inputs[childIndex].connect(inPlug.child(childIndex))

    for childIndex in range(len(outputs)):
        inA = outputs[childIndex]
        if inA is None:
            continue
        ouPlug.child(childIndex).connect(outputs[childIndex])
    return rev


def createSetRange(name, value, min_, max_, oldMin, oldMax, outValue=None):
    """ Generates and connects a setRange node.

    input/output arguments take an iterable, possibles values are om2.MPlug,
     float or None.

    if a value is None it will be skipped this is useful when you want
    some not connected or set to a value but the other is left to the
    default state.
    If MPlug is passed and its a compound it'll be connected.

    :param name: the new name for the set Range node
    :type name: str
    :param value:
    :type value: iterable(om2.MPlug or float or None)
    :param min_:
    :type min_: iterable(om2.MPlug or float or None)
    :param max_:
    :type max_: iterable(om2.MPlug or float or None)
    :param oldMin:
    :type oldMin: iterable(om2.MPlug or float or None)
    :param oldMax:
    :type oldMax: iterable(om2.MPlug or float or None)
    :param outValue:
    :type outValue: iterable(om2.MPlug or float or None)
    :return: the created setRange node
    :rtype: om2.MObject

    .. code-block:: python

        one = nodes.createDagNode("one", "transform")
        two = nodes.createDagNode("two", "transform")
        end = nodes.createDagNode("end", "transform")

        oneFn = om2.MFnDagNode(one)
        twoFn = om2.MFnDagNode(two)
        endFn = om2.MFnDagNode(end)
        values = [oneFn.findPlug("translate", False)]
        min_ = [twoFn.findPlug("translate", False)]
        max_ = [twoFn.findPlug("translate", False)]
        oldMax = [0.0,180,360]
        oldMin = [-10,-720,-360]
        reload(creation)
        outValues = [endFn.findPlug("translateX", False), endFn.findPlug("translateY", False), None]
        pma = creation.createSetRange("test_pma", values, min_, max_, oldMin, oldMax, outValues)

    """
    setRange = base.createDG(name, "setRange")
    valuePlug = setRange.value
    oldMinPlug = setRange.oldMin
    oldMaxPlug = setRange.oldMax
    minPlug = setRange.min
    maxPlug = setRange.max

    # deal with all the inputs
    # source list, destination plug
    for source, destination in ((value, valuePlug), (min_, minPlug), (max_, maxPlug), (oldMin, oldMinPlug),
                                (oldMax, oldMaxPlug)):
        if source is None:
            continue
        for index, inner in enumerate(source):
            if inner is None:
                continue
            elif isinstance(inner, base.Plug):
                if inner.isCompound:
                    inner.connect(destination)
                    break
                child = destination.child(index)
                inner.connect(child)
                continue
            child = destination.child(index)
            child.set(inner)
    if outValue is None:
        return setRange
    outPlug = setRange.outValue
    # now the outputs
    for index, out in enumerate(outValue):
        if out is None:
            continue
        if isinstance(out, base.Plug):
            if out.isCompound:
                outPlug.connect(out)
                break
            outPlug.child(index).connect(out)
            continue
        # not a plug must be a plug value
        outPlug.child(index).set(out)
    return setRange


def createPlusMinusAverage1D(name, inputs, output=None, operation=1):
    """ Create's a plusMinusAverage node and connects the 1D inputs and outputs.

    :param name: the plus minus average node name
    :type name: str
    :param inputs: tuple of MPlugs and/or float values, each value will be applied to /
    a new Input1D element. If the value is MPlug then it will be connected
    :type inputs: iterable(plug or float)
    :param output: A tuple of downstream MPlugs to connect to.
    :type output: iterable(plug)
    :return: The plus minus average MObject
    :rtype: om2.MObject

    .. code-block:: python

        one = nodes.createDagNode("one", "transform")
        two = nodes.createDagNode("two", "transform")
        end = nodes.createDagNode("end", "transform")

        oneFn = om2.MFnDagNode(one)
        twoFn = om2.MFnDagNode(two)
        endFn = om2.MFnDagNode(end)
        inputs = [oneFn.findPlug("translateX", False), twoFn.findPlug("translateX", False)]
        outputs = [endFn.findPlug("translateX", False)]
        pma = creation.createPlusMinusAverage1D("test_pma", inputs, outputs)
        # Result: <OpenMaya.MObject object at 0x000002AECB23AE50> #

    """
    pma = base.createDG(name, "plusMinusAverage")
    inPlug = pma.input1D
    pma.operation.set(operation)
    for i, p in enumerate(inputs):
        if p is None:
            continue
        child = inPlug.nextAvailableElementPlug()
        if isinstance(p, base.Plug):
            p.connect(child)
            continue
        child.set(p)

    if output is not None:
        ouPlug = pma.output1D
        for out in output:
            ouPlug.connect(out)
    return pma


def createPlusMinusAverage2D(name, inputs, output=None, operation=1):
    """ Create's a plusMinusAverage node and connects the 2D inputs and outputs.

    :param name: the plus minus average node name
    :type name: str
    :param inputs: tuple of MPlugs and/or float values, each value will be applied to /
    a new Input2D element. If the value is MPlug then it will be connected
    :type inputs: iterable(plug or float)
    :param output: A tuple of downstream MPlugs to connect to.
    :type output: iterable(plug)
    :return: The plus minus average MObject
    :rtype: om2.MObject
    """
    pma = base.createDG(name, "plusMinusAverage")
    inPlug = pma.input2D
    pma.operation.set(operation)
    for i, p in enumerate(inputs):
        if p is None:
            continue
        child = inPlug.nextAvailableElementPlug()
        if isinstance(p, base.Plug):
            p.connect(child)
            continue
        child.set(p)

    if output is not None:
        ouPlug = pma.output2D
        for index, out in enumerate(output):
            if out is None:
                continue
            ouPlug.connect(out)
    return pma


def createPlusMinusAverage3D(name, inputs, output=None, operation=1):
    """ Create's a plusMinusAverage node and connects the 3D inputs and outputs.

    :param name: the plus minus average node name.
    :type name: str
    :param inputs: tuple of MPlugs and/or float values, each value will be applied to /
    a new Input3D element. If the value is MPlug then it will be connected.
    :type inputs: iterable(plug or float)
    :param output: A tuple of downstream MPlugs to connect to.
    :type output: iterable(plug) or None
    :return: The plus minus average MObject.
    :rtype: om2.MObject

    .. code-block:: python

        one = nodes.createDagNode("one", "transform")
        two = nodes.createDagNode("two", "transform")
        end = nodes.createDagNode("end", "transform")

        oneFn = om2.MFnDagNode(one)
        twoFn = om2.MFnDagNode(two)
        endFn = om2.MFnDagNode(end)
        inputs = [oneFn.findPlug("translate", False), twoFn.findPlug("translate", False)]
        outputs = [endFn.findPlug("translate", False)]
        pma = creation.createPlusMinusAverage3D("test_pma", inputs, outputs)
        # Result: <OpenMaya.MObject object at 0x000002AECB23AE50> #
        
    """
    pma = base.createDG(name, "plusMinusAverage")
    inPlug = pma.input3D
    pma.operation.set(operation)
    for i, p in enumerate(inputs):
        if p is None:
            continue
        child = inPlug.nextAvailableElementPlug()
        if isinstance(p, base.Plug):
            p.connect(child)
            continue
        child.set(p)

    if output is not None:
        ouPlug = pma.output3D
        for index, out in enumerate(output):
            if out is None:
                continue
            ouPlug.connect(out)
    return pma


def createControllerTag(node, name, parent=None, visibilityPlug=None):
    """Create a maya kControllerTag and connects it up to the 'node'.

    :param node: The Dag node MObject to tag
    :type node: om2.MObject
    :param name: The name for the kControllerTag
    :type name: str
    :param parent: The Parent kControllerTag mObject or None
    :type parent: om2.MObject or None
    :param visibilityPlug: The Upstream Plug to connect to the visibility mode Plug
    :type visibilityPlug: om2.MPlug or None
    :return: The newly created kController node as a MObject
    :rtype: om.MObject
    """
    ctrl = base.createDG(name, "controller")

    node.message.connect(ctrl.controllerObject)
    if visibilityPlug is not None:
        visibilityPlug.connect(ctrl.visibilityMode)
    if parent is not None:
        ctrl.attribute("parent").connect(parent.children.nextAvailableDestElementPlug())
        parent.prepopulate.connect(ctrl.prepopulate)
    return ctrl


def createDisplayLayer(name):
    """Create's a standard displayLayer

    :todo:: nodes as an argument.
    """
    return base.nodeByName(cmds.createDisplayLayer(name=name, empty=True))


def createIkHandle(name, startJoint, endJoint, solverType="ikRPsolver", parent=None):
    """Creates a Ik handle and returns both the ikHandle and the ikEffector as :class:`DagNode`

    :param name: The name of the ikhandle.
    :type name: str
    :param startJoint: The Start joint
    :type startJoint: :class:`DagNode`
    :param endJoint: The end joint for the effector
    :type endJoint: :class:`DagNode`
    :param solverType: "ikRPSolver" or ikSCsolver
    :type solverType: str
    :return:
    :rtype: tuple(:class:`DagNode`)
    """
    with general.namespaceContext(om2.MNamespace.rootNamespace()):
        ikNodes = cmds.ikHandle(sj=startJoint.fullPathName(),
                                ee=endJoint.fullPathName(),
                                solver=solverType,
                                n=name)
        handle, effector = map(base.nodeByName, ikNodes)
        if parent:
            handle.setParent(parent)
        return handle, effector
