import maya.OpenMayaUI as omui
import maya.cmds as cmds
try:
    import PySide2
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtUiTools import *
    import shiboken2

except:

    import PySide
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtUiTools import *
    import shiboken
    
def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    try:
        mWindow= shiboken.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow)             
    return mWindow

   
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
        
        self.utilBox = QGroupBox(self.mainWidget)
        self.utilBox.setTitle("Utils")       
        self.utilLayout  = QVBoxLayout()
        self.utilBox.setLayout(self.utilLayout)
        
        self.mainLayout.addWidget(self.selBox)
        self.mainLayout.addWidget(self.consBox)
        self.mainLayout.addWidget(self.keyBox)
        self.mainLayout.addWidget(self.utilBox)
        self.addSelection()
        self.addConstraint()
        self.addKeyframe()
        
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
        
    
    def aimconstraint(self):
        skip = self.skipChannel()
        
        offset = False
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
        animCurves = []
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

def main():
    if cmds.window('Toolbox',ex=True):
        cmds.deleteUI('Toolbox')
    
    win = toolBox()         
    print("win:",win.objectName())
    
    win.show()
