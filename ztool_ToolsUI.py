# -*- coding: utf-8 -*-
from __future__ import print_function
from imp import reload
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os
import zt_AniUI
reload(zt_AniUI) 
try:    
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtUiTools import *
    import shiboken2

except:    
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtUiTools import *
    import shiboken

SHELF_PATH = '%s/shelves' % os.path.dirname(__file__).replace('\\','/')

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    try:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(int(mayaMainWindowPtr), QMainWindow)             
    return mWindow

class mayaShelfWidget(QWidget):
    def __init__(self,name,path='',parent=None):
        super(mayaShelfWidget,self).__init__()
        self.name = name
        self.path = path
        self.setObjectName = self.name
        self.vLayout = QVBoxLayout(self)
        self.widget = self.shelfWidget()
        self.widget.setParent(self)
        self.vLayout.addWidget(self.widget)
    def shelfWidget(self): 
        mainWindow = maya_main_window()
        funcName = ''
        if self.path:
            with open( self.path,'r') as f:
                lines = f.readlines()
                
            for line in lines:
                if 'global proc' in line:
                    funcName = '%s()' % line.split(' ')[2]
            mel.eval('source"%s"'% self.path)  
            
        if cmds.shelfLayout(self.name,ex=True):
            cmds.deleteUI(self.name)                        
        shelfLayout = cmds.shelfLayout(self.name,parent=mainWindow.objectName())
        
        mel.eval(funcName)   
        ptr = omui.MQtUtil_findControl(shelfLayout)
        try:   
            return shiboken2.wrapInstance(long(ptr),QWidget)  
        except:
            return shiboken2.wrapInstance(int(ptr),QWidget)  
    def contextMenuEvent(self,event):
        contextMenu = QMenu(self)
        saveAction = QAction(u'save',self)
        contextMenu.addAction(saveAction)
        saveAction.triggered.connect(lambda:(cmds.saveShelf(self.name,os.path.splitext(self.path)[0]),print('Shelf was saved')))
        contextMenu.exec_(self.mapToGlobal(event.pos()))

