import maya.api.OpenMaya as om2

from zoo.apps.toolsetsui import run
from zoo.apps.toolpalette import run as runPalette
from zoo.libs.pyqt.widgets import elements


MODELING_TOOLSET_UIS = ["zooMirrorGeo", "modelingAlign", "curveDuplicate", "tubeFromCurve", "thickExtrude",
                        "subDSmoothControl", "objectCleaner"]
CONTROLS_JOINTS_TOOLSET_UIS = ["controlCreator", "editControls", "colorOverrides", "jointTool", "jointsOnCurve",
                               "controlsOnCurve", "splineRig", "reparentGroupToggle", "skinningUtilities"]
MODEL_ASSETS_TOOLSET_UIS = ["modelAssets", "mayaScenes", "thumbnailScenes"]
UTILITIES_TOOLSET_UIS = ["zooRenamer", "makeConnections", "nodeEditorAlign", "aimAligner"]
CAMERAS_TOOLSET_UIS = ["cameraManager", "imagePlaneTool", "imagePlaneAnim"]
ANIMATION_TOOLSET_UIS = ["generalAnimationTools", "createTurntable"]
DYNAMIC_TOOLSET_UIS = ["nclothwrinklecreator"]
LIGHT_TOOLSET_UIS = ["lightPresets", "hdriSkydomeLights", "areaLights", "directionalLights", "editLights",
                     "viewportLight", "placeReflection"]
UV_TOOLSET_UIS = ["uvUnfold", "unwrapTube", "transferUvs"]
RENDERER_TOOLSET_UIS = ["convertRenderer"]
SHADER_TOOLSET_UIS = ["shaderPresets", "shaderManager", "displacementCreator", "createMattesAovs", "shaderSwapSuffix"]

ALL_TOOLSET_UIS = MODELING_TOOLSET_UIS + CONTROLS_JOINTS_TOOLSET_UIS + MODEL_ASSETS_TOOLSET_UIS + UTILITIES_TOOLSET_UIS
ALL_TOOLSET_UIS += CAMERAS_TOOLSET_UIS + ANIMATION_TOOLSET_UIS + DYNAMIC_TOOLSET_UIS + LIGHT_TOOLSET_UIS
ALL_TOOLSET_UIS += UV_TOOLSET_UIS + RENDERER_TOOLSET_UIS + SHADER_TOOLSET_UIS


def openAllUIs(hive=True):
    """Opens all Zoo UIs"""
    om2.MGlobal.displayInfo("\n\n---------- OPEN ALL TOOLSETS: {} -----------")
    for toolsetUi in ALL_TOOLSET_UIS:
        om2.MGlobal.displayInfo("log ---> Toolset Opened: {}".format(toolsetUi))
        run.openToolset(toolsetUi)
        om2.MGlobal.displayInfo("log ---> Toolset Toggled Off: {}".format(toolsetUi))
        run.openToolset(toolsetUi)
    om2.MGlobal.displayInfo("\n\n---------- OPEN OTHER ZOO WINDOWS: {} -----------")
    runPalette.show().executePluginById("zoo.preferencesui")
    om2.MGlobal.displayInfo("log ---> Toolset Opened: Zoo Prefs")
    runPalette.show().executePluginById("zoo.hotkeyeditorui")
    om2.MGlobal.displayInfo("log ---> Toolset Opened: Hotkey Editor")
    if hive:
        runPalette.show().executePluginById("zoo.hive.artistui")
        om2.MGlobal.displayInfo("log ---> Toolset Opened: Hive Artist UI")
    elements.MessageBox.showOK(title="Question Test Window", parent=None, message="Do something?")
    om2.MGlobal.displayInfo("log ---> Dialog Opened")
    om2.MGlobal.displayInfo("\n\n\n#### SUCCESS IMPORTED ASSETS FOR ALL RENDERERS ####\n\n\n")