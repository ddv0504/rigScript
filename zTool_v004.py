# -*- coding: utf-8 -*-
import sys,os,random,json,subprocess,logging,shutil,threading,pprint,getpass,time,collections
from imp import reload
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from datetime import datetime
import maya.OpenMaya as OpenMaya
import maya.mel as mel
import pymel.core as pm
import textwrap
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin  
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

MAYA_VERSION = cmds.about(v=True)

#Save option data function
def saveJson(filePath,data):
    with open(filePath,'w') as f:
        json.dump(data,f,indent=4)
        
#Load option data function
def loadJson(filePath,data):
    with open(filePath,'r') as f:
        data = json.load(f)
    return data

#default optionData
#optionData has startup,shelfdata,current shelf info;
optionData  = {"shelfData":{"defaultShelf":{"icon":69},"currentIndex":0},"startUp":0}
#If have not shelfPath 'C:\Users\username\Documents\maya\scripts\zTool' directory create it
shelfPath  = '%s/%s' % (os.getenv('HOME'),'maya/scripts/zTool')
#Check option directory
#If have not option file,Create a dictionary(optionData) and save to option file(json)
optionPath    = '%s/options' % shelfPath 
optionFile    = '%s/option.json' % optionPath
if not os.path.isdir(optionPath):
    os.makedirs(optionPath)    
    saveJson(optionFile,optionData)        
elif not os.path.isfile(optionFile):    
    saveJson(optionFile,optionData)

else:
    optionData = loadJson(optionFile,optionData)
    if not optionData:
        optionData = {"shelfData":{"defaultShelf":{"icon":69},"currentIndex":0},"startUp":0}
 
#Default shelf file contents
defaultContent = u'''\
global proc defaultShelf () {
    global string $gBuffStr;
    global string $gBuffStr0;
    global string $gBuffStr1;
    
    }  
    '''
    
#PyQt base icon list
baseIcons = [
            'SP_ArrowBack',
            'SP_ArrowDown',
            'SP_ArrowForward',
            'SP_ArrowLeft',
            'SP_ArrowRight',
            'SP_ArrowUp',
            'SP_BrowserReload',
            'SP_BrowserStop',
            'SP_CommandLink',
            'SP_ComputerIcon',
            'SP_CustomBase',
            'SP_DesktopIcon',
            'SP_DialogApplyButton',
            'SP_DialogCancelButton',
            'SP_DialogCloseButton',
            'SP_DialogDiscardButton',
            'SP_DialogHelpButton',
            'SP_DialogNoButton',
            'SP_DialogOkButton',
            'SP_DialogOpenButton',
            'SP_DialogResetButton',
            'SP_DialogSaveButton',
            'SP_DialogYesButton',
            'SP_DirClosedIcon',
            'SP_DirHomeIcon',
            'SP_DirIcon',
            'SP_DirLinkIcon',
            'SP_DirOpenIcon',
            'SP_DockWidgetCloseButton',
            'SP_DriveCDIcon',
            'SP_DriveDVDIcon',
            'SP_DriveFDIcon',
            'SP_DriveHDIcon',
            'SP_DriveNetIcon',
            'SP_FileDialogBack',
            'SP_FileDialogContentsView',
            'SP_FileDialogDetailedView',
            'SP_FileDialogEnd',
            'SP_FileDialogInfoView',
            'SP_FileDialogListView',
            'SP_FileDialogNewFolder',
            'SP_FileDialogStart',
            'SP_FileDialogToParent',
            'SP_FileIcon',
            'SP_FileLinkIcon',
            'SP_MediaPause',
            'SP_MediaPlay',
            'SP_MediaSeekBackward',
            'SP_MediaSeekForward',
            'SP_MediaSkipBackward',
            'SP_MediaSkipForward',
            'SP_MediaStop',
            'SP_MediaVolume',
            'SP_MediaVolumeMuted',
            'SP_MessageBoxCritical',
            'SP_MessageBoxInformation',
            'SP_MessageBoxQuestion',
            'SP_MessageBoxWarning',
            'SP_TitleBarCloseButton',
            'SP_TitleBarContextHelpButton',
            'SP_TitleBarMaxButton',
            'SP_TitleBarMenuButton',
            'SP_TitleBarMinButton',
            'SP_TitleBarNormalButton',
            'SP_TitleBarShadeButton',
            'SP_TitleBarUnshadeButton',
            'SP_ToolBarHorizontalExtensionButton',
            'SP_ToolBarVerticalExtensionButton',
            'SP_TrashIcon',
            'SP_VistaShield'
            ]    

