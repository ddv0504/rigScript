from maya import cmds
from zoo.apps.toolpalette import palette
from zoo.libs.command import executor


class TriggerStateToggle(palette.ToolDefinition):
    id = "zoo.triggers.state"
    creator = "David Sparrow"
    tags = ["triggers"]
    uiData = {"icon": "menu_reload",
              "tooltip": "Toggles the state of triggers, if off then marking menus will no longer operate",
              "label": "Trigger Toggle",
              "color": "",
              "backgroundColor": "",
              "isCheckable": True,
              "isChecked": True,
              "multipleTools": False,
              "loadOnStartup": True
              }

    def execute(self, state):
        from zoo.libs.maya.markingmenu import markingmenuoverride

        if state:
            # turn on the triggers
            markingmenuoverride.setup()
            return
        # remove the triggers
        markingmenuoverride.reset()

    def teardown(self):
        from zoo.libs.maya.markingmenu import markingmenuoverride
        # remove the triggers
        markingmenuoverride.reset()


class MayaToolTipsToggle(palette.ToolDefinition):
    id = "zoo.help.tooltips"
    creator = "Keen Foong"
    tags = ["toggle"]
    uiData = {"icon": "menu_reload",
              "tooltip": "Toggle Maya Tooltips",
              "label": "Toggle Maya Tooltips",
              "color": "",
              "backgroundColor": "",
              "isCheckable": True,
              "isChecked": True,
              "multipleTools": False,
              "loadOnStartup": True
              }

    def __init__(self, manager):
        from zoo.libs.maya.utils import tooltips
        self.uiData['isChecked'] = tooltips.tooltipState()
        super(MayaToolTipsToggle, self).__init__(manager=manager)
        self.tools = []

    def execute(self, state):
        """ Execute toggle

        :param state:
        :return:
        """
        from zoo.libs.maya.utils import tooltips
        tooltips.setMayaTooltipState(state)


class UninstallerUi(palette.ToolDefinition):
    id = "zoo.uninstaller"
    creator = "Keen Foong"
    tags = ["toggle"]
    uiData = {"icon": "trash",
              "tooltip": "Uninstall ZooToolsPro",
              "label": "Uninstall ZooToolsPro",
              "color": "",
              "backgroundColor": "",
              }


    def execute(self, *args, **kwargs):
        from zoo.apps.uninstallerui import run
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