class toolBox(QMainWindow):
    selList =    ["Polygon","Curves","Locator","Constraint","Hierachy","HideObject","Joint","AnimObject","AnimNode"]
    constrains = ["ParentConstraint","PointConstraint","OrientConstraint","ScaleConstraint","AimConstraint"]
    keyframes =  ["SetKey","Animated","Translate","Rotate","Scale","HoldCurrentKeys","cutKey","DeleteKeys"]
    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent=maya_main_window())  
        self.setObjectName("Toolbox")
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.init()
        self.setForm() 
        self.setFocusPolicy(Qt.NoFocus)       
        
    def init(self):
        self.setting = QSettings("optionData","toolBoxOptions")
        self.resize(370,840)
        if self.setting.value('size'):
            self.resize(self.setting.value('size'))
        if self.setting.value('pos'):
            self.move(self.setting.value('pos'))
        self.setWindowTitle("ToolsBox")
    
    def setForm(self):
        self.mainLayout = QVBoxLayout(self.mainWidget)
        
        self.setLayout(self.mainLayout)
        self.viewEditorLayout = QHBoxLayout()
        self.viewEditorLayout.setSpacing(0)
        self.viewEditorLayout.setContentsMargins(0,0,0,0)
        self.viewerBox = QGroupBox()
        self.viewerBox.setTitle('View')
        self.viewerBox.setContentsMargins(0,0,0,0)
        viewerBoxLayout = QHBoxLayout()
        viewerBoxLayout.setContentsMargins(0,0,0,0)
        viewerBoxLayout.setSpacing(0)
        self.viewerBox.setLayout(viewerBoxLayout)
        viewerShelf = mayaShelfWidget(name='ztView',path='%s/ztView.mel' % SHELF_PATH)
        viewerBoxLayout.addWidget(viewerShelf)
        self.editorBox = QGroupBox()
        self.editorBox.setTitle('EdiorWindows')
        self.editorBox.setContentsMargins(0,0,0,0)
        editorBoxLayout = QHBoxLayout()
        editorBoxLayout.setSpacing(0)
        editorBoxLayout.setContentsMargins(0,0,0,0)
        self.editorBox.setLayout(editorBoxLayout)
        editorShelf = mayaShelfWidget(name='ztEditorWindow',path='%s/ztEditorWindow.mel' % SHELF_PATH)
        editorBoxLayout.addWidget(editorShelf)
        

        self.viewEditorLayout.addWidget(self.viewerBox)
        self.viewEditorLayout.addWidget(self.editorBox)
        

        self.selBox  = QGroupBox(self.mainWidget)
        self.selBox.setTitle("Selection:")
        self.selLayout  = QVBoxLayout()
        self.selBox.setLayout(self.selLayout)
        
        self.consBox = QGroupBox(self.mainWidget)
        self.consBox.setTitle("Constraint:")
        self.consLayout  = QVBoxLayout()
        self.consBox.setLayout(self.consLayout)
        
        self.keyBox  = QGroupBox(self.mainWidget)
        self.keyBox.setTitle("Keyframe")
        self.keyLayout  = QVBoxLayout()
        self.keyBox.setLayout(self.keyLayout)

        self.connectBox = QGroupBox(self.mainWidget)
        self.connectBox.setTitle("Connection:")
        
        self.utilBox = QGroupBox(self.mainWidget)
        self.utilBox.setTitle("Category")       
        self.utilLayout  = QHBoxLayout()
        self.utilBox.setLayout(self.utilLayout)

        self.mainLayout.addLayout(self.viewEditorLayout)
        self.mainLayout.addWidget(self.selBox)
        self.mainLayout.addWidget(self.consBox)
        self.mainLayout.addWidget(self.connectBox)
        self.mainLayout.addWidget(self.keyBox)
        self.mainLayout.addWidget(self.utilBox)
        
        self.addSelection()  #Add selection items  ex: Polygon,Curves,Locator etc...
        self.addConstraint() #Add Constraint items 
        self.setConnectBox()    #Set Connect Box Widget
        self.addKeyframe()   #Add Keyframe items
        self.addUtil()       #Add Util items
        
    def addSelection(self):
        for seq,btnName in  enumerate(self.selList):
            if seq % 3 == 0 or seq == 0:
                btnLayout = QHBoxLayout()
            btn = QPushButton(btnName)
            btn.setObjectName(btnName)
            btnLayout.addWidget(btn)
            
            if btnName == 'Polygon':
                btn.clicked.connect(lambda: selPolyMesh('mesh'))
            
            if btnName == 'Curves':
                btn.clicked.connect(lambda: selPolyMesh('nurbsCurve'))                            
                           
            if btnName == 'Locator':
                btn.clicked.connect(lambda: selPolyMesh('locator'))   
            
            if btnName == 'Constraint':
                btn.clicked.connect(lambda: selPolyMesh('constraint'))
             
            if btnName == "Hierachy":
                btn.clicked.connect(lambda: cmds.select(r=True,hi=True))
              
            if btnName == 'HideObject':
                btn.clicked.connect(lambda: selPolyMesh('hide'))
            
            if btnName == 'Joint':
                btn.clicked.connect(lambda: selPolyMesh('joint')) 
             
            if btnName == 'AnimObject':
                btn.clicked.connect(lambda: selkeyedobjs())
            
            if btnName == 'AnimNode':
                btn.clicked.connect(lambda: selPolyMesh('animNode'))   
            
            self.selLayout.addLayout(btnLayout)
            
    def addConstraint(self):
        offsetLayout = QHBoxLayout()
        self.consLayout.addLayout(offsetLayout)
        
        self.offsetCheckBox = QCheckBox(self.mainWidget)
        self.offsetCheckBox.setObjectName("offsetCheckBox")
        self.offsetCheckBox.setText("Maintain offset")
        self.offsetCheckBox.setLayoutDirection(Qt.RightToLeft)
        offsetLayout.addWidget(self.offsetCheckBox)
        offsetSpacerItem = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)        
        offsetLayout.addSpacerItem(offsetSpacerItem)
        
        consTypeLayout = QHBoxLayout(self.mainWidget)
        for seq,consType in enumerate(self.constrains):
            if seq % 3 == 0 or seq == 0:
                consLayout = QHBoxLayout(self.mainWidget)
            btn = QPushButton(consType)
            btn.setObjectName(consType)
            btn.clicked.connect(eval("self.{0}".format(consType.lower())))
            consLayout.addWidget(btn)                
            self.consLayout.addLayout(consLayout)
        
        channelLayout = QHBoxLayout()
        channelLayout.setSpacing(30)
        chennelLst = ['x','y','z']
        
        label = QLabel("Channel:")
        channelLayout.addWidget(label)
        for seq,channel  in enumerate(chennelLst):
            checkBox = QCheckBox(channel)
            checkBox.setObjectName(channel)
            checkBox.setCheckState(Qt.Checked)
            checkBox.setLayoutDirection(Qt.RightToLeft)
            channelLayout.addWidget(checkBox)
        channelSpacerItem = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)        
        channelLayout.addSpacerItem(channelSpacerItem)
        self.consLayout.addLayout(channelLayout) 
                   
    def addKeyframe(self):
        cmdA = lambda cmd: eval('cmds.SetKey%s' % cmd)
        cmdB = lambda cmd: eval('cmds.%s' % cmd)
        for seq,key  in enumerate(self.keyframes):            
            if seq % 3 == 0 or seq == 0:
                keyLayout = QHBoxLayout(self.mainWidget)
            btn = QPushButton(key)
            btn.setObjectName(key)
            if not key in ['SetKey','HoldCurrentKeys', 'DeleteKeys','cutKey']:
                btn.clicked.connect(cmdA(key))
            elif key == 'cutKey':
                btn.clicked.connect(lambda: cmds.cutKey(t=(cmds.currentTime(q=True),cmds.currentTime(q=True)))) 
            else:
                btn.clicked.connect(cmdB(key))
            keyLayout.addWidget(btn)                
            self.keyLayout.addLayout(keyLayout)

    def addUtil(self):
        
        niceNameLst = ['Animation','Rig','Light','FX']
        toolNameLst = ['zt_AniUI','zt_RigUI','zt_LightUI','zt_FXUI']
        
        for name,tool in zip(niceNameLst,toolNameLst):     
            toolBtn = utilBtn(name=name,module=tool)                
            toolBtn.setText(name)
            self.utilLayout.addWidget(toolBtn)

    def parentconstraint(self):
        offset = False
        if self.offsetCheckBox.checkState() == Qt.Checked:
            offset = True            
        objs = cmds.ls(sl=True)
        for seq,obj in enumerate(objs):
            if obj != objs[0]:
                cmds.parentConstraint(objs[0],objs[seq],mo=offset)
        
    
    def skipChannel(self):
        checkList = [self.findChild(QCheckBox,"x"),self.findChild(QCheckBox,"y"),self.findChild(QCheckBox,"z")] 
        skipList = [x.objectName() for x in checkList if x.checkState() != Qt.Checked]       
        skip = 'skip=('
        for i in skipList:
            skip+='"%s",' % i            
        skip+=')'
        return skip
    
    def pointconstraint(self):
        skip = self.skipChannel()
        
        offset = False
        if self.offsetCheckBox.checkState() == Qt.Checked:
            offset = True            
        objs = cmds.ls(sl=True)        
        for seq,obj in enumerate(objs):
            if obj != objs [0]:
                exec(u'cmds.pointConstraint(objs[0],objs[seq],mo=offset,%s)' % skip)
    
    def orientconstraint(self):
        skip = self.skipChannel()
        
        offset = False
        if self.offsetCheckBox.checkState() == Qt.Checked:
            offset = True   
        objs = cmds.ls(sl=True)            
        for seq,obj in enumerate(objs):
            if obj != objs [0]:
                exec(u'cmds.orientConstraint(objs[0],objs[seq],mo=offset,%s)' % skip)
        
    def scaleconstraint(self):
        skip = self.skipChannel()
        
        offset = False
        if self.offsetCheckBox.checkState() == Qt.Checked:
            offset = True 
        objs = cmds.ls(sl=True)              
        for seq,obj in enumerate(objs):
            if obj != objs [0]:
                exec(u'cmds.scaleConstraint(objs[0],objs[seq],mo=offset,%s)' % skip)
        
    def setConnectBox(self):
        mainLayout = QVBoxLayout()
        self.connectBox.setLayout(mainLayout)
        topLayout   = QHBoxLayout()

        srcLayout = QVBoxLayout()
        trgLayout = QVBoxLayout()

        srcWidget = QListWidget()
        srcWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        srcWidget.setFocusPolicy(Qt.NoFocus)
        trgWidget = QListWidget()
        trgWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        trgWidget.setFocusPolicy(Qt.NoFocus)

        srcBtnLayout = QHBoxLayout()
        trgBtnLayout = QHBoxLayout()

        srcAddBtn = QPushButton('Add Source')
        srcRemBtn = QPushButton('Remove Source')
        srcClsBtn = QPushButton('Clear')

        srcLayout.addWidget(srcWidget)
        srcLayout.addLayout(srcBtnLayout)
        srcBtnLayout.addWidget(srcAddBtn)
        srcBtnLayout.addWidget(srcRemBtn)
        srcBtnLayout.addWidget(srcClsBtn)

        trgAddBtn = QPushButton('Add Target')
        trgRemBtn = QPushButton('Remove Target')
        trgClsBtn = QPushButton('Clear')

        trgLayout.addWidget(trgWidget)
        trgLayout.addLayout(trgBtnLayout)
        trgBtnLayout.addWidget(trgAddBtn)
        trgBtnLayout.addWidget(trgRemBtn)
        trgBtnLayout.addWidget(trgClsBtn)

        topLayout.addLayout(srcLayout)
        topLayout.addLayout(trgLayout)

        drivenConnectBtn = QPushButton('SetDrivenKey==>')
        connectBtn = QPushButton('<==Connect==>')

        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(connectBtn)
        mainLayout.addWidget(drivenConnectBtn)


        srcAddBtn.clicked.connect(lambda:(srcWidget.addItems(getObjAttrs())))
        srcRemBtn.clicked.connect(lambda:(removeItems(srcWidget)))
        srcClsBtn.clicked.connect(lambda:srcWidget.clear())    

        trgAddBtn.clicked.connect(lambda:(trgWidget.addItems(getObjAttrs())))
        trgRemBtn.clicked.connect(lambda:(removeItems(trgWidget)))
        trgClsBtn.clicked.connect(lambda:trgWidget.clear())
        
        connectBtn.clicked.connect(lambda:connectAttrs(srcWidget.selectedItems()[0].text(),[i.text() for i in trgWidget.selectedItems()]))
        drivenConnectBtn.clicked.connect(lambda:setDrivenKey(srcWidget.selectedItems()[0].text(),[i.text() for i in trgWidget.selectedItems()]))
    def aimconstraint(self):
        skip = self.skipChannel()
        if self.offsetCheckBox.checkState() == Qt.Checked:
            offset = True            
        objs = cmds.ls(sl=True)
        for seq,obj in enumerate(objs):
            if obj != objs [0]:
                exec(u'cmds.aimConstraint(objs[0],objs[seq],mo=offset,%s)' % skip)
            
    def resizeEvent(self,event):        
        self.setting.setValue("size",self.size())
    
    def moveEvent(self,event):
        self.setting.setValue("pos",self.pos())   