#The option path add to current maya version enviroment file.
envFile = '%s/maya/%s/Maya.env' %(os.getenv('HOME'),MAYA_VERSION)

def onMayaDroppedPythonFile(*args):    
    shelfTab = mel.eval('''global string $gShelfTopLevel;
                string $shelves = `tabLayout -q -selectTab $gShelfTopLevel`;''')
    cmds.shelfButton(annotation='Start zTool', label='zTool',imageOverlayLabel="ZTool",image1='commandButton.png', command='import zTool_v004\nzTool_v004.main()' ,p=shelfTab)
    path = getScriptPath()
    os.system('cmd /c "set PYTHONPATH={}"'.format(path))
    sys.path.append(path)
def getScriptPath():
    path = os.path.dirname(__file__)       
    return path

def checkEnv(envFile):    
    if not os.path.isfile(envFile):
        with open(envFile,'w') as f:
            f.write('') 
               
    lineContent = ''    
    with open(envFile,'r') as f:
        lst = f.readlines()
    pythonStr = 'PYTHONPATH'
    for l in lst:
        if not pythonStr in l:
            continue
        elif optionPath and getScriptPath() in l:
            return
        lineContent = l
    if lineContent:
        if '\r\n' in lineContent:
            newlineContent = lineContent.split('\r\n')[0]
            newLineContent = '%s;%s;%s;\r\n' % (newlineContent,optionPath,getScriptPath())
            index = lst.index(lineContent)
            lst[index] = newLineContent
            t = time.time()
            t = time.strftime("%Y%m%d")
            shutil.copy2(envFile,'%s%s.backup' %(envFile,t))
            print(t)
        with open(envFile,'w') as f:
            for l in lst:
                f.write(l)        
    else:
        print(getScriptPath())
        with open(envFile,'w') as f:
            f.write('PYTHONPATH = %s;%s;\r\n' % (optionPath,getScriptPath()) )         
checkEnv(envFile)
    
#Startup file contents
startUpFile     = '%s/maya/scripts/zTool/options/userSetup.py' % os.getenv('HOME')
startUpContents = u'''\
import maya.cmds as cmds
cmds.evalDeferred("import zTool_v004")
cmds.evalDeferred("zTool_v004.main()")
    '''

def userSetup(file):
    startUpContents = u'''\
    import maya.cmds as cmds
    cmds.evalDeferred("import zTool_v004")
    cmds.evalDeferred("zTool_v004.main()")
    '''
    if not os.path.isfile(file):
        if not os.path.isdir(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file)) 
        with open(file,'w') as f:
            f.write(textwrap.dedent(startUpContents))  
            
#Rotate icon
def rotateIcon(icon,deg):
    #QIcon convert to pixmap
    pixmap = icon.pixmap(QSize(120,120))
    #QPoint with mattrix rotation
    center = pixmap.rect().center()
    matrix = QMatrix()
    matrix.translate(center.x(),center.y())
    matrix.rotate(deg)
    pix = pixmap.transformed(matrix)
    pix = pix.scaledToWidth(50)    
    #conver pixmap to QIcon
    icon = QIcon()
    icon.addPixmap(pix)    
    return icon       

#Check shelves directory
#If have not any one shelf file,Create a default shelf file
if not os.path.isdir(shelfPath):
    os.makedirs(shelfPath)    
    with open('%s/defaultShelf.mel' % shelfPath,'w') as f:
        f.write(defaultContent)
        
elif not len(os.listdir(shelfPath))>1:
    with open('%s/defaultShelf.mel' % shelfPath,'w') as f:
        f.write(defaultContent)

#Organize optionfile contents.
if len(os.listdir(shelfPath)) > 0:
    keyList =[]
    for i in os.listdir(shelfPath):
        if os.path.splitext(i)[-1] == ".mel":
            key = os.path.splitext(os.path.basename(i))[0]
            if not key in optionData["shelfData"]:
                optionData["shelfData"].update({key:{"icon":69}})
                print("this:",key)
            keyList.append(key)  
    for key,value in optionData["shelfData"].items():
        if not key in keyList:
            if key == 'currentIndex':
                continue
            optionData["shelfData"].pop(key)  
             
    saveJson(optionFile,optionData)        
