import os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
import shiboken2
from imp import reload
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin  
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
from zooPyMaya.mayaDecorators import d_unifyUndo
from ztRigUtils import ztRigUtil
reload(ztRigUtil)



currentPath = os.path.dirname(__file__).replace('\\','/')
shelfPath = '%s/shelves' % currentPath

def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        
    try:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(int(mayaMainWindowPtr), QMainWindow) 
            
    return mWindow     
mainWindow = maya_main_window()    
class rigWindow(MayaQWidgetDockableMixin, QMainWindow):

    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent=None)
    
        self.resize(480,820)
        self.mainUI()
        self.addMenu()
        
    def mainUI(self):
        self.mainWidget = QWidget(self)
        mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(mainLayout)      
        displayBox = QToolBox()        
        mainLayout.addWidget(displayBox)
        self.jntWidget = QGroupBox('Joint Operation')          
        self.jntOperationLayout = QHBoxLayout() 
        self.jntWidget.setLayout(self.jntOperationLayout)

        # Joint on Curve Layout
        jntOnCurveLayout = QVBoxLayout()
        # joint on curve label
        jntOnCurveLabel = QLabel('Joint on Curve')
        jntOnCurveLayout.addWidget(jntOnCurveLabel)
        jntOnCurveNameLayout = QHBoxLayout()
        # joint on curve name label
        jntOnCurveNameLabel = QLabel('Name:')
        jntOnCurveNameLayout.addWidget(jntOnCurveNameLabel)
        # joint on curve name line edit
        self.jntOnCurveNameLineEdit = QLineEdit()
        jntOnCurveNameLayout.addWidget(self.jntOnCurveNameLineEdit)
        jntOnCurveLayout.addLayout(jntOnCurveNameLayout)
        # joint name padding label
        jntOnCurvePaddingLabel = QLabel('Padding:')
        jntOnCurveNameLayout.addWidget(jntOnCurvePaddingLabel)
        # jntOnCurvePaddingLayout = QHBoxLayout()
        # joint on curve padding line edit
        self.jntOnCurvePaddingLineEdit = QLineEdit('0')
        jntOnCurveNameLayout.addWidget(self.jntOnCurvePaddingLineEdit)
        # jntOnCurveName suffix label
        jntOnCurveSuffixLabel = QLabel('Suffix:')
        jntOnCurveNameLayout.addWidget(jntOnCurveSuffixLabel)
        # joint on curve suffix line edit
        self.jntOnCurveSuffixLineEdit = QLineEdit('_jnt')
        jntOnCurveNameLayout.addWidget(self.jntOnCurveSuffixLineEdit)
        jntOnCurveLayout.addLayout(jntOnCurveNameLayout)
        # joint on curve suffix group name label
        jntOnCurveSuffixGrpNameLabel = QLabel('Group Name:')
        jntOnCurveNameLayout.addWidget(jntOnCurveSuffixGrpNameLabel)
        # joint on curve suffix group name line edit
        self.jntOnCurveSuffixGrpNameLineEdit = QLineEdit('_grp')
        jntOnCurveNameLayout.addWidget(self.jntOnCurveSuffixGrpNameLineEdit)
        jntOnCurveLayout.addLayout(jntOnCurveNameLayout)

        # joint on curve connect checkbox
        self.jntOnCurveConnectCheckBox = QCheckBox('Connect')
        jntOnCurveLayout.addWidget(self.jntOnCurveConnectCheckBox)
        
        # joint on curve button
        self.jntOnCurveBtn = QPushButton('Create')
        # jntOnCurveBtn.clicked.connect(ztRigUtil.jointOnCurve)
        jntOnCurveLayout.addWidget(self.jntOnCurveBtn)
        mainLayout.addLayout(jntOnCurveLayout)

        # Point on Curve Layout
        pointOnCurveLayout = QHBoxLayout()
        # point on curve 
        pointOnCurveLabel = QLabel('Point on Curve')
        pointOnCurveLayout.addWidget(pointOnCurveLabel)
        # point on curve Button
        self.pointOnCurveBtn = QPushButton('Create')
        self.pointOnCurveBtn.setToolTip('Select the objects you want to attach to the curve, then select the curve.')
        pointOnCurveLayout.addWidget(self.pointOnCurveBtn)
        mainLayout.addLayout(pointOnCurveLayout)
        
        mainLayout.addSpacerItem(QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding))

        self.grpWidget = QGroupBox('Group Operation')
        self.grpOperationLayout = QHBoxLayout()
        self.grpWidget.setLayout(self.grpOperationLayout)
        
        for f in [ '%s/%s.mel' % (shelfPath,i) for i in ['ztRigDisplay','ztRigEditModel','ztRigBuild','ztRigDeformation','ztRigExtraTools']]:
            name = os.path.splitext(os.path.basename(f))[0]
            shelf = mayaShelfWidget(name=name,path = f)
            displayBox.addItem(shelf,name)
        self.setCentralWidget(self.mainWidget)
        mainLayout.addWidget(self.jntWidget)
        mainLayout.addWidget(self.grpWidget)
        #mainLayout.addLayout(self.jntOperationLayout)
        
        self.customButton()
        
    def addMenu(self):
        menubar = self.menuBar()
        fileMenu = QMenu('File',self)
        saveAct = QAction('Save',self)
        fileMenu.addAction(saveAct)
        menubar.addMenu(fileMenu)

        saveAct.triggered.connect(self.saveShelf)
    def saveShelf(self):
        for f in [ '%s/%s' % (shelfPath,i) for i in os.listdir(shelfPath)]:
            name = os.path.basename(os.path.splitext(f)[0])
            if 'ztAnimation' in name:
                continue
            print(name,os.path.splitext(f)[0])
            cmds.saveShelf(name,os.path.splitext(f)[0])
            print('%s was Saved' % name)
    def customButton(self):
        #### Joint operation ####
        displayJntOrientBtn = QPushButton('Display joint orient')
        displayJntOrientBtn.clicked.connect(lambda:[ztRigUtil.displayJointOrient(i) for i in cmds.ls(sl=True) if cmds.objectType(i) == 'joint'])
        self.jntOperationLayout.addWidget(displayJntOrientBtn)
        
        hideJntOrientBtn = QPushButton('Hide joint orient')
        hideJntOrientBtn.clicked.connect(lambda:[ztRigUtil.hideJointOrient(i) for i in cmds.ls(sl=True) if cmds.objectType(i) == 'joint'])
        self.jntOperationLayout.addWidget(hideJntOrientBtn)
        
        jntRotToOrientBtn = QPushButton('Joint rotation to orient')
        jntRotToOrientBtn.clicked.connect(lambda:[ztRigUtil.rotToOrient(i) for i in cmds.ls(sl=True) if cmds.objectType(i) == 'joint'])
        self.jntOperationLayout.addWidget(jntRotToOrientBtn)
        
        #### Group operation ####
        addOffsetBtn = QPushButton('Add offset group')
        
        self.grpOperationLayout.addWidget(addOffsetBtn)
        
        addOffsetWidget = QWidget()
        radioBtnGrp = QButtonGroup(addOffsetWidget)
        defaultCheckBox = QRadioButton('Default')
        defaultCheckBox.setChecked(True)
        customCheckBox = QRadioButton('Custom')
        suffixLabel = QLabel('Suffix:')
        suffixLineEdit = QLineEdit('_')
        suffixLineEdit.setEnabled(False)
        
        radioBtnGrp.addButton(defaultCheckBox)
        radioBtnGrp.addButton(customCheckBox)
        self.grpOperationLayout.addWidget(addOffsetWidget)
        self.grpOperationLayout.addWidget(defaultCheckBox)
        self.grpOperationLayout.addWidget(customCheckBox)
        
        self.grpOperationLayout.addWidget(suffixLabel)
        self.grpOperationLayout.addWidget(suffixLineEdit)
        radioBtnGrp.buttonClicked.connect(lambda:self.offsetGroupSwitch(defaultCheckBox,suffixLineEdit))
        addOffsetBtn.clicked.connect(lambda:self.addOffsetGroup(radioBtnGrp,suffixLineEdit))        

        self.jntOnCurveBtn.clicked.connect(lambda:ztRigUtil.createJntOnCurve(self.jntOnCurveNameLineEdit.text(),int(self.jntOnCurvePaddingLineEdit.text()),self.jntOnCurveSuffixLineEdit.text(),self.jntOnCurveSuffixGrpNameLineEdit.text(),self.jntOnCurveConnectCheckBox.isChecked()))
        self.pointOnCurveBtn.clicked.connect(lambda:ztRigUtil.createPointOnCurveInfo(cmds.ls(sl=True)[-1],cmds.ls(sl=True)[0:-1]))

    def rotToOrient(self):
        cmds.undoInfo(ock=True)
        for jnt in cmds.ls(sl=True):
            if cmds.objectType(jnt) == 'joint':
                ztRigUtil.rotToOrient(jnt)
        cmds.undoInfo(cck=True)
    def addOffsetGroup(self,btnGroup,lineEdit=None):
        objs = cmds.ls(sl=True)
        btn = [i for i in btnGroup.buttons() if i.isChecked()][0]
        cmds.undoInfo(ock=True)
        if btn.text() == 'Default':
            for obj in objs:
                ztRigUtil.addOffsetGroup(obj)
        elif btn.text() == 'Custom':
            suffix = lineEdit.text()
            for obj in objs:
                ztRigUtil.addOffsetGroup(obj,'%s%s' % (obj,suffix))
        cmds.undoInfo(cck=True)
    def offsetGroupSwitch(self,checkBox,lineEdit):
        
        if checkBox.text() == 'Default':
            if checkBox.isChecked():
                lineEdit.setEnabled(False)
            else:
                lineEdit.setEnabled(True)   
class listItem(QStandardItem):
    def __init__(self,name=None,image=None,cmd=None):
        QStandardItem.__init__(self)
        self.name=name
        self.cmd=cmd
        self.setText(self.name)
        
        self.setIcon(QIcon(':{0}'.format(image)))
        self.setToolTip(image)
        
    
    def excute(self):        
        if self.cmd:
            try:
                mel.eval(self.cmd)                
            except Exception as e:
                
                print(e)     
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
        try:   
            ptr = omui.MQtUtil_findControl(shelfLayout)
        except Exception as e:
            ptr = omui.MQtUtil.findControl(shelfLayout)
        try:   
            return shiboken2.wrapInstance(long(ptr),QWidget)  
        except:
            return shiboken2.wrapInstance(int(ptr),QWidget)    
def main():
        
    title = 'ZT_RIGTools'
    if cmds.window(title, exists =True):
        cmds.deleteUI(title, wnd =True)
    win = rigWindow(maya_main_window())
    win.setObjectName(title)
    win.setWindowTitle(title)
    win.show() 