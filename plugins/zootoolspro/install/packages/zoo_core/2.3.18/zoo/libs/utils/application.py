from zoo.core.util import env


def quit():
    if env.isInMaya():
        from maya import cmds
        cmds.quit()
    elif env.isInBlender():
        print("TODO: Quit Blender")


def mainWindow():
    if env.isInMaya():
        from zoo.libs.maya.qt import mayaui
        return mayaui.getMayaWindow()
    elif env.isInBlender():
        return None