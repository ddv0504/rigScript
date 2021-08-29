import maya.cmds as cmds
import maya.mel as mel

def breakAnimCycle():
    currentTime=cmds.currentTime(q=True)
    animCurves = cmds.keyframe(n=True,sl=True,q=True)
    
    if not animCurves:
        print('Select animation curves first!')
        return
    if cmds.window('AnimCurveCycle',ex=True):
        cmds.deleteUI('AnimCurveCycle')
    window = cmds.window('AnimCurveCycle')
    cmds.frameLayout('AnimCurveCycleLayout')
    
    progressControl = cmds.progressBar(maxValue=100, width=300)
    cmds.showWindow( window )
    for animCurve in animCurves:
        cmds.frameLayout('AnimCurveCycleLayout',e=True,l='Copy %s...' % animCurve)
        if cmds.progressBar(progressControl, query=True, isCancelled=True):
            break
        frames = cmds.keyframe(animCurve,q=True)
        maxFrame = max(frames)
        minFrame = min(frames)
        frameRange = maxFrame-minFrame
        cmds.copyKey(animCurve)
        if currentTime > maxFrame:
            while maxFrame < currentTime:
                cmds.pasteKey(animCurve,copies= 1)
                maxFrame = max(cmds.keyframe(animCurve,q=True))
            cmds.setKeyframe(animCurve,insert=True,t=currentTime)
            cmds.cutKey(animCurve,t=(currentTime+1,currentTime+frameRange))

        if currentTime < minFrame:
            n=0
            while minFrame > currentTime:
                n += 1
                pastFrame = maxFrame-frameRange*n
                cmds.pasteKey(animCurve,copies=1,timeOffset = 0,option='merge',connect=0,floatOffset=0,valueOffset=0,t=(pastFrame,pastFrame))
                minFrame = min(cmds.keyframe(animCurve,q=True))
                minFrame=min(cmds.keyframe(animCurve,q=True))
            cmds.setKeyframe(animCurve,insert=True,t=currentTime)
            cmds.cutKey(animCurve,t=(currentTime-frameRange,currentTime-1))
        cmds.progressBar(progressControl,e=True,step=1)
    cmds.progressBar(progressControl,endProgress=True)
    cmds.deleteUI('AnimCurveCycle')


def moveKeyFrame(frame=0,toFrame=False,move=False,overLap=False):
    if toFrame:
        minFrame = min(cmds.keyframe(sl=True,q=True))
        moveValue = frame - minFrame
        cmds.keyframe(e=True,tc=moveValue,iub=True,r=True,o='over')

    if move:
        cmds.keyframe(e=True,tc=frame,iub=True,r=True,o='over')

    if overLap:
        n=0
        for obj in cmds.ls(sl=True):
            cmds.keyframe(obj,e=True,tc=n,iub=True,r=True,o='over')
            n+=frame

def alignKeyframe(right=False,current=False):
    animCurves = pm.keyframe(name=True,q=True)
    times  = pm.keyframe(tc=True,q=True)
    if not any([animCurves,times]):
        print('Select keys first...')
        return
    dic = {}
    for animCurve,t in zip(animCurves,times):
        dic[animCurve] = t
    minTime = min(dic.values())
    maxTime = max(dic.values())
    currentTime = cmds.currentTime(q=True)

    for anim,t in dic.items():
        tc = (t-minTime)*-1
        if right:
            tc = (t-maxTime)*-1
        if current:
            tc = (currentTime - t)
        cmds.keyframe(anim,e=True, iub=True,r=True, o='over',tc=tc,t=(t,t))