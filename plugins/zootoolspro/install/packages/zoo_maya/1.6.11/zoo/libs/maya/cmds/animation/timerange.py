from maya import cmds


# -------------------
# ANIMATION & PLAYBACK FRAME RANGES
# -------------------


def playbackRangeStartToCurrentFrame(animationStartTime=True):
    """Sets the range slider start to be the current frame in time

    :param animationEndTime: if True sets the range to be the entire range, False is playback range only
    :type animationStartTime: bool
    """
    theCurrentTime = cmds.currentTime(query=True)
    if animationStartTime:
        cmds.playbackOptions(animationStartTime=theCurrentTime)
    else:
        cmds.playbackOptions(minTime=theCurrentTime)


def playbackRangeEndToCurrentFrame(animationEndTime=True):
    """Sets the range slider end to be the current frame in time

    :param animationEndTime: if True sets the range to be the entire range, False is playback range only
    :type animationEndTime: bool
    """
    theCurrentTime = cmds.currentTime(query=True)
    if animationEndTime:
        cmds.playbackOptions(animationEndTime=theCurrentTime)
    else:
        cmds.playbackOptions(maxTime=theCurrentTime)


def animMoveTimeForwardsBack(frames):
    """Moves the time slider back or forwards by these amount of frames.  Can be a negative number for backwards.

    :param frames: The amount of frames to offset from current time
    :type frames: float
    """
    theCurrentTime = cmds.currentTime(query=True)
    cmds.currentTime(theCurrentTime + frames)


def getRangePlayback():
    """Returns the playback range, so the start and end frame of the grey bar in the timeline

    :return timeRange: The start and end time in a list
    :rtype timeRange: list(float)
    """
    return [cmds.playbackOptions(minTime=True, query=True),
            cmds.playbackOptions(maxTime=True, query=True)]


def getRangeAnimation():
    """Returns the animation range, so the start and end frame of whole timeline.
    Not the grey bar but the min and max range.

    :return timeRange: The start and end time in a list
    :rtype timeRange: list(float)
    """
    return [cmds.playbackOptions(animationStartTime=True, query=True),
            cmds.playbackOptions(animationEndTime=True, query=True)]


# -------------------
# GET FRAME RANGES - FROM KEYFRAMES
# -------------------


def getTimeRangeAnimCurveSelection(animCurve):
    timeKeys = cmds.keyframe(animCurve, query=True, timeChange=True, selected=True)
    return [timeKeys[0], timeKeys[-1]]


def getTimeRangeAnimCurveList(animCurveList):
    startFrameList = list()
    endFrameList = list()
    for animCurve in animCurveList:
        range = getTimeRangeAnimCurveSelection(animCurve)
        startFrameList.append(range[0])
        endFrameList.append(range[-1])
    return [min(startFrameList), max(endFrameList)]


# -------------------
# GET KEYFRAMES - FRAME RANGES
# -------------------


def keysInRange(obj, attr, timeRange=[0 - 100]):
    """Returns all keyframes of an attribute within a range

    :param obj:
    :type obj:
    :param attr:
    :type attr:
    :param timeRange:
    :type timeRange:
    :return:
    :rtype:
    """
    keyList = cmds.keyframe(obj, attribute=attr, query=True, timeChange=True)
    if not keyList:
        return list()
    return list(x for x in keyList if timeRange[0] <= x <= timeRange[1])


def keysInRangeCurve(animCurve, timeRange=[0 - 100]):
    """Returns all keyframes of an attribute within a range

    :param animCurve:
    :type animCurve:
    :param timeRange:
    :type timeRange:
    :return:
    :rtype:
    """
    keyList = cmds.keyframe(animCurve, query=True, timeChange=True)
    if not keyList:
        return list()
    return list(x for x in keyList if timeRange[0] <= x <= timeRange[1])
