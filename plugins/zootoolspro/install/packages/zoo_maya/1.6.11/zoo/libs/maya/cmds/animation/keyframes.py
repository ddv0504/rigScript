import maya.cmds as cmds

from zoo.libs.utils import output


# -------------------
# TURNTABLE
# -------------------


def createTurntable(rotateGrp, start=0, end=200, spinValue=360, startValue=0, attr='rotateY',
                    tangent="spline", prePost="linear", setTimerange=True, reverse=False, angleOffset=0):
    """Creates a spinning object 360 degrees, useful for turntables

    :param rotateGrp: the group name to animate
    :type rotateGrp: str
    :param start: the start frame
    :type start: float
    :param end: the end frame
    :type end: float
    :param spinValue: the value to spin, usually 360
    :type spinValue: float
    :param startValue: the start value usually 0
    :type startValue: float
    :param attr: the attribute to animate, usually "rotateY"
    :type attr: str
    :param tangent: the tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next" etc
    :type tangent: str
    :param prePost: the infinity option, linear forever?  "constant", "linear", "cycle", "cycleRelative" etc
    :type prePost: str
    :param setTimerange: do you want to set Maya's timerange to the in (+1) and out at the same time?
    :type setTimerange: bool
    :param angleOffset: the angle offset of the keyframes in degrees, will change the start rotation of the asset
    :type angleOffset: float
    :param reverse: reverses the spin direction
    :type reverse: bool
    :return rotateGrp: the grp/object now with keyframes
    :rtype rotateGrp: str
    """
    cmds.cutKey(rotateGrp, time=(-10000, 100000), attribute=attr)  # delete if any keys on that attr
    startValue = startValue + angleOffset
    if reverse:  # spins the other way -360
        spinValue *= -1
    endValue = spinValue + angleOffset
    cmds.setKeyframe(rotateGrp, time=start, value=startValue, breakdown=0, attribute=attr,
                     inTangentType=tangent, outTangentType=tangent)
    cmds.setKeyframe(rotateGrp, time=end, value=endValue, breakdown=0, attribute=attr,
                     inTangentType=tangent, outTangentType=tangent)
    cmds.setInfinity(rotateGrp, preInfinite=prePost, postInfinite=prePost)
    if setTimerange:
        cmds.playbackOptions(minTime=start + 1, maxTime=end)  # +1 makes sure the cycle plays without repeated frame
    return rotateGrp


def turntableSelectedObj(start=0, end=200, spinValue=360, startValue=0, attr='rotateY', tangent="spline",
                         prePost="linear", setTimerange=True, angleOffset=0, reverse=False, message=True):
    """Creates a turntable by spinning the selected object/s by 360 degrees

    :param rotateGrp: the group name to animate
    :type rotateGrp: str
    :param start: the start frame
    :type start: float
    :param end: the end frame
    :type end: float
    :param spinValue: the value to spin, usually 360
    :type spinValue: float
    :param startValue: the start value usually 0
    :type startValue: float
    :param attr: the attribute to animate, usually "rotateY"
    :type attr: str
    :param tangent: the tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next" etc
    :type tangent: str
    :param prePost: the infinity option, linear forever?  "constant", "linear", "cycle", "cycleRelative" etc
    :type prePost: str
    :param setTimerange: do you want to set Maya's timerange to the in (+1) and out at the same time?
    :type setTimerange: bool
    :param angleOffset: the angle offset of the keyframes in degrees, will change the start rotation of the asset
    :type angleOffset: float
    :param reverse: reverses the spin direction
    :type reverse: bool
    :param message: report the message to the user in Maya
    :type message: bool
    :return rotateObjs: the grp/objects now with keyframes
    :rtype rotateGrp: list
    """
    selObjs = cmds.ls(selection=True)
    if not selObjs:
        output.displayWarning("No Objects Selected. Please Select An Object/s")
        return
    for obj in selObjs:
        createTurntable(obj, start=start, end=end, spinValue=spinValue, startValue=startValue, attr=attr,
                        tangent=tangent, prePost=prePost, setTimerange=setTimerange, angleOffset=angleOffset,
                        reverse=reverse)
    if message:
        output.displayInfo("Turntable Create on:  {}".format(selObjs))
    return selObjs


def deleteTurntableSelected(attr="rotateY", returnToZeroRot=True, message=True):
    """Deletes a turntable animation of the selected obj/s. Ie. Simply deletes the animation on the rot y attribute

    :param attr: The attribute to delete all keys
    :type attr: str
    :param returnToZeroRot: Return the object to default zero?
    :type returnToZeroRot: bool
    :param message: Report the messages to the user in Maya?
    :type message: bool
    :return assetGrps: The group/s now with animation
    :rtype assetGrps: list
    """
    selObjs = cmds.ls(selection=True)
    if not selObjs:
        output.displayWarning("No Objects Selected. Please Select An Object/s")
        return
    for obj in selObjs:
        cmds.cutKey(obj, time=(-10000, 100000), attribute=attr)  # delete all keys rotY
    if returnToZeroRot:
        cmds.setAttr(".".join([obj, attr]), 0)
    if message:
        output.displayInfo("Turntable Keyframes deleted on:  {}".format(selObjs))
    return selObjs


# -------------------
# TOGGLE KEY VISIBILITY
# -------------------


def toggleAndKeyVisibility():
    """Inverts the visibility of an object in Maya and keys it's visibility attribute
    Works on selected objects. Example:

        "cube1.visibility True"
        becomes
        "cube1.visibility False"
        and the visibility attribute is also keyed

    """
    selObjs = cmds.ls(selection=True)
    for obj in selObjs:
        if cmds.getAttr("{}.visibility".format(obj)):  # if visibility is True
            cmds.setAttr("{}.visibility".format(obj), 0)
        else:  # False so set visibility to True
            cmds.setAttr("{}.visibility".format(obj), 1)
        cmds.setKeyframe(obj, breakdown=False, hierarchy=False, attribute="visibility")












