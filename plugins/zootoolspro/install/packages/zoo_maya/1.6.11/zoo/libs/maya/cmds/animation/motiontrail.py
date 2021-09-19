import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.mel as mel

from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import namehandling


def createMotionTrail():
    """Creates a motion trail on the selected object and changes the draw mode to `alternating` frames"""
    # List all motiontrails in the scene
    if not cmds.ls(selection=True):
        om2.MGlobal.displayWarning("Please select an object to create a motion trail.")
        return
    allMoTrailShapes = cmds.ls(type="motionTrailShape")
    mel.eval('CreateMotionTrail;')  # Build the trail
    updatedTrailShapes = cmds.ls(type="motionTrailShape")
    motionTrailShapes = list(set(updatedTrailShapes).difference(allMoTrailShapes))  # Take second list from first
    if not motionTrailShapes:
        om2.MGlobal.displayWarning("Motion Trail not created")
        return

    # TODO:  Could build manually
    # node = cmds.createNode("motionTrail", name="someName", skipSelect=True)
    # shape = cmds.createNode("motionTrailShape", skipSelect=True)
    # Then connect manually gah! Maybe not.

    for motionTrail in motionTrailShapes:  # Change to alternating display type
        cmds.setAttr("{}.trailDrawMode".format(motionTrail), 1)


# ---------------------------
# CLONE OBJECTS FROM ANIMATION
# ---------------------------


def cloneObjFromAnimation(obj, startTime, endTime, objToFrame=1.0):
    """Creates objects from animation with snapshot, clones new objects.

    :param obj: A single object name, should be keys on translation
    :type obj: str
    :param startTime: The time start point to start creeating the curve
    :type startTime: float
    :param endTime: The time end point to end creating the curve
    :type endTime: float
    :param objToFrame: The amount of objects to frames, 1.0 is one obj per frame, 2.0 is one obj every 2 frames
    :type objToFrame: float
    """
    # snapNode is a snapshot node used to automatically duplicate the objects along the timeline
    snapNode = cmds.snapshot(obj, n="{}_snap".format(obj),
                             increment=objToFrame,
                             startTime=startTime,
                             endTime=endTime,
                             update='animCurve')[0]  # create snap node for geo trail
    # Rename objects -------------------------
    objList = cmds.listRelatives(snapNode, children=True)
    namehandling.renumberListSingleName(obj, objList, removeTrailingNumbers=True, addUnderscore=True, padding=2,
                                        renameShape=True, message=False)
    return snapNode, objList


def cloneObjsFromAnimation(objs, startTime, endTime, objToFrame=1):
    """Creates objects from animation with snapshot, clones new objects.

    :param objs: A list of objects (transforms) to create the CV curve.
    :type objs: list(str)
    :param startTime: The time start point to start creeating the curve
    :type startTime: float
    :param endTime: The time end point to end creating the curve
    :type endTime: float
    :param objToFrame: The amount of objects to frames, 1.0 is one obj per frame, 2.0 is one obj every 2 frames
    :type objToFrame: float
    """
    for obj in objs:
        cloneObjFromAnimation(obj, startTime, endTime, objToFrame=objToFrame)


def cloneObjsFromAnimationSelected(objToFrame=1):
    """Creates objects from animation with snapshot, clones new objects.

    :param objToFrame: The amount of objects to frames, 1.0 is one obj per frame, 2.0 is one obj every 2 frames
    :type objToFrame: float
    """
    selObjs = cmds.ls(sl=True, type='transform')
    if not selObjs:
        output.displayInfo("Nothing Selected, please select an animated object")
        return
    startTime = cmds.playbackOptions(query=True, min=True)
    endTime = cmds.playbackOptions(query=True, max=True)
    cloneObjsFromAnimation(selObjs, startTime, endTime, objToFrame=objToFrame)


# ---------------------------
# CV CURVE FROM OBJ
# ---------------------------