#Mouse curser        
curser = QCursor()
    
#Get maya mainwindow pointer as QMainWindow
def maya_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()        
    try:
        mWindow= shiboken2.wrapInstance(long(mayaMainWindowPtr), QMainWindow) 
    except:
        mWindow= shiboken2.wrapInstance(int(mayaMainWindowPtr), QMainWindow)             
    return mWindow

#Maya main window global var
mainWindow = maya_main_window()

#Create costum button class.Use to when pressed icon rotate.
class costumButton(QPushButton):
    def __init__(self,parent=None):
        super(costumButton,self).__init__(parent)              
        self.defaultIcon()  
        self.setStyleSheet("""QPushButton{background-color:rgba(2,3,4,0);
                           border-width:2px;
                           }""")
        self.release()    
        self.pressed.connect(self.press)
        self.released.connect(self.release)
    #When this button pressed icon rotate 45 degree.  
    def press(self):       
        self.setIcon(self.icon01)        
    #when this button released icon rotate -45 degree.   
    def release(self):
        icon = rotateIcon(self.icon(),-45)
        self.setIcon(icon)
    #Set default icon. 
    def defaultIcon(self):
        self.icon01 =QApplication.style().standardIcon(getattr(QStyle,'SP_MessageBoxCritical'))
        rotateIcon(self.icon01,-45)       
        self.setIcon(self.icon01)
        self.setIconSize(QSize(40,40)) 
         
