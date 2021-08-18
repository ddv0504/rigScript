import maya.cmds as cmds
import maya.mel as mel

class srcAttrBtn(object):
    def __init__(self,name,attr,parent=None):
        self.name = name
        self.parent = parent
        self.attr = attr
        
        cmds.rowLayout('%sLayout' % self.name,parent=self.parent,nc=2)   
        cmds.button(self.name,c=self.click,ann=self.name)
        cmds.button('%sRemove' % self.name,l='-',c=self.remove)
        
    def click(self,*args):
        
        if cmds.button(self.name,q=True,bgc=True) == [0,1,0]:
            cmds.button(self.name,bgc=(.4,.4,.4),e=True)
            connectedAttrs = cmds.listConnections(self.attr)
            if connectedAttrs:
                for attr in connectedAttrs:               
                    cmds.deleteUI(attr)             
            
        else:
            cmds.button(self.name,bgc=(0,1,0),e=True)
            
            connectedAttrs = cmds.listConnections(self.attr)
            
            if connectedAttrs:
                for attr in connectedAttrs:
                    if cmds.button(attr,ex=True):
                        continue
                    
                    trgAttrBtn(attr,parent='ztTargetAttrLayout')
            else:
                cmds.button(self.name,bgc=(.4,.4,.4),e=True)
    def remove(self,*args):
        cmds.deleteUI('%sLayout' % self.name)
        if not cmds.objExists(self.attr):
            return
        connectedAttrs = cmds.listConnections(self.attr)
        if connectedAttrs:
            for attr in connectedAttrs:               
                cmds.deleteUI(attr) 
class trgAttrBtn(object):
    def __init__(self,name,parent=None):
        self.name=name
        self.parent = parent
        cmds.button(self.name,ann=self.name,parent=self.parent,c=self.click)
    def click(self,*args):
        cmds.select(self.name,r=True)
    
def channelBoxSelectedEvent(parentUI):
    attrs = mel.eval('channelBox -q -selectedMainAttributes mainChannelBox;')
    sel = cmds.ls(sl=True)[0]
    if not attrs:
        return
    try:
        if '%s_%sLayout' % (sel,attrs[0]) in cmds.scrollLayout('ztSourceAttrLayout',ca=True,q=True):
            return
    except:
        pass
    srcAttrBtn('%s_%s' % (sel,attrs[0]),'%s.%s' % (sel,attrs[0]),parentUI)
    
def clearUI(*args):
    try:
        [cmds.deleteUI(i) for i in cmds.scrollLayout('ztSourceAttrLayout',q=True,ca=True)]
        [cmds.deleteUI(i) for i in cmds.frameLayout('ztTargetAttrLayout',q=True,ca=True)]
    except Exception as e:
        pass
def main(*args):
    
    if cmds.window('ztAttributeTools',ex=True):
        cmds.deleteUI('ztAttributeTools')
    
    cmds.window('ztAttributeTools',wh=(680,380))    
    cmds.frameLayout('ztAttributeToolsMainLayout',lv=True,l='AttributeList:')
       
    cmds.rowLayout(nc=2,adj=1)
    cmds.frameLayout('ztSourceAttrs')
    cmds.scrollLayout('ztSourceAttrLayout',h=500,w=320)  
    cmds.scriptJob(event=('ChannelBoxLabelSelected',lambda:channelBoxSelectedEvent('ztSourceAttrLayout')),parent='ztAttributeTools')
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout('ztTargetAttrLayout',h=500,w=450)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.button('ztAttributeToolsClearButton',l='Clear',c=clearUI)
    cmds.showWindow()