def cvCurveFromObjAnimation(obj, startTime, endTime, cvEveryFrame=1.0):
    """Creates a CV curve based on an animated object with keys per frame.

    Credit DELANO ATHIAS, cleaned up/faster code from:
        https://www.delanimation.com/tutorials-1/2020/1/2/generating-curves-from-motion-trails-in-maya

    :param obj: A single object name, should be keys on translation
    :type obj: str
    :param startTime: The time start point to start creeating the curve
    :type startTime: float
    :param endTime: The time end point to end creating the curve
    :type endTime: float
    :param cvEveryFrame: The amount of cvs per frame, 1.0 is one cv per frame, 2.0 is one CV every 2 frames
    :type cvEveryFrame: float
    """
    plane = cmds.polyPlane()[0]  # Plane geo needed for snapshot trail
    cmds.pointConstraint(obj, plane)
    cmds.select(plane, replace=True)  # Cube needs to be selected for the trail
    # snapNode is a snapshot node used to automatically duplicate the curves along the curve
    snapNode = cmds.snapshot(n="{}_snap".format(obj),
                             increment=cvEveryFrame,
                             startTime=startTime,
                             endTime=endTime,
                             update='animCurve')[0]  # create snap node for geo trail
    planeList = cmds.listRelatives(snapNode, children=True)
    cvCount = len(planeList) - 1
    # Create Curve -----------------------------------------------
    cvCurve = cmds.curve(degree=1, point=[(0, 0, 0), (0, 0, 1)])
    cvCurve = cmds.rebuildCurve(cvCurve,
                                constructionHistory=False,
                                rpo=True,
                                rebuildType=0,
                                endKnots=0,
                                spans=cvCount,
                                degree=1)  # Rebuild the curve with correct spans
    # Store cvs in a list ----------------------
    cmds.select(('{}.cv[0:*]'.format(cvCurve[0])), replace=True)
    cvs = cmds.ls(selection=True, flatten=True)
    # Match curve cvs to cubes ---------------------------
    for i, planeGeo in enumerate(planeList):
        wSpace = cmds.objectCenter(planeGeo, gl=True)  # Finds the center of the planeGeo in global space
        cmds.move(wSpace[0], wSpace[1], wSpace[2], cvs[i], worldSpace=True)
    # Cleanup ---------------------------------------------
    cmds.delete(cvCurve, constructionHistory=True)
    cmds.delete(plane, snapNode)
    # Make the curve smooth - 3 degrees -----------------------------
    cmds.rebuildCurve(cvCurve,
                      constructionHistory=False,
                      replaceOriginal=True,
                      rebuildType=0,
                      endKnots=0,
                      keepControlPoints=True,
                      keepEndPoints=True,
                      degree=3)


def cvCurveFromObjsAnimation(objs, startTime, endTime, cvEveryFrame=1):
    """Creates a CV curve based on an animated object with keys per frame.

    Credit DELANO ATHIAS, cleaned up code from
    https://www.delanimation.com/tutorials-1/2020/1/2/generating-curves-from-motion-trails-in-maya

    :param objs: A list of objects (transforms) to create the CV curve.
    :type objs: list(str)
    :param startTime: The time start point to start creeating the curve
    :type startTime: float
    :param endTime: The time end point to end creating the curve
    :type endTime: float
    :param cvEveryFrame: The amount of cvs per frame, 1.0 is one cv per frame, 2.0 is one CV every 2 frames
    :type cvEveryFrame: float
    """
    for obj in objs:
        cvCurveFromObjAnimation(obj, startTime, endTime, cvEveryFrame=cvEveryFrame)


def cvCurveFromObjAnimationSelected(cvEveryFrame=1):
    """Creates a CV curve based on an animated selected objects uses the time range and sets a CV per frame.

    Credit DELANO ATHIAS, cleaned up code from
    https://www.delanimation.com/tutorials-1/2020/1/2/generating-curves-from-motion-trails-in-maya

    :param cvEveryFrame: The amount of cvs per frame, 1.0 is one cv per frame, 2.0 is one CV every 2 frames
    :type cvEveryFrame: float
    """
    selObjs = cmds.ls(sl=True, type='transform')
    if not selObjs:
        output.displayInfo("Nothing Selected, please select an animated object")
        return
    startTime = cmds.playbackOptions(query=True, min=True)
    endTime = cmds.playbackOptions(query=True, max=True)
    cvCurveFromObjsAnimation(selObjs, startTime, endTime, cvEveryFrame=cvEveryFrame)
