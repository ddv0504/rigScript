import sys
import os
import regUtil
reload(regUtil)
path = os.path.dirname(__file__)
if not path in sys.path:
    sys.path.append(path)

def addEnv(envKey,oldEnvLst,newEnvLst):
    if not newEnvLst:
        return
    else:
        newEnvLst = [i.replace('/','\\') for i in newEnvLst]
    for env in newEnvLst:
        oldEnvLst.append(env)
        
    regUtil.setEnv(envKey,';')
    pass
def onMayaDroppedPythonFile(*args):
    scriptPath = regUtil.getEnv('MAYA_SCRIPT_PATH')
    pythonPath = regUtil.getEnv('PYTHONPATH')
    iconPath   = regUtil.getEnv('XBMLANGPATH')
    pluginPath = regUtil.getEnv('MAYA_PLUGIN_PATH')
    
    #Check script path
    if scriptPath:
        oldScriptPath = scriptPath.split(';')
    
    #Check python path
    if pythonPath:
        oldPythonPath = pythonPath.split(';')
    
    #Check icon path 
    if iconPath:
        oldIconPath = iconPath.split(';')

    #Check plugin path
    if pluginPath:
        oldPluginPath = pluginPath.split(';')    
    
    
    
    # with open('%s/PYTHONPATH.txt' % path,'r') as f:
    #     pythonPath = f.readlines()
    # with open('%s/MAYASCRIPTPATH.txt' % path,'r') as f:
    #     scriptPath = f.readlines()
    
    # os.system('setx PYTHONPATH %s' % pythonPath[0])
    # os.system('setx MAYA_SCRIPT_PATH %s' % scriptPath[0])
if __name__ == '__main__':
    onMayaDroppedPythonFile()