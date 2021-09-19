from zoo.apps.toolsetsui import toolsetui
from zoovendor.six import string_types
# maintain the instance of the ui

win = None


def launch(toolArgs=None):
    """Load the artist GUI for hive.

    :param toolArgs:
    :type toolArgs:
    :return:
    :rtype: :class:`toolsetui.ToolsetsUI`
    """
    global win
    try:
        win.close()
    except AttributeError:
        pass

    toolArgs = {} or toolArgs

    toolsetIds = [] or toolArgs.get("toolsetIds")
    position = toolArgs.get("position")

    toolsetUi = toolsetui.ToolsetsUI(iconColor=(231, 133, 255),
                                     hueShift=10,
                                     toolsetIds=toolsetIds, position=position)

    return toolsetUi


def openToolset(toolsetId, position=None):
    """ Opens a tool given the toolset ID name

    :param toolsetId: The name of the toolset ID eg "cleanObjects" or "createTube" etc
    :type toolsetId: string
    """

    toolOpened = toolsetui.runToolset(toolsetId, logWarning=False)
    if not toolOpened:  # then try again and this time open the toolset window first
        from zoo.apps.toolpalette import run
        a = run.show()

        toolsetIds = [toolsetId]
        ret = a.executePluginById("zoo.toolsets", toolsetIds=toolsetIds, position=position)

        return ret