#Main window class
class zTool(MayaQWidgetDockableMixin,QWidget):     
    def __init__(self,parent=None):
        super(zTool,self).__init__(parent)
        self.shelfList = []
        self.settings = QSettings("optionData","zToolOption")
        style ='''QToolBox::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border-radius: 5px;
    color: darkgray;
}
'''  
        styleSheet = '%s\n%s\n%s' %(self.settings.value('styleSheet'),self.settings.value('font-color'),style)
        
        try:           
            self.setStyleSheet(styleSheet)
        except Exception as e:
            print("Error:",e)
        for i in os.listdir(shelfPath):
            if os.path.splitext(i)[1] == '.mel':
                self.shelfList.append(i)
        
        self.setParent(maya_main_window())
        self.setWindowTitle('zTool_V004')
        self.setObjectName('zTool_V004')
        
        self.resize(120,800)
        self.setUI()
        self.btnConnect()
    def setUI(self):
        font = QFont() 
        font.fromString(self.settings.value('bgFont'))
        
        vLayout = QVBoxLayout()
        self.setLayout(vLayout)
        formLayout = QFormLayout()
        
        self.sceneSettingBtn = QPushButton(self)
        self.sceneSettingBtn.setText('SceneSetting')
        self.sceneSettingBtn.setMinimumSize(QSize(82,0))
        self.sceneSettingBtn.setObjectName('SceneSetting')
        self.sceneSettingBtn.setFont(font)
        formLayout.setWidget(0,QFormLayout.LabelRole,self.sceneSettingBtn)
        
        self.toolBtn = QPushButton(self)
        self.toolBtn.setText('Tools')
        self.toolBtn.setMinimumSize(QSize(82,0))
        self.toolBtn.setObjectName("Tools")
        self.toolBtn.setFont(font)
        formLayout.setWidget(0,QFormLayout.FieldRole,self.toolBtn)
        
        self.controlBtn = QPushButton(self)
        self.controlBtn.setText('Controller')
        self.controlBtn.setMinimumSize(QSize(82,0))
        self.controlBtn.setObjectName('Controller')
        self.controlBtn.setFont(font)
        formLayout.setWidget(1,QFormLayout.LabelRole,self.controlBtn)
        
        self.optionBtn = QPushButton(self)
        self.optionBtn.setText('Options')
        self.optionBtn.setMinimumSize(QSize(82,0)) 
        self.optionBtn.setObjectName('Options')
        self.optionBtn.setFont(font)     
        formLayout.setWidget(1,QFormLayout.FieldRole,self.optionBtn)        
        self.plusBtn   = costumButton(self)
        self.plusBtn.setMinimumSize(QSize(40,40))
        self.plusBtn.setMaximumSize(QSize(40,40))            
        
        self.startUpCheckBox = QCheckBox("startUp",self)
        self.startUpCheckBox.setObjectName("startUp")
        self.startUpCheckBox.setText('StartUP')
        
        if loadJson(optionFile,optionData)["startUp"] == 1:
            self.startUpCheckBox.setChecked(1)
        else:
            self.startUpCheckBox.setChecked(0)
            
        vLayout.addLayout(formLayout,0)
        self.horizontalLayout = QHBoxLayout(self)
        spacerItem = QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addWidget(self.startUpCheckBox)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.plusBtn)
        self.horizontalLayout.setSpacing(2)      
        vLayout.addLayout(self.horizontalLayout,1)
        
        if self.shelfList:   
            self.toolBox = toolBox(parent=self,lst=self.shelfList)                            
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.addWidget(self.toolBox)
            vLayout.addLayout(self.verticalLayout,2)
        
    #Button connection function
    def btnConnect(self):
        self.optionBtn.clicked.connect(self.optionDialog)
        self.plusBtn.clicked.connect(self.addShelf)
        self.sceneSettingBtn.clicked.connect(self.sceneSetting)
        self.controlBtn.clicked.connect(self.addControl)
        self.toolBtn.clicked.connect(self.tools)
        self.startUpCheckBox.stateChanged.connect(self.checkStartUp)
    
    def checkStartUp(self):
        if self.startUpCheckBox.isChecked():
            optionData.update({"startUp":1})
            saveJson(optionFile,optionData)            
            if not os.path.isfile(startUpFile):                
                with open(startUpFile,'w') as f:
                    f.write(textwrap.dedent(startUpContents))
            print('%s file was created' % startUpFile)               
            print("Start up was checked.")
            
        else:
            optionData.update({"startUp":0})
            saveJson(optionFile,optionData)
            if os.path.isfile(startUpFile):                
                os.remove(startUpFile)
            print('%s file was removed' % startUpFile)
            print("Start up was unchecked.")
                
    def tools(self):
        import ztool_ToolsUI
        reload(ztool_ToolsUI)
        
        ztool_ToolsUI.main()
        
    def addShelf(self):
        if cmds.window('addShelfDialog',ex=True):
            cmds.deleteUI('addShelfDialog')
        #Creat a shelf file
        diag = dialog(name='addShelfDialog',parent=self)
        diag.setObjectName('addShelfDialog')  
        
        #diag.move(self.lastPoint)
        diag.show()         

    def optionDialog(self):
        #font = QFont(QFontDialog.getFont()[0])
        if cmds.window('optionDialog',ex=True):
            cmds.deleteUI('optionDialog')
        dialog = optionDialog(parent = self,name='optionDialog')
        dialog.move(curser.pos())
        dialog.show()
        return                
        
    def sceneSetting(self):
        #Get frame info
        startFrame=int(cmds.playbackOptions(minTime=True,query=True))
        endFrame=int(cmds.playbackOptions(maxTime=True,query=True))
        
        #Check Scene_root exist
        if	not cmds.objExists('Scene_root'):	
            #Creat a aim camera	 
            mel.eval('camera -centerOfInterest 5 -focalLength 35 -lensSqueezeRatio 1 -cameraScale 1 -horizontalFilmAperture 1.41732 -horizontalFilmOffset 0 -verticalFilmAperture 0.94488 -verticalFilmOffset 0 -filmFit Fill -overscan 1 -motionBlur 0 -shutterAngle 144 -nearClipPlane 0.1 -farClipPlane 100000 -orthographic 0 -orthographicWidth 30 -panZoomEnabled 0 -horizontalPan 0 -verticalPan 0 -zoom 1; objectMoveCommand; cameraMakeNode 2 "";')
        else:
            print('Scene_root group exist already.')
            return
        
        #Get camera,aim's name. Create root group,main group
        currentCam,aim       =   cmds.ls(sl=True)
        camGroup      =   '%s_group' % currentCam
        sceneRoot    =   cmds.spaceLocator(n='Scene_root')[0]
        sceneMain    =   cmds.spaceLocator(n='Scene_main')[0]
        
        #Set parent	
        camMain = cmds.spaceLocator(n='cam_main')[0]
        cmds.parent(sceneMain,sceneRoot)
        cmds.parent(camGroup,camMain)
        cmds.parent(camMain,sceneMain)						  
        
        #Rename current camera        
        camName = 'cam_main_%s_%s' % (startFrame,endFrame)        
        cmds.rename(currentCam,camName)        
        cmds.setAttr('%s.translateZ' % camName, 100)
        cmds.setAttr('%s.translateZ' % aim, 0)
        #Set camMain attribute
        attrList = ['rotateZ','scaleX','scaleY','scaleZ','visibility']
        for attr in attrList:
            cmds.setAttr('%s.%s' % (camMain,attr),lock=True,keyable=False)
            
        cmds.addAttr(camMain,longName='twist',at='float',r=True,w=True,k=True)
        cmds.expression(s="%s.twist=%s.twist" % (camGroup,camMain))
        camShape = 'cam_main_%s_Shape%s' % (startFrame,endFrame)
        cmds.setAttr('%s.locatorScale' % camShape,10)
        camAttrList=cmds.listAttr(camGroup,keyable=True)

        for i in camAttrList:

            cmds.setAttr('%s.%s' % (camGroup,i),keyable=False)
            
    def addControl(self):
        objs=cmds.ls(sl=True)	
        for obj in objs:
            print(obj)            
            #Create a locator and match to current object
            controlLocator = cmds.spaceLocator(n='%s_con' % obj)[0]
            tempConstraint = cmds.parentConstraint(obj,controlLocator,mo=False)
            cmds.delete(tempConstraint)
            #Get locked attribute from object
            attrList = cmds.listAttr(obj,locked=True,k=False)
            transAttrList  = []
            rotateAttrList = []
            if attrList:
                for skipAttr in attrList:
                    cmds.setAttr('%s.%s' % (controlLocator,skipAttr),l=True)
                    if 'translate' in skipAttr:
                        transAttrList.append(skipAttr[-1].lower())
                    elif 'rotate' in skipAttr:
                        rotateAttrList.append(skipAttr[-1].lower())
            
            cmds.parentConstraint(controlLocator,obj,mo=False,st=transAttrList,sr=rotateAttrList)
    
       
        
