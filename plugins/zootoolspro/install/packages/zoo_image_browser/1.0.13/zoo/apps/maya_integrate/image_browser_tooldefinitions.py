from maya import cmds
from zoo.apps.toolpalette import palette
from zoo.libs.command import executor


class ImageBrowserUi(palette.ToolDefinition):
    id = "zoo.browserui"
    creator = "Keen Foong"
    tags = ["image", "browser", "ui"]
    uiData = {"icon": "menu_cube",
              "tooltip": "Image Browser",
              "label": "Image Browser",
              "color": "",
              "backgroundColor": "",
              "multipleTools": False,
              "dock": {"dockable": True, "tabToControl": ("AttributeEditor", -1), "floating": False}
              }

    def execute(self, *args, **kwargs):
        from zoo.apps.imagebrowserui import run
        return run.launch()

    def setStyleSheet(self, style):
        for t in self.tools:
            t.setStyleSheet(style)

    def toolClosed(self, tool):
        """ Clean up after tool has closed

        :param tool:
        :return:
        """
        self.tools.remove(tool)

    def teardown(self):
        for t in self.tools:
            if t:
                try:
                    t.close()
                except RuntimeError:
                    pass

        self.tools = []
