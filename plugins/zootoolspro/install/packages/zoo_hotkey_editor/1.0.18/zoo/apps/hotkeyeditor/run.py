# maintain the instance of the ui
from zoo.apps.hotkeyeditor import hotkeyeditorui
from zoo.libs.maya.qt import mayaui

def launch():
    """Load the artist GUI for hive.

    :return:
    :rtype: :class:`toolsetui.ToolsetsUI`
    """
    toolsetUi = hotkeyeditorui.HotkeyEditorUI()

    return toolsetUi


def scriptEditorLaunch():
    from zoo.apps.toolpalette import run

    a = run.show()
    toolDef = a.loadPlugin("HotkeyEditorUi")._execute()
