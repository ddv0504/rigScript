import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import ztRigUtil
reload(ztRigUtil)
class buttonGroup(object):
    def __init__(self,name,mesh,parent=None,lock=False):
        self.name = name
        self.parent = parent
        self.lock = lock
        self.mesh = mesh
        cmds.rowLayout('%s_Layout' % self.name,adj=1,nc=3,parent=self.parent,cl3=('left','left','right'),cw=(1,240))
        cmds.button(self.name,l=self.name,c=self.lockToggle)
        cmds.text(' ')
        if self.lock:
            cmds.text('%s_infLockTx' % self.name,l='locked')
            self.setBackGroundColor((1,0,0))
        else:
            cmds.text('%s_infLockTx' % self.name,l='unlocked')
            self.setBackGroundColor((0,1,0))
        cmds.setParent('..')
    def lockToggle(self,*args):
        if not ztRigUtil.getLockState(self.mesh,self.name):
            ztRigUtil.lockInf(self.mesh,self.name)
            self.setBackGroundColor((1,0,0))
        else:
            ztRigUtil.unlockInf(self.mesh,self.name)
            self.setBackGroundColor((0,1,0))
    def setBackGroundColor(self,color):
        cmds.button(self.name,e=True,bgc=color)
        
def addJntButton(*args):
    lst = cmds.ls(sl=True)
    transform = cmds.textFieldButtonGrp('meshNameTxField',q=True,tx=True)
    mesh = pm.ls(transform)[0].getShape().name()
    if not mesh or not ztRigUtil.getSkinClusterFromMesh(mesh):
        return
    
    for i in lst:
        if not cmds.objectType(i) == 'joint':
            print('Must selected objects are joint.')
            return
    for i in lst: 
        # if ztRigUtil.getLockState():  
        lock = ztRigUtil.getLockState(mesh,i)  
        button = buttonGroup(i,mesh,'jntButtonLayout',lock=lock)

def clearLayout(*args):
    lst = cmds.scrollLayout('jntButtonLayout',ca=True,q=True)    
    for l in lst:
        cmds.deleteUI(l)
def lockSwitch(lockState,*args):
    '''
    parameter:
        lockState: text(locked or unlocked)
    '''
    transform = cmds.textFieldButtonGrp('meshNameTxField',q=True,tx=True)
    mesh = pm.ls(transform)[0].getShape().name()
    jntLst = cmds.scrollLayout('jntButtonLayout',ca=True,q=True)
    jntLst = [i.split('_Layout')[0] for i in jntLst]
    for jnt in jntLst:
        if lockState == 'locked':
            cmds.text('%s_infLockTx' % jnt,l=lockState,e=True)
            cmds.button(jnt,e=True,bgc=(1,0,0))
            ztRigUtil.lockInf(mesh, jnt)
        elif lockState == 'unlocked':
            cmds.text('%s_infLockTx' % jnt,l=lockState,e=True)
            cmds.button(jnt,e=True,bgc=(0,1,0))
            ztRigUtil.unlockInf(mesh, jnt)
def main(*args):
    if cmds.window('infLocker',ex=True):
        cmds.deleteUI('infLocker')
    cmds.window('infLocker',wh=(300,640))
    cmds.frameLayout(lv=True,l='object:')
    cmds.textFieldButtonGrp('meshNameTxField',ed=False,bl='<<',bc=lambda:cmds.textFieldButtonGrp('meshNameTxField',tx = cmds.ls(sl=True)[0],e=True))
    cmds.setParent('..')
    cmds.rowLayout(nc=2)
    cmds.button(l='Lock',c=lambda x:lockSwitch('locked'))
    cmds.button(l='Unlock',c=lambda x:lockSwitch('unlocked'))
    cmds.setParent('..')
    cmds.frameLayout(l='Joint list',lv=True)
    cmds.scrollLayout('jntButtonLayout')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(style='in')
    cmds.rowLayout(nc=2)
    cmds.button(l='Get Joints',c=addJntButton)
    cmds.button(l='clear',c=clearLayout)
    cmds.showWindow('infLocker')
    cmds.window('infLocker',wh=(300,640),e=True)