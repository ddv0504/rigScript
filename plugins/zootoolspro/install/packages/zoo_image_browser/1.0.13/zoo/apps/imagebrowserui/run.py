# maintain the instance of the ui
from zoo.libs.maya.qt import mayaui

from zoo.apps.imagebrowserui import imagebrowserui


def launch():
    """Load the artist GUI for hive.

    :return:
    :rtype: :class:`toolsetui.ToolsetsUI`
    """
    tool = imagebrowserui.ImageBrowserUI()
    return tool


def scriptEditorLaunch(browserType=None):
    from zoo.apps.toolpalette import run

    a = run.show()
    toolDef = a.loadPlugin("ImageBrowserUi")._execute(browserType)