class Reload(palette.ToolDefinition):
    id = "zoo.reload"
    creator = "David Sparrow"
    tags = ["reload"]
    uiData = {"icon": "menu_zoo_reload",
              "tooltip": "Reloads zootools by reloading the zootools.py plugin",
              "label": "Reload",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        cmds.evalDeferred('from maya import cmds;cmds.unloadPlugin("zootools.py")\ncmds.loadPlugin("zootools.py")')


class Shutdown(palette.ToolDefinition):
    id = "zoo.shutdown"
    creator = "David Sparrow"
    tags = ["menu_shutdown"]
    uiData = {"icon": "zoo_shutdown",
              "tooltip": "shutdown zootools by unloading the zootools.py plugin",
              "label": "Shutdown",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self):
        cmds.evalDeferred('from maya import cmds;cmds.unloadPlugin("zootools.py")')


class HotkeyEditorUi(palette.ToolDefinition):
    id = "zoo.hotkeyeditorui"
    creator = "Keen Foong"
    tags = ["hotkey", "hotkeys", "editor"]
    uiData = {"icon": "menu_keyboard",
              "tooltip": "Create custom hotkeys",
              "label": "Hotkey Editor",
              "color": "",
              "backgroundColor": "",
              "multipleTools": False,
              "dock": {"dockable": True, "tabToControl": ("AttributeEditor", -1), "floating": False}
              }

    def execute(self, *args, **kwargs):
        from zoo.apps.hotkeyeditor import run
        return run.launch()

    def setStyleSheet(self, style):
        for t in self.tools:
            t.setStyleSheet(style)

    def toolClosed(self, tool):
        """ Clean up after tool has closed

        :param tool:
        :return:
        """
        if tool in self.tools:
            self.tools.remove(tool)

    def teardown(self):
        for t in self.tools:
            if t:
                t.close()

        self.tools = []


class TriggersUi(palette.ToolDefinition):
    id = "zoo.triggersui"
    creator = "Dave Sparrow"
    tags = ["trigger", "triggers"]
    uiData = {"icon": "menu_rayGun",
              "tooltip": "Loads Triggers UI",
              "label": "Triggers",
              "color": "",
              "backgroundColor": "",
              "multipleTools": False,
              "dock": {"dockable": True, "tabToControl": ("AttributeEditor", -1), "floating": False}
              }

    def execute(self, *args, **kwargs):
        from zoo.apps.triggersui import run
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


class PreferencesUi(palette.ToolDefinition):
    id = "zoo.preferencesui"
    creator = "Dave Sparrow"
    tags = ["preference"]
    uiData = {"icon": "menu_zoo_preferences",
              "tooltip": "Loads the zootools preferences GUI",
              "label": "Preferences",
              "color": "",
              "backgroundColor": "",
              "multipleTools": False,
              "dock": {"dockable": True, "tabToControl": ("AttributeEditor", -1), "floating": False}
              }

    def execute(self, *args, **kwargs):
        from zoo.apps.preferencesui import run
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


class ToolsetsUi(palette.ToolDefinition):
    id = "zoo.toolsets"
    creator = "Keen Foong"
    tags = ["tools", "toolsets"]
    uiData = {"icon": "menu_toolsets",
              "tooltip": "Toolsets Window for tool browsing",
              "label": "Toolsets",
              "color": "",
              "backgroundColor": "",
              "multipleTools": True,
              "dock": {"dockable": True, "tabToControl": ("AttributeEditor", -1), "floating": False}
              }

    def execute(self, *args, **kwargs):
        toolArgs = kwargs or {}

        from zoo.apps.toolsetsui import run

        return run.launch(toolArgs=toolArgs)

    def setStyleSheet(self, style):
        for t in self.tools:
            t.setStyleSheet(style)

    def toolClosed(self, tool):
        """ Clean up after tool has closed

        :param tool:
        :return:
        """
        if tool in self.tools:
            self.tools.remove(tool)

    def teardown(self):
        from zoo.apps.toolsetsui import toolsetui
        toolsetuis = list(toolsetui.toolsetUis())

        for t in toolsetuis:
            t.close()

        self.tools = []


class UnitestUI(palette.ToolDefinition):
    id = "zoo.dev.unitest.ui"
    creator = "David Sparrow"
    tags = ["dev", "unitest"]
    uiData = {"icon": "menu_test",
              "tooltip": "Zootools unitesting GUI",
              "label": "Unittest",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        from unittestui import unittestui
        try:
            for tool in self.tools:
                tool.close()
        except (AttributeError, TypeError, RuntimeError):
            pass
        self.tools.append(unittestui.show())

    def teardown(self):
        if self.tools:
            for tool in self.tools:
                tool.close()


"""
SHELF ICONS
"""


class AnimationIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.animation"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "animationMenu_shlf",
              "tooltip": "Animation Tools",
              "label": "Animation Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        pass


class RiggingIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.rigging"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "riggingMenu_shlf",
              "tooltip": "Rigging Tools",
              "label": "Rigging Tools",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        name = kwargs["variant"]
        exe = executor.Executor()
        if name == "match_curves":
            exe.execute("zoo.maya.curves.match")


class ShaderIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.shader"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "shaderMenu_shlf",
              "tooltip": "Shader Tools",
              "label": "Shader Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        pass


class UvIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.uv"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "uvMenu_shlf",
              "tooltip": "UV Tools",
              "label": "UV Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        pass

class UtilitiesIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.utility"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "utilsMenu_shlf",
              "tooltip": "Utilities",
              "label": "Utilities Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        pass


class DevIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.dev"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "devMenu_shlf",
              "tooltip": "Developer Tools",
              "label": "Developer Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        name = kwargs["variant"]
        if name == "zoo_unittest":
            self.manager.executePluginById("zoo.dev.unitest.ui")
        elif name == "reload":
            self.manager.executePluginById("zoo.reload")
        elif name == "shutdown":
            self.manager.executePluginById("zoo.shutdown")
        elif name == "logging":
            pass


class HelpIconShelf(palette.ToolDefinition):
    id = "zoo.shelf.help"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "helpMenu_shlf",
              "tooltip": "Help Menu",
              "label": "Help Menu",
              "color": "",
              "multipleTools": False,
              "backgroundColor": ""
              }

    def execute(self, *args, **kwargs):
        name = kwargs["variant"]
        if name == "create3dcharacters":
            import webbrowser
            webbrowser.open('http://create3dcharacters.com')
        elif name == "zooToolsHelpContents":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/zoo2')
        elif name == "zooToolsInstallUpdate":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/maya-zoo-tools-pro-installer')
        elif name == "zooChangelog":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/maya-zoo-tools-pro-changelog')
        elif name == "zooIssuesFixes":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/maya-zoo-tools-pro-known-issues')
        elif name == "coursesByOrder":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/package-courses')
        elif name == "coursesByPopularity":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/package-by-popularity')
        elif name == "coursesByDateAdded":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/package-by-date-added')
        elif name == "intermediateCourse":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/package-maya-generalist-intermediate')
        elif name == "advancedCourse":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/package-maya-generalist-advanced')
        elif name == "mayaHotkeyList":
            import webbrowser
            webbrowser.open('https://create3dcharacters.com/maya-hotkeys-zoo2')