class utilBtn(QPushButton):
    def __init__(self,name=None,module=None):
        QPushButton.__init__(self)
        self.name = name
        self.module = module
        self.clicked.connect(self.push)

    def push(self):
        module = __import__(self.module)
        reload(module)
        if not module:
            print('No module %s' % module)
            return 
        module.main()

def setDrivenKey(driver,drivens):
    for dri in drivens:
        cmds.setDrivenKeyframe(dri,currentDriver=driver)  

def connectAttrs(srcAttr,trgAttrs):
    for trgAttr in trgAttrs:        
        cmds.connectAttr(srcAttr,trgAttr,f=True)

def removeItems(listWidget):      #Remove items from QListWidget
        indexes = listWidget.selectedIndexes()
        indexLst = sorted([index.row() for index in indexes],reverse=True)
        for i in indexLst:
            listWidget.takeItem(i) 

def getObjAttrs(): # Get attributes from channelBox

    objs = cmds.ls(sl=True)
    attrs = mel.eval('channelBox -q -selectedMainAttributes mainChannelBox;')
    
    if not attrs:
        try:
            attrs = mel.eval('channelBox -q -sha mainChannelBox;')
        except:
            return
    attrFullNames = []
    for obj in objs:
        for attr in attrs:
            attrFullNames.append('%s.%s' % (obj,attr))
            
    return attrFullNames

