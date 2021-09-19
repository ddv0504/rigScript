"""
Zoo Python Hotkeys
"""
import zoo.libs.maya.cmds.shaders.shaderutils
from zoo.apps.toolsetsui.run import openToolset
from zoo.libs.maya.cmds.modeling import create
from zoo.apps.toolpalette import run
from zoo.libs.maya.cmds.animation import generalanimation


# -------------------
# CREATE FUNCTIONS
# -------------------


def createCamRooXzy():
    """Creates a camera and changes it's rotate order to zxy"""
    from zoo.libs.maya.cmds.cameras import cameras
    cameras.createCameraZxy()


def createCubeMatch():
    """Creates a cube and will match it to the selected object if an object is selected"""
    create.createPrimitiveAndMatch(cube=True, sphere=False, cylinder=False, plane=False)


def createCylinderMatch():
    """Creates a cylinder and will match it to the selected object if an object is selected"""
    create.createPrimitiveAndMatch(cube=False, sphere=False, cylinder=True, plane=False)


def createPlaneMatch():
    """Creates a plane and will match it to the selected object if an object is selected"""
    create.createPrimitiveAndMatch(cube=False, sphere=False, cylinder=False, plane=True)


def createSphereMatch():
    """Creates a plane and will match it to the selected object if an object is selected"""
    create.createPrimitiveAndMatch(cube=False, sphere=True, cylinder=False, plane=False)


# -------------------
# SETTINGS
# -------------------


def hotkeySetToggle():
    """Toggles through all the zoo hotkey sets and user sets"""
    from zoo.apps.hotkeyeditor.core import keysets
    keysets.KeySetManager().nextKeySet()


def reloadZooTools():
    """Reloads Zoo Tools for developers"""
    from zoo.apps.toolpalette import run
    run.show().executePluginById("zoo.reload")


# -------------------
# OBJECTS
# -------------------


def alignSelection():
    """Match Align based on selection (rotation and translation)

    Matches to the first selected object, all other objects are matched to the first in the selection
    """
    from zoo.libs.maya.cmds.objutils import alignutils
    alignutils.matchAllSelection(translate=True, rotate=True, scale=False, pivot=False, message=True)


def mirrorInstanceGroupWorldX():
    """mirror instances an object across world X"""
    from zoo.libs.maya.cmds.modeling import mirror
    mirror.instanceMirror()


def mirrorPolygonPlus():
    """Mirrors polygon with special zero edge or vert selection, plus smooth all edges and delete history"""
    from zoo.libs.maya.cmds.modeling import mirror
    mirror.mirrorPolyEdgeToZero(smoothEdges=True, deleteHistory=True, smoothAngle=180, mergeThreshold=0.001)


# ------------------------------------------------------------------------------------------------------------------
#                                                     WINDOWS
# ------------------------------------------------------------------------------------------------------------------


# -------------------
# ZOO WINDOWS
# -------------------


def open_hiveArtistUI():
    """Opens the Hive Artist UI Window """
    run.show().executePluginById("zoo.hive.artistui")


def open_zooHotkeyEditor():
    """Opens the Zoo Hotkey Editor toolset tool"""
    run.show().executePluginById("zoo.hotkeyeditorui")


def open_zooPreferences():
    """Opens the Zoo Preferences toolset tool"""
    run.show().executePluginById("zoo.preferencesui")


# -------------------
# OPEN ZOO TOOLSET TOOLS
# -------------------


def open_mayaShaders():
    """Opens the Maya Shaders toolset tool"""
    openToolset("mayaShaders")


def open_mayaScenes():
    """Opens the Maya Scenes toolset tool"""
    openToolset("mayaScenes")


def open_randomizeObjects():
    """Opens the Randomize Objects toolset tool"""
    openToolset("randomizeObjects")


def open_graphEditorTools():
    """Opens the Graph Editor Toolbox toolset tool"""
    openToolset("graphEditorTools")


def open_keyRandomizer():
    """Opens the Randomize Keys toolset tool"""
    openToolset("keyRandomizer")


def open_bakeAnimation():
    """Opens the Bake Animation toolset tool"""
    openToolset("bakeAnimation")