#Customize QDialog
class dialog(QDialog):
    def __init__(self,name=None,parent=None):
        super(dialog,self).__init__(parent)
        self.parent = parent
        self.name   = name
        self.setUI()
    
    def setUI(self):
        self.resize(260,50)
        self.move(curser.pos())
        self.setWindowTitle(self.name)
        self.setObjectName(self.name)
        self.layout = QVBoxLayout(self)
        self.hLayout   = QHBoxLayout()
        self.lineLabel = QLabel(self)
        self.lineLabel.setText('Shelf name:')
        self.lineEdit  = QLineEdit(self)
        self.hLayout.addWidget(self.lineLabel)
        self.hLayout.addWidget(self.lineEdit)
        self.saveBtn = QPushButton(self)
        self.saveBtn.setText('Save')
        self.saveBtn.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.layout.addLayout(self.hLayout)
        self.buttomLayout = QVBoxLayout()
        self.buttomLayout.addWidget(self.saveBtn)
        self.layout.addLayout(self.buttomLayout)

        self.saveBtn.clicked.connect(self.save)
        
    def save(self):        
        if not  self.lineEdit.text():
            return
        if self.name == 'addShelfDialog':
            shelfFileName = '%s/%s.mel' % (shelfPath,self.lineEdit.text())
            if os.path.isfile(shelfFileName):
                print('Current file exist already')
                return
            shelfContent  = defaultContent.replace('defaultShelf',self.lineEdit.text())
            optionData['shelfData'][self.lineEdit.text()]={"icon":69}         
            with open(shelfFileName,'w') as f:
                f.write(shelfContent)
            toolBox = mainWindow.findChild(QToolBox,'zToolBox')
            shelfList = []
            for i in range(toolBox.count()):
                shelfList.append(toolBox.widget(i).name)
            shelfList.append(self.lineEdit.text())
            index = sorted(shelfList).index(self.lineEdit.text())
            optionData["shelfData"].update({"currentIndex":index})
            print("OptionData was saved as ",optionFile)
            pprint.pprint(optionData)
            saveJson(optionFile,optionData)            
                 
        elif self.name == 'renameShelfDialog':
            newName = self.parent.path.replace(self.parent.name,self.lineEdit.text())
            os.rename(self.parent.path,newName)
            print('Rename as %s' % self.lineEdit.text())
            icon = optionData["shelfData"][self.parent.name]["icon"]
            optionData["shelfData"].update({self.lineEdit.text():{"icon":icon}})
            optionData["shelfData"].pop(self.parent.name)
            saveJson(optionFile,optionData)

        main()
                    
        