def constraintLoc(src,*trgs):
    '''
    Add contraint target parent
    ex:
        parent          -       child
        
        src             -       src locator
        
        src locator     -       trg locator
        
        trg locator     -       trg        
    '''
    srcLoc = '%s_loc' % src
    if not cmds.objExists('%s_loc' % src):
        srcLoc = cmds.spaceLocator(name='%s_loc' % src)[0]      
        cmds.select([srcLoc,src],r=True)
        cmds.MatchTransform()
    trgLocs = []
    for trg in trgs:
        trgLoc = cmds.spaceLocator(name='%s_loc' % trg)[0]
        cmds.parent(trgLoc,srcLoc)
        cmds.select([trgLoc,trg],r=True)
        cmds.MatchTransform()
        trgLocs.append(trgLoc)
    
    return srcLoc,trgLocs
    

def selPolyMesh(typ=None):  
    '''
    Set typ return poly,curve,joint,etc... type object
    typ ex:
            polygon     = mesh
            curve       = nurbsCurve
            joint       = joint
            constraint  = parentConstraint,pointConstraint,orientConstraint,scaleConstraint,constraint
            locator     = locator
            
    '''
    sel = cmds.ls(long=True, sl=True)   
    tops = list()
    for obj in sel:
        short = cmds.ls(obj, shortNames=True)[0]        
        hier = obj.split('|')       
        if not ':' in short:
            if len(hier) > 1:
                tops.append(hier[1])
            else:
                tops.append(obj)
            continue                    
        namespace1 = short.partition(':')[0]
        namespace1 +=':'
        for each in hier:
            if namespace1 in each:
                tops.append(each)
                break       
    if not tops:
        return
    
    if typ == 'joint':
        nodes = cmds.listRelatives(tops, pa=True, type='joint', ad=True)  
            
        if not nodes:
            return            
        cmds.select(nodes,r=True) 
    
    elif typ == 'constraint':
        nodes = cmds.listRelatives(tops, pa=True, type='constraint', ad=True)  
            
        if not nodes:
            return            
        cmds.select(nodes,r=True) 
    
    elif typ == 'hide':
        nodes = cmds.listRelatives(tops, pa=True, type='transform', ad=True)  
        hideObjs = [i for i in nodes if cmds.getAttr('%s.v' % i) == 0]   
        if not hideObjs:
            return
        cmds.select(hideObjs,r=True) 
         
    elif typ == 'animNode':
        nodes =   cmds.listRelatives(tops, pa=True, type='transform', ad=True)  
        
        cmds.select(cl=True)
        for node in nodes: 
            if not cmds.listConnections(node) :
                continue
            [cmds.select(i,add=True) for i in cmds.listConnections(node) if 'animCurve' in cmds.objectType(i)]
                                
    else:        
        nodes = cmds.listRelatives(tops, pa=True, type=typ, ad=True)        
        if not nodes:
            return        
        polyMeshes = [cmds.listRelatives(i,p=True)[0] for i in nodes]
        if polyMeshes:
            cmds.select(polyMeshes,r=True)           
    
