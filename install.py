import sys
import os
from imp import reload
import regUtil
reload(regUtil)
path = os.path.dirname(__file__)
    
if not path in sys.path:
    sys.path.append(path)

def addEnv(envKey,newEnvLst):
    if not newEnvLst:
        return
    else:
        newEnvLst = [i.replace('/','\\') for i in newEnvLst]
            
    regUtil.setEnv(envKey,';'.join(newEnvLst))
    

def onMayaDroppedPythonFile(*args):
    
    scriptPath = regUtil.getEnv('MAYA_SCRIPT_PATH')
    pythonPath = regUtil.getPythonPath('PYTHONPATH')
    scriptPathLst = []    
    #Add maya script path  
    if scriptPath: 
        [scriptPathLst.append(i) for i in scriptPath.split(';')]    
        if not '%s\\melScripts' % path.replace('/','\\') in scriptPath:            
            scriptPathLst.append('%s\\melScripts' % path)
    else:
        scriptPathLst.append('%s\\melScripts' % path)
    
    addEnv('MAYA_SCRIPT_PATH',scriptPathLst)

    #Add maya python path.
    pythonPathLst = []
    if pythonPath:            
        if not path.replace('/','\\') in pythonPath:            
            regUtil.appendPath(path)
    else:
        pythonPathLst.append(path)
    #[regUtil.appendPath(i.replace('/','\\')) for i in pythonPathLst]
    
    try:
        import maya.cmds as cmds
        import maya.mel as mel

        cmds.evalDeferred("import sys")
        cmds.evalDeferred('if not "{0}" in sys.path:\n\tsys.path.append("{0}")'.format(path))
        
        mel.eval('source "%s/melScripts/userSetup.mel"' % path.replace('\\','/'))
        
    except ImportError:
        pass
    
if __name__ == '__main__':
    onMayaDroppedPythonFile()