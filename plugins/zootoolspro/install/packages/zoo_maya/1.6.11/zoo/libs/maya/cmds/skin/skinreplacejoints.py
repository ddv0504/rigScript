import maya.cmds as cmds
import maya.api.OpenMaya as om2

from zoo.libs.maya.cmds.objutils import namehandling, connections
from zoo.libs.maya.cmds.skin import bindskin


REPLACE_SKIN_ATTRS = ["worldMatrix", "objectColorRGB", "lockInfluenceWeights", "bindPose", "message"]
SKIN_DEST_TYPES = ["skinCluster", "dagPose"]

def replaceSkinMatrixJoint(boundJoint, replaceJoint):
    """Swaps the binding of a joint and replaces the bind to another joint.

    Useful while swapping the skinning from one skeleton to another.

    The skinning is swapped based on the matrix positions, so if the joint is in new locations the mesh may move.

    :param boundJoint: The joint with the skinning, to be replaced
    :type boundJoint: str
    :param replaceJoint: The new joint that will receive the skinning
    :type replaceJoint: str
    """
    if not cmds.attributeQuery('lockInfluenceWeights', node=replaceJoint, exists=True):
        cmds.addAttr(replaceJoint, longName='lockInfluenceWeights', attributeType='bool')  # New joints need this attr
    for attr in REPLACE_SKIN_ATTRS:  # "worldMatrix", "objectColorRGB" etc
        connections.swapDriverConnectionAttr(boundJoint, replaceJoint, attr, checkDestNodeTypes=SKIN_DEST_TYPES)


def replaceSkinJointMatrixList(boundJoints, replaceJoints, filterSkinnedJoints=True, message=False):
    """Swaps the binding of a list of joints and replaces the bind to another list of joints.

    Useful while swapping the skinning from one skeleton to another.

    The skinning is swapped based on the matrix positions, so if joints are in new locations the mesh may move.

    :param boundJoints: A list of joints bound to a skin cluster
    :type boundJoints: list(str)
    :param replaceJoints: A list of joints to be switched to connect to the skin cluster
    :type replaceJoints: list(str)
    :param message: Report the message to the user
    :type message: bool
    """
    if filterSkinnedJoints:
        boundJoints = bindskin.filterSkinnedJoints(boundJoints)
        # TODO check not referenced joints
        if not boundJoints:
            return
    for i, boundJnt in enumerate(boundJoints):
        replaceSkinMatrixJoint(boundJnt, replaceJoints[i])
    if message:
        shortNames = namehandling.getShortNameList(replaceJoints)
        om2.MGlobal.displayInfo("Skinning transferred to: {}".format(shortNames))