def open_numericRetimer():
    """Opens the Numeric Retimer toolset tool"""
    openToolset("numericRetimer")


def open_scaleKeysFromCenter():
    """Opens the Scale Keys From Center Values toolset tool"""
    openToolset("scaleKeysFromCenter")


def open_manageNodes():
    """Opens the Manage Nodes toolset tool"""
    openToolset("manageNodes")


def open_aimAligner():
    """Opens the Aim Aligner toolset tool"""
    openToolset("aimAligner")


def open_imagePlaneAnim():
    """Opens the Animate Image Plane toolset tool"""
    openToolset("imagePlaneAnim")


def open_areaLights():
    """Opens the Area Lights toolset tool"""
    openToolset("areaLights")


def open_makeConnections():
    """Opens the Attribute COnnections toolset tool"""
    openToolset("makeConnections")


def open_cameraManager():
    """Opens the Camera Manager toolset tool"""
    openToolset("cameraManager")


def open_colorOverrides():
    """Opens the Color Overrides toolset tool"""
    openToolset("colorOverrides")


def open_controlCreator():
    """Opens the Control Creator toolset tool"""
    openToolset("controlCreator")


def open_controlsOnCurve():
    """Opens the Controls On Curve toolset tool"""
    openToolset("controlsOnCurve")


def open_convertRenderer():
    """Opens the Convert Renderer toolset tool"""
    openToolset("convertRenderer")


def open_createMattesAovs():
    """Opens the Convert Renderer toolset tool"""
    openToolset("createMattesAovs")


def open_createTurntable():
    """Opens the Create Turntable toolset tool"""
    openToolset("createTurntable")


def open_directionalLights():
    """Opens the Directional Lights toolset tool"""
    openToolset("directionalLights")


def open_displacementCreator():
    """Opens the Displacement Creator toolset tool"""
    openToolset("displacementCreator")


def open_curveDuplicate():
    """Opens the Duplicate Along Curve toolset tool"""
    openToolset("curveDuplicate")


def open_editControls():
    """Opens the Edit Controls toolset tool"""
    openToolset("editControls")


def open_editLights():
    """Opens the Edit Lights toolset tool"""
    openToolset("editLights")


def open_generalAnimationTools():
    """Opens the General Animation toolset tool"""
    openToolset("generalAnimationTools")


def open_hdriSkydomeLights():
    """Opens the HDRI Skydome toolset tool"""
    openToolset("hdriSkydomeLights")


def open_imagePlaneTool():
    """Opens the Image Plane Tool toolset tool"""
    openToolset("imagePlaneTool")


def open_jointsOnCurve():
    """Opens the Joints On Curve toolset tool"""
    openToolset("jointsOnCurve")


def open_jointTool():
    """Opens the Joint Tool toolset tool"""
    openToolset("jointTool")


def open_lightPresets():
    """Opens the Light Presets toolset tool"""
    openToolset("lightPresets")


def open_zooMirrorGeo():
    """Opens the Mirror Geo toolset tool"""
    openToolset("zooMirrorGeo")


def open_modelAssets():
    """Opens the Model Assets toolset tool"""
    openToolset("modelAssets")


def open_modelingAlign():
    """Opens the Modeling Align toolset tool"""
    openToolset("modelingAlign")


def open_nclothwrinklecreator():
    """Opens the NCloth Wrinkle Creator toolset tool"""
    openToolset("nclothwrinklecreator")


def open_nodeEditorAlign():
    """Opens the Node Editor Align toolset tool"""
    openToolset("nodeEditorAlign")


def open_objectCleaner():
    """Opens the Object CLeaner toolset tool"""
    openToolset("objectCleaner")


def open_placeReflection():
    """Opens the Place Reflection toolset tool"""
    openToolset("placeReflection")


def open_zooRenamer():
    """Opens the Zoo Renamer toolset tool"""
    openToolset("zooRenamer")


def open_reparentGroupToggle():
    """Opens the Reparent Group Toggle toolset tool"""
    openToolset("reparentGroupToggle")