#Customize QToolBox                    
class toolBox(QToolBox):
    def __init__(self,parent=None,lst=[]):
        super(toolBox,self).__init__(parent)
        self.lst = lst
        self.setObjectName('zToolBox')
        self.parent=parent
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        style = self.parent.settings.value('toolBoxStyle')
           
        self.setStyleSheet(style)
        
        font  = QFont()
        font.fromString(self.parent.settings.value('shelfFont'))
        self.setFont(font)
        self.setLineWidth(2)
                        
        self.loadOption()
        self.loadIndex()
        self.currentChanged.connect(self.saveIndex)
        
    def loadOption(self):
        #Loading optionData and set the attributes
        print("optionData:")
        pprint.pprint(optionData)
        if optionData:
            if len(self.lst)>0:
                print("\nShelves list:")
                for index,i in enumerate(self.lst):
                    path  = '%s/%s' % (shelfPath,i)                    
                    i = os.path.splitext(i)[0]
                    lv = optionData['shelfData'][i]["icon"]
                    if type(lv) == int:
                        icon = QApplication.style().standardIcon(getattr(QStyle, baseIcons[lv]))  
                    else:
                        if os.path.isfile(lv):
                            icon=QIcon()
                            icon.addFile(lv)
                    self.shelfWidget = shelfWin(parent=self,name=i,path=path,index=index)
                    print('\t%s'%self.shelfWidget.name)
                    self.addItem(self.shelfWidget,icon,i)                        
                
    def saveIndex(self):
        # if not optionData:
        #     optionData =  {"shelfData":{"defaultShelf":{"icon":69},"currentIndex":0},"startUp":0}
        optionData['shelfData'].update({'currentIndex':self.currentIndex()})
        print(optionData)
        saveJson(optionFile,optionData)
        print("Set currentIndex as %s" % (self.currentIndex()+1))
        
    def loadIndex(self):
        if not optionData:
            return
        if not 'currentIndex' in optionData['shelfData']:
            optionData['shelfData']['currentIndex'] = 0
            saveJson(optionFile,optionData)
        index = optionData['shelfData']['currentIndex']
        self.setCurrentIndex(index)
        print("Current index is %s" % self.currentIndex())
             
        
def deleteControl(control):
    
    if cmds.dockControl(control,ex=True):
        cmds.deleteUI(control)
    
    elif cmds.window(control,ex=True):
        cmds.deleteUI(control)
        