def selkeyedobjs():
        
    sel = cmds.ls(long=True, sl=True)    
    tops = list()
    for obj in sel:
        short = cmds.ls(obj, shortNames=True)[0]        
        hier = obj.split('|')
        
        if not ':' in short:
            if len(hier) > 1:
                tops.append(hier[1])
            else:
                tops.append(obj)
            continue
                    
        namespace1 = short.partition(':')[0]
        namespace1 +=':'
        for each in hier:
            if namespace1 in each:
                tops.append(each)
                break
        
    if not tops:
        return
    
    nodes = cmds.listRelatives(tops, pa=True, type='transform', ad=True)
    if not nodes:
        return
    
    keyed = list()
    
    for node in nodes:
      
        if cmds.keyframe(node, time=(':',), query=True, keyframeCount=True):
            keyed.append(node)
    
    if keyed:
        cmds.select(keyed, replace=True)
# def setEnv():
#     print(os.environ['XBMLANGPATH'])  
#     print(ICON_PATH)  
#     if not ICON_PATH in os.environ['XBMLANGPATH']:
#         os.environ['XBMLANGPATH'] += ';%s' % ICON_PATH
#         print(ICON_PATH,'was add')
def main():

    if cmds.window('ZT_Toolbox',ex=True):
        cmds.deleteUI('ZT_Toolbox')    
    win = toolBox() 
    win.setObjectName('ZT_Toolbox')        
    win.show()