def open_shaderManager():
    """Opens the Shader Manager toolset tool"""
    openToolset("shaderManager")


def open_shaderPresets():
    """Opens the Shader Presets toolset tool"""
    openToolset("shaderPresets")


def open_shaderSwapSuffix():
    """Opens the Shader Swap Suffix toolset tool"""
    openToolset("shaderSwapSuffix")


def open_skinningUtilities():
    """Opens the Skinning Utilities toolset tool"""
    openToolset("skinningUtilities")


def open_splineRig():
    """Opens the Spline Rig toolset tool"""
    openToolset("splineRig")


def open_subDSmoothControl():
    """Opens the SubD Smooth Control toolset tool"""
    openToolset("subDSmoothControl")


def open_thickExtrude():
    """Opens the Thick Extrude toolset tool"""
    openToolset("thickExtrude")


def open_thumbnailScenes():
    """Opens the Thumbnail Scenes toolset tool"""
    openToolset("thumbnailScenes")


def open_transferUvs():
    """Opens the Transfer UVs toolset tool"""
    openToolset("transferUvs")


def open_tubeFromCurve():
    """Opens the Tube From Curve toolset tool"""
    openToolset("tubeFromCurve")


def open_unwrapTube():
    """Opens the UV Unfold toolset tool"""
    openToolset("unwrapTube")


def open_uvUnfold():
    """Opens the UV Unfold toolset tool"""
    openToolset("uvUnfold")


def open_viewportLight():
    """Opens the Viewport Light toolset tool"""
    openToolset("viewportLight")


# ------------------------------------------------------------------------------------------------------------------
#                                                     ANIMATION
# ------------------------------------------------------------------------------------------------------------------


# -------------------
# ANIMATION SELECT
# -------------------


def animSelectHierarchy():
    """Selects all animated nodes in the selected hierarchy"""
    generalanimation.selectAnimNodes(mode=0)


def animSelectScene():
    """Selects all animated nodes in the scene"""
    generalanimation.selectAnimNodes(mode=1)


def animSelectSelection():
    """Filters all animated nodes in the current selection"""
    generalanimation.selectAnimNodes(mode=2)


# -------------------
# ANIMATION GENERAL
# -------------------


def setKeyframeChannelBox():
    """Keys the selected attrs or if nothing is selected keys all attrs"""
    generalanimation.setKeyChannel()


def setKeyAll():
    """Sets a key on all attributes ignoring any Channel Box selection."""
    generalanimation.setKeyAll()


def animMakeHold():
    """Creates a held pose with two identical keys and flat tangents intelligently from the current keyframes
    """
    generalanimation.animHold()


def toogleKeyVisibility():
    """Reverses the visibility of an object in Maya and keys it's visibility attribute"""
    generalanimation.keyToggleVis()


def resetAttrs():
    """Resets attributes in the channel box to defaults"""
    generalanimation.resetAttrsBtn()


def bakeKeys():
    """Bakes animation keyframes using bake curves or bake simulation depending on the selection"""
    generalanimation.bakeKeys()


def eulerFilter():
    """Perform Maya's Euler Filter on selected objects rotation values"""
    generalanimation.eulerFilter()


def createMotionTrail():
    """Creates a motion trail on the selected object and changes the draw mode to `alternating` frames"""
    generalanimation.createMotionTrail()


def openGhostEditor():
    """Opens Maya's Ghost Editor Window"""
    generalanimation.openGhostEditor()


# -------------------
# GRAPH EDITOR
# -------------------


def jumpKeySelectedTime():
    """Changes the current time in the graph editor (Maya timeline) to match to the closest selected keyframe"""
    generalanimation.timeToKey()


def keySnapToTime():
    """Moves the selected keys to the current time. The first keyframe matching, maintains the spacing of selection"""
    generalanimation.snapKeysCurrent()


def selectObjFromFCurve():
    """Selects an object from an fCurve"""
    generalanimation.selObjGraph()


def snapKeysWholeFrames():
    """Snaps the selected keys to whole frames."""
    generalanimation.snapKeysWholeFrames()


def toggleInfinity():
    """Toggles infinity on and off in the Graph Editor"""
    generalanimation.toggleInfinity()


