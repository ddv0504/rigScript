# maintain the instance of the ui
from zoo.apps.preferencesui import preferencesui


def launch():
    """Load the artist GUI for hive.

    :return:
    :rtype: :class:`toolsetui.ToolsetsUI`
    """
    prefui = preferencesui.PreferencesUI()
    return prefui


def scriptEditorLaunch():
    from zoo.apps.toolpalette import run
    a = run.show()
    return a.executePluginById("zoo.preferencesui")

