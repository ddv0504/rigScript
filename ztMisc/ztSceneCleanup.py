#-*- coding:utf-8 -*-
import os
import maya.cmds as cmds
import maya.mel as mel
import datetime
from stat import S_IWUSR, S_IREAD
import fnmatch

class issueReporter(object):
    def __init__(self):
        self.filePath = None
    def logFile(self,filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.filePath = filename

def reportIssue(msgString,logFile=None):
    issueObject = issueReporter()
    issueObject.logFile('%s/MayaVaccineLog.txt' % os.getenv('TEMP'))
    # if os.path.exists(logFile):
    #     issueObject.logFile(logFile)
    if issueObject.filePath:
        with open(issueObject.filePath,'a') as f:
            f.write('%s\r\n' % msgString)
def test_ConcreteScriptFiles():
    '''
    test if the userSetup.mel has been created, or appended by the malware
    '''
    prefs = os.path.dirname(os.path.dirname(cmds.about(env=True)))
    usersetups = []
    malType = 0
    status = ''
    testedFilePath = os.path.normpath(os.path.join(prefs, 'scripts', 'userSetup.mel'))
    if os.path.exists(testedFilePath):
        f = open(testedFilePath, "r")
        data = f.read()
        if 'fuck_All_U' in data:
            status = 'compromised'
            reportIssue('userSetup.mel : Compromised by Malware!')
        if all([len(data) >= 4118,
                '// Maya Mel UI Configuration File.Maya Mel UI Configuration File..\n// \n//\n//  This script is machine generated.  Edit at your own risk' in data,
                'string $chengxu' in data]):
            reportIssue('userSetup.mel : Infected by Malware!')
            status = 'rename'
            usersetups.append(testedFilePath)
            malType = 1

    testedFilePath = os.path.normpath(os.path.join(prefs, 'scripts', 'userSetup.py'))
    if os.path.exists(testedFilePath):
        f = open(testedFilePath, "r")
        data = f.read()
        if "cmds.evalDeferred(\'leukocyte = vaccine.phage()\')" in data and "cmds.evalDeferred(\'leukocyte.occupation()\')" in data:
            reportIssue('userSetup.py : Infected by Malware!')
            status = 'rename'
            usersetups.append(testedFilePath)
            malType += 2

    testedFilePath = os.path.normpath(os.path.join(prefs, 'scripts', 'vaccine.py'))
    if os.path.exists(testedFilePath):
        f = open(testedFilePath, "r")
        data = f.read()
        if "petri_dish_path = cmds.internalVar(userAppDir=True) + 'scripts/userSetup.py" in data:
            reportIssue('vaccine.py found : Infected by Malware!')
            status = 'rename'
            usersetups.append(testedFilePath)

    return usersetups, status, malType
def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def fix_userSetup():
    issueFound = 0
    issueFixed = 0
    usersetups, status, malwareType = test_ConcreteScriptFiles()
    if status == 'rename':
        if usersetups:
            for usersetup in usersetups:
                # we still want to know of this for fail report
                issueFound += 1
                #
                os.chmod(usersetup, S_IWUSR | S_IREAD)
                try:
                    pyCache = os.path.join(os.path.dirname(usersetup),'__pycache__')
                    if os.path.exists(pyCache):
                        findvaccine = find('vaccine*', pyCache)
                        for vacPath in findvaccine:
                            os.remove(vacPath)
                            reportIssue('Pyc vaccine file : %s has deleted' % vacPath)
                    if os.path.exists(usersetup + '.INFECTED') == True:
                        os.remove(usersetup + '.INFECTED')
                        reportIssue('Previous infected file : %s has deleted' % usersetup + '.INFECTED')
                    os.rename(usersetup, usersetup + '.INFECTED')
                    issueFixed += 1
                    reportIssue('Renamed : %s' % usersetup)
                except:
                    reportIssue("Can't rename %s file" % usersetup)

    return issueFound, issueFixed, malwareType

def test_scriptNodes():
    '''
    test for the known scriptNode with specific data
    '''
    malware_scripts = []
    for script in cmds.ls(type='script'):
        if 'MayaMelUIConfigurationFile' in script.split('|')[-1].split(':')[-1]:
            scriptdata = cmds.scriptNode(script, bs=True, q=True)
            if 'This script is machine generated.  Edit at your own risk' in scriptdata and 'fuck_All_U' in scriptdata:
                malware_scripts.append(script)
                reportIssue('scriptNode present : %s' % script)
        if 'vaccine_gene' in script or 'breed_gene' in script:
            malware_scripts.append(script)
            reportIssue('scriptNode present : %s' % script)
    return malware_scripts

def test_scriptJob():
    '''
    test for the scriptJob this Malware geenerates
    '''
    scriptjob_id = []
    try:
        a = -1
        if (mel.eval('whatIs "$autoUpdateAttrEd_aoto_int"') != "Unknown"):
            a = int(mel.eval('$temp=$autoUpdateAttrEd_aoto_int'))
        for jobStr in cmds.scriptJob(listJobs=True):
            if jobStr.startswith(str(a)) == True:
                scriptjob_id.append(a)
                reportIssue('Malware 1: scriptJob present : %s' % a)
            # find Malware 2
            if 'leukocyte.antivirus()' in jobStr:
                foundId = jobStr.split(":")[0]
                if foundId.isdigit():
                    scriptjob_id.append(int(foundId))
                    reportIssue('Malware : scriptJob present : %s' % foundId)
    except:
        pass
        #reportIssue('scriptjob not found')
    return scriptjob_id


def fix_scriptNodes():
    issueFound = 0
    issueFixed = 0
    if test_scriptNodes():
        for script in test_scriptNodes():
            cmds.delete(script)
            reportIssue('Removed : scriptNode: %s' % script)
            issueFixed += 1
            issueFound += 1
    else:
        reportIssue('scriptNode not found')
    return issueFound, issueFixed
def fix_scriptJob():
    issueFound = 0
    issueFixed = 0
    ids = test_scriptJob()
    if ids:
        for foundId in ids:
            cmds.scriptJob(kill=foundId, force=True)
            reportIssue('Removed : scriptJob ID: %s' % str(foundId))
            issueFixed += 1
            issueFound += 1
    else:
        reportIssue('scriptJob not found')
    return issueFound, issueFixed

def getUnknownPlugins():
    lst = cmds.unknownPlugin(q=1,list=1)
    return lst

def removeUnknownPlugins( name):
    rst = cmds.unknownPlugin(name, remove=1 )
    print('remove unknown plug-in : %s'%name)

def removeAllUnknownPlugins():
    lst = getUnknownPlugins()
    if lst:
        for l in lst:
            try:
                removeUnknownPlugins(l)
                reportIssue('Unknown plugin removed: %s' % l)
            except:
                print('failed to remove: %s'%l)
    else:
        print('# no Unknown Plugin')
        reportIssue('no Unknown Plugin')

def getUnknowTypeNode():
    return cmds.ls(type='unknown')

def removeUnknownTypeNode():
    _list = getUnknowTypeNode()
    if _list:
        cmds.delete(_list)
        print('delete %s unknownTypeNode '% len(_list))
        print('delete %s' % _list)
        reportIssue('delete %s unknownTypeNode '% len(_list))
    else:
        print('# no UnknownType Node')
        reportIssue('no UnknownType Plugin')


def removeAll(arg=None):
    removeAllUnknownPlugins()
    removeUnknownTypeNode()

def cleanUp(arg=None):
    fileName = cmds.file(sn=1,q=1)
    s = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    msg = 'Check issue file: {0} -- {1}'.format(fileName,s)
    reportIssue(msg)
    fix_userSetup()
    fix_scriptJob()
    fix_scriptNodes()
    removeAll()


