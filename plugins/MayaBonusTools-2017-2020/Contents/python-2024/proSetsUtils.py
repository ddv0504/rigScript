### See the file "LICENSE.txt" for the full license governing this code.
import maya.OpenMaya as om
import maya.mel as mel
import maya.cmds as cmds

import maya.app.flux.ae.api as loader

def registerTemplates():
    loader.registerTemplate('AEproSetTemplate.AEproSetTemplate', 'proSet')

def isInBatch():
    return (om.MGlobal.mayaState() == om.MGlobal.kBatch or om.MGlobal.mayaState() == om.MGlobal.kLibraryApp)

def register():
    try:
        if not isInBatch():
            setupUI()
    except Exception as e:
        raise

def deregister():
    if not isInBatch():
        tearDownUI()

# def getShelfButton():
#     children = cmds.shelfLayout('Polygons', childArray=True, q=True)

#     for c in children:
#         docTag = ''
#         docTag = cmds.shelfButton(c, dtg=True, q=True)
#         if docTag and docTag == 'ProSet/Create':
#             return c

def setupUI():
    registerTemplates()
    # if not getShelfButton():
    #     cmds.shelfButton('ProSetCreate', annotation='Create ProSet',
    #         image1='ProSet_Icon_Shelf.png', command='import proSetsAPI as psapi; psapi.createProSet()',
    #         p='Polygons', dtg='ProSet/Create', label='ProSet')

def tearDownUI():
    return
    # shelfBtn = getShelfButton()
    # if shelfBtn:
    #     fullPath = cmds.shelfButton(shelfBtn, fullPathName=True, q=True)
    #     cmds.deleteUI(fullPath)
