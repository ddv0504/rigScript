from maya import cmds
import maya.api.OpenMaya as om2


def resetNodes(nodes, skipVisibility=True, message=False):
    """Resets all keyable unlocked attributes on given objects to their default values.

    Will filter to the channelbox selection if there is one.

    If from selection will only work on transform nodes. See resetSelection()

    Great for running on a large selection such as all character controls.

    :param nodes: A list of Maya nodes
    :type nodes: list(str)
    :param skipVisibility: Don't reset the visibility attribute
    :type skipVisibility: bool
    """
    selAttrs = cmds.channelBox('mainChannelBox', q=True, sma=True) or cmds.channelBox('mainChannelBox', q=True,
                                                                                      sha=True)
    for node in nodes:
        attrs = cmds.listAttr(node, keyable=True, shortNames=True, unlocked=True)
        if not attrs:
            continue
        for attr in attrs:
            if skipVisibility and attr == 'visibility':
                continue
            # If there are selected attributes AND the current attribute isn't in the list of selected attributes, skip
            if selAttrs is not None and attr not in selAttrs:
                continue
            default = 0
            try:
                default = cmds.attributeQuery(attr, n=node, listDefault=True)[0]
            except RuntimeError:
                pass
            attrpath = ".".join([node, attr])
            if not cmds.getAttr(attrpath, settable=True):
                continue
            # need to catch because maya will let the default value lie outside an attribute's
            # valid range (ie maya will let you create an attribute with a default of 0, min 5, max 10)
            try:
                cmds.setAttr(attrpath, default, clamp=True)
            except RuntimeError:
                pass
    if message:
        om2.MGlobal.displayInfo("Attributes Reset")


def resetNode(node, skipVisibility=True):
    """Resets all keyable attributes on a single Maya object to it's default value
    Great for running on a large selection such as all character controls.

    :param skipVisibility: don't reset the visibility attribute
    :type skipVisibility: bool
    """
    return resetNodes([node], skipVisibility=skipVisibility)


def resetSelection(skipVisibility=True, message=True):
    """Resets all keyable attributes on a selection of object to their default value
    Great for running on a large selection such as all character controls.

    :param skipVisibility: don't reset the visibility attribute
    :type skipVisibility: bool
    """
    nodes = cmds.ls(selection=True, type="transform")
    if not nodes:
        if message:
            om2.MGlobal.displayWarning("No Objects Selected, please select the objects to be reset")
        return
    resetNodes(nodes, skipVisibility=skipVisibility, message=message)