class shelfWin(QWidget):
    def __init__(self,name,path='',parent=None,index=None):
        super(shelfWin,self).__init__()
        self.name = name
        self.path = path
        self.setObjectName = self.name
        self.index = index
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
        ptr = omui.MQtUtil_findControl(shelfLayout)
        try:   
            return shiboken2.wrapInstance(long(ptr),QWidget)  
        except:
            return shiboken2.wrapInstance(int(ptr),QWidget)    
            
    def contextMenuEvent(self,event):
        menu = QMenu(self)
        #Create rename Action
        renameAction = menu.addAction('Rename')
        renameAction.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogBack))
        
        #Remove current shelf Action
        removeAction = menu.addAction('Remove')
        removeAction.setIcon(QApplication.style().standardIcon(QStyle.SP_DirHomeIcon))        
        
        #Set a New Icon
        setIcon     = menu.addAction('SetIcon')
        setIcon.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogYesButton))
        
        #Save current shelf Action
        saveAction   = menu.addAction('Save')
        saveAction.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        #Save all shelf Action
        saveAllAction   = menu.addAction('SaveAll')  
        saveAllAction.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        
        action = menu.exec_(self.mapToParent(event.globalPos()))
                
        if action == renameAction:
            renameDialog = dialog(name='renameShelfDialog',parent=self)
            renameDialog.show()
            
        elif action == removeAction:
            msg=QMessageBox(self)
            msg.move(curser.pos())
            msg.setWindowTitle('warning') 
            reply = msg.warning(msg,"message","Delete current tab,\nAre you sure?",QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.StandardButton.Yes:
                os.remove(self.path)
                print('%s file was removed' % self.path)
            else:
                return    
            main()
            
        elif action == setIcon:
            if cmds.window('IconLibrary',ex=True):
                cmds.deleteUI('IconLibrary')
            self.iconWidget = iconWidget(parent=self)
            self.iconWidget.move(curser.pos())
            self.iconWidget.show()             
               
        elif action == saveAction:  
            print(self.name,os.path.splitext(self.path)[0],self.path)          
            cmds.saveShelf(self.name,os.path.splitext(self.path)[0])      
            print('Current shelf: %s was saved'%self.path)
            
        elif action == saveAllAction:
            toolBoxV    = mainWindow.findChild(QToolBox,'zToolBox')
            n=0
            while True:
                widget = toolBoxV.widget(n)
                if not widget:
                    return
                print(widget.path,n,',shelf was saved')
                cmds.saveShelf(widget.name,os.path.splitext(widget.path)[0])
                n+=1
            print('All shelf was saved') 
#Icon library dialog widget
class iconWidget(QDialog):
    def __init__(self,name='IconLibrary',parent=None):
        super(iconWidget,self).__init__(parent)
        self.name=name
        self.setWindowTitle(self.name)        
        self.setObjectName(self.name)
        self.baseLayout = QVBoxLayout(self)
        self.gridLayout = QGridLayout()
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        self.baseLayout.addLayout(self.gridLayout)        
        x=0
        n=0
        for i in baseIcons:
            if n>5:
                n=0
                x+=1            
            btn = iconButton(name=i,parent=self.parent)
            btn.setIcon(self.style().standardIcon(getattr(QStyle, i)))
            btn.lv = baseIcons.index(i)
            self.gridLayout.addWidget(btn,x,n)
            n+=1
        btn = iconButton(name='Browser',parent=self.parent)
        btn.setText('<<Select Icon From Image File>>')
        btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        self.baseLayout.addWidget(btn)
    # def closeEvent(self,e):
    #     print('closed') 
                   
class iconButton(QPushButton):
    def __init__(self,name,parent=None,lv=None):
        super(iconButton,self).__init__()
        self.name = name
        self.lv   = lv
        self.setObjectName(self.name)
        #self.setText(self.name)
        self.setToolTip(self.name)
        self.clicked.connect(self.click)
        self.setIconSize(QSize(26,26))
    def click(self):
        
        toolBoxV = mainWindow.findChild(QToolBox,'zToolBox')
        shelfWidget = self.parent().parent()
        
        if self.name == 'Browser':
            filter = 'PNG(*.png);;GIF(*.gif);;JPEG (*.jpg;*.jpeg;*.jpeg2000);;All Files (*.*)'
            imageFile = QFileDialog.getOpenFileName(filter=filter)[0]
            if not imageFile:
                return
            icon = QIcon()
            icon.addFile(imageFile)          
            self.lv = imageFile       
        toolBoxV.setItemIcon(shelfWidget.index,self.icon())  
                         
        optionData['shelfData'].update({shelfWidget.name:{"icon":self.lv}})
        pprint.pprint(optionData)
        saveJson(optionFile,optionData)          
        
#Option dialog window
class optionDialog(QDialog):
    
    def __init__(self,name=None,parent=None):
        super(optionDialog,self).__init__(parent)
        self.parent = parent
        self.name   = name
        self.setObjectName(self.name)
        self.layout = QVBoxLayout(self)
        self.resize(300,80)
            
        self.setWindowTitle(self.name)
        self.setObjectName(self.name)
        self.bgColorBtn = QPushButton(self,'Background-Color')
        self.bgColorBtn.setText('Background-Color')
        self.toolBoxFontBtn = QPushButton(self,'Shelf-Font')
        self.toolBoxFontBtn.setText('Shelf-Font')
        
        self.bgFontBtn  =  QPushButton(self,"Button-Font")
        self.bgFontBtn.setText('Button-Font')
        
        self.toolBoxBtn  = QPushButton(self,"Shelf-Background-Color")
        self.toolBoxBtn.setText("Shelf-Background-Color")
        
        self.fontColorBtn = QPushButton(self,"Font-Color")
        self.fontColorBtn.setText("Font-Color")
        
        self.layout.addWidget(self.bgColorBtn)
        self.layout.addWidget(self.toolBoxBtn)
        self.layout.addWidget(self.bgFontBtn)
        self.layout.addWidget(self.toolBoxFontBtn)
        self.layout.addWidget(self.fontColorBtn)                          
        
        self.bgColorBtn.clicked.connect(self.setBgColor)
        self.toolBoxFontBtn.clicked.connect(self.setToolBoxFont)
        self.toolBoxBtn.clicked.connect(self.setToolBox)
        self.bgFontBtn.clicked.connect(self.setBgFont)
        self.fontColorBtn.clicked.connect(self.setFontColor) 
        
    def setFontColor(self):
        color = QColor()
        color = QColorDialog(color)
        color = color.getColor()
        r,g,b,a = color.getRgbF()
        styleSheet =  "color:rgba(%s,%s,%s,%s);"%(r*255,g*255,b*255,a)
        ogStyleSheet = self.parent.settings.value('styleSheet',styleSheet)
        newStyleSheet = "%s\n%s" %(ogStyleSheet,styleSheet)
        print(newStyleSheet)         
        self.parent.setStyleSheet(newStyleSheet)
        self.parent.settings.setValue("font-color",styleSheet)
    def setBgColor(self):
        color = QColor()
        color = QColorDialog(color)
        color = color.getColor()
        r,g,b,a = color.getRgbF()
        if (r,g,b) == (0,0,0):
            return
        fontStyleSheet = self.parent.settings.value('font-color')
        styleSheet = "background-color:rgba(%s,%s,%s,%s);"%(r*255,g*255,b*255,a)
        styleSheet +='\n%s' % fontStyleSheet
        self.parent.setStyleSheet(styleSheet)
        self.parent.settings.setValue('styleSheet',styleSheet)
        self.parent.settings.setValue('rgb',(r,g,b))
        cmds.dockControl('zTool_V004',e=True,bgc=(r,g,b))
        
    def setBgFont(self):
        #Set all font
        currentFont = self.parent.parent().font()
        fontDialog = QFontDialog()
        font = fontDialog.getFont(currentFont)[0]        
        self.parent.parent().setFont(font)        
        btnList = self.parent.findChildren(QPushButton)
        for btn in btnList:
            if btn.objectName() in ['SceneSetting','Tools','Controller','Options']:
                btn.setFont(font)
                print(btn.objectName())        
        font = font.toString()       
        self.parent.settings.setValue("bgFont",font)          
            
    def setToolBoxFont(self):
        
        self.setToWidget = mainWindow.findChild(QToolBox,'zToolBox') 
        currentFont = self.setToWidget.font()        
        fontDialog = QFontDialog()
        font = fontDialog.getFont(currentFont)[0]        
        if font.toString() == currentFont.toString():
            return
        
        fontSetting = font.toString()
        self.parent.settings.setValue('shelfFont',fontSetting)
        self.setToWidget.setFont(font)        
    
    def setToolBox(self):
        #set toolBox color        
        self.setToToolBox = mainWindow.findChild(QToolBox,'zToolBox')         
        color = QColor()
        color = QColorDialog(color)
        color = color.getColor()
        r,g,b,a = color.getRgbF()
        if [r,g,b] == [0,0,0]:
            return  
        styleSheet =  "background-color:rgba(%s,%s,%s,%s);"%(r*255,g*255,b*255,a) 
        self.setToToolBox.setStyleSheet(styleSheet)      
        self.parent.settings.setValue('toolBoxStyle',styleSheet)

class toolWidget(QDialog):
    pass
    
windowList = ['zToolBox','zTool','zTool_V004']
def initial():
    if not len(os.listdir(shelfPath))>1:
        #Create a default shelf file
        with open('%s/defaultShelf.mel' % shelfPath,'w') as f:
            f.write(defaultContent)
    
    for win in windowList:
        deleteControl(win)
          
      
def main():
    initial()        
    ztWin = zTool() 
    cmds.checkBox("startUp",ex=True)
    r,g,b=(0.3,0.3,0.3)
    if ztWin.settings.value('rgb'):
        r,g,b = ztWin.settings.value('rgb')
    cmds.dockControl('zTool_V004',area='left', bgc=(float(r),float(g),float(b)),content=ztWin.objectName(),floating = False, allowedArea=['right', 'left'],w=80)


    