def cycleInfinity():
    """Cycles the selected objects, with standard cycle option pre and post."""
    generalanimation.cycleAnimation()


def removeCycleAnimation():
    """Cycles the selected objects, with standard cycle option pre and post."""
    generalanimation.removeCycleAnimation()


def copyKeys():
    """Snaps the selected keys to whole frames."""
    generalanimation.copyKeys()


def pasteKeys():
    """Snaps the selected keys to whole frames."""
    generalanimation.pasteKeys()


# -------------------
# PLAY STEP
# -------------------


def playPause():
    """Regular Maya play pause hotkey"""
    generalanimation.playPause()


def playReversePause():
    """Regular Maya play pause hotkey"""
    generalanimation.reverse()


def animMoveTimeBack5Frames():
    """Moves the time slider backwards by 5 frames."""
    generalanimation.step5framesBackwards()


def animMoveTimeForwards5Frames():
    """Moves the time slider forwards by 5 frames."""
    generalanimation.step5framesForwards()


# -------------------
# TIMELINE
# -------------------


def playRangeStart():
    """Sets the range slider start to be the current frame in time"""
    generalanimation.playRangeStart()


def playRangeEnd():
    """Sets the range slider end to be the current frame in time
    """
    generalanimation.playRangeEnd()


def timeRangeStart():
    """Sets the time-range start to the current time."""
    generalanimation.timeRangeStart()


def timeRangeEnd():
    """Sets the time-range end to the current time."""
    generalanimation.timeRangeEnd()


# -------------------
# DISPLAY
# -------------------


def displayToggleTextureMode():
    """Toggles the texture viewport mode, will invert. Eg. if "on" turns "off" """
    from zoo.libs.maya.cmds.display import viewportmodes
    viewportmodes.displayToggleTextureMode()


def displayToggleWireShadedMode():
    """Toggles the texture viewport mode, will invert. Eg. if "on" turns "off" """
    from zoo.libs.maya.cmds.display import viewportmodes
    viewportmodes.displayToggleWireShadedMode()


def displayToggleLightingMode():
    """Toggles the light viewport mode, will invert. Eg. if "on" turns "off" """
    from zoo.libs.maya.cmds.display import viewportmodes
    viewportmodes.displayToggleLightingMode()


def displayToggleWireOnShadedMode():
    """Toggles the 'wireframe on shaded' viewport mode. Will invert. Eg. if "shaded" turns "wireframeOnShaded" """
    from zoo.libs.maya.cmds.display import viewportmodes
    viewportmodes.displayToggleWireOnShadedMode()


def displayToggleXrayMode():
    """Toggles the xray viewport mode. Will invert. Eg. if "xray on" turns "xray off" """
    from zoo.libs.maya.cmds.display import viewportmodes
    viewportmodes.displayToggleXrayMode()


def selectCamInView():
    """Selects the camera under the pointer or if an error, get the camera in active panel, if error return message"""
    from zoo.libs.maya.cmds.cameras import cameras
    cameras.selectCamInView()


def zooCycleBackgroundColors():
    """Adds additional colors to "alt b" which adds more dark colors while cycling through viewport background colors"""
    from zoo.libs.maya.cmds.display import viewportcolors
    viewportcolors.cycleBackgroundColorsZoo()


def cyclePerspCameras(limitPerspective=True):
    """Cycles the main view through all cameras in the scene, default skips orthographic cams"""
    from zoo.libs.maya.cmds.cameras import cameras
    cameras.cycleThroughCameras(limitPerspective=limitPerspective)


# -------------------
# SELECT
# -------------------


def selectHierarchy():
    """Select all children in the hierarchy"""
    from zoo.libs.maya.cmds.objutils import selection
    selection.selectHierarchy()


def selectNodeOrShaderAttrEditor():
    """Selects the shader or the selected nodes:

        1. Selects the node if selected in the channel box and opens the attribute editor
        2. Or if a transform node is selected, select the shaders of the current selection and open attr editor

    """
    zoo.libs.maya.cmds.shaders.shaderutils.selectNodeOrShaderAttrEditor()
