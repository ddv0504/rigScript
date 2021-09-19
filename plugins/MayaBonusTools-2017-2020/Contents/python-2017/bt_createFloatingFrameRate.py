import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

#global floatFrameRateState
#global frameRateCallback_Id


    
def bt_frameRateCounterShape(panelName, data):
    fps = cmds.headsUpDisplay('HUDFrameRate', q=True, sr=True)
    fpsValue = fps[0]
    #fpsOnly = fps[:3]a

    #cmds.setAttr('polyDigits1.counter', float(fpsValue[:5]))
    if cmds.objExists('frameRateCounterShape') == True:
        cmds.undoInfo(swf=False)
        cmds.setAttr('frameRateCounterShape.text', 'Frame Rate:  ' + (fpsValue[:5]), type="string")
        cmds.undoInfo(swf=True)
    #print fpsValue[:5]


def bt_killFrameRateCallback():
    
    global frameRateCallback_Id
    
    try:
        om.MMessage.removeCallback( frameRateCallback_Id )
        print 'Killing Frame Rate callback'
    except:
        print 'No Frame Rate callback'
   


def bt_createFloatingFrameRate():
    
    global frameRateCallback_Id
    global frameRateScriptJob_Id

    #turn on default framerate HUD
    mel.eval('setFrameRateVisibility(1)')
    
    if cmds.objExists('frameRateCounterShape') == False:
        cmds.createNode('annotationShape', n='frameRateCounterShape')
        cmds.addAttr(longName='state', defaultValue=0, minValue=0, maxValue=1, attributeType='long')
        cmds.pickWalk(d='up')
        cmds.rename('frameRateCounter')
        
        cmds.setAttr ('frameRateCounterShape.text', 'Frame Rate', type="string")
        cmds.setAttr ('frameRateCounterShape.displayArrow', 0)
        cmds.setAttr ('frameRateCounterShape.overrideEnabled', 1)
        cmds.setAttr ('frameRateCounterShape.overrideRGBColors', 1)
        cmds.setAttr ('frameRateCounterShape.overrideColorRGB', 1, 0 ,0)

        
    # remove existing callback    
    try:
        om.MMessage.removeCallback( frameRateCallback_Id )
        if cmds.objExists('frameRateCounterShape') == True:
            cmds.setAttr ('frameRateCounterShape.text', 'Frame Rate:  Disabled', type="string")
    except:
        if cmds.objExists('frameRateCounterShape') == True:
            cmds.setAttr ('frameRateCounterShape.text', 'Frame Rate:  Disabled', type="string")        
        

    if cmds.getAttr ('frameRateCounterShape.state') == 0:
        # create callback
        frameRateCallback_Id = omui.MUiMessage.add3dViewPostRenderMsgCallback( 'modelPanel4', bt_frameRateCounterShape )
        frameRateScriptJob_Id = cmds.scriptJob( runOnce=True, event=['NewSceneOpened', bt_killFrameRateCallback] )
        print 'Enabling Frame Rate Counter.   Turn on Show->Dimensions in Panel to see.'
        cmds.inViewMessage( amg='Enabling floating Frame Rate counter.   Turn on Show->Dimensions in Panel to see.', pos='midCenter', fade=True)
        cmds.setAttr ('frameRateCounterShape.state', 1)
    else:
        print 'Disabling Frame Rate Counter'
        cmds.inViewMessage( amg='Disabling floating Frame Rate counter', pos='midCenter', fade=True)
        cmds.setAttr ('frameRateCounterShape.state', 0)
        cmds.scriptJob( kill=frameRateScriptJob_Id, force=True)
                

# create annotation node
#bt_createFloatingFrameRate()
