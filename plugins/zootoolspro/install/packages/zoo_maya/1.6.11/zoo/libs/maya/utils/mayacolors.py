import maya.mel as mel

from zoo.libs.maya.utils import mayaenv
from zoo.libs.utils import output

# Maya calls these from the list integer 0-31, note this is not Linear (will not match the viewport), see linear below
MAYA_COLOR_SRGB = [(0.0, 0.0156, 0.3764),
                   (0.0, 0.0, 0.0),
                   (0.251, 0.251, 0.251),
                   (0.6, 0.6, 0.6),
                   (0.608, 0.0, 0.157),
                   (0.0, 0.0156, 0.3764),
                   (0.0, 0.0, 1.0),
                   (0.0, 0.275, 0.098),
                   (0.149, 0.0, 0.263),
                   (0.784, 0.0, 0.784),
                   (0.541, 0.282, 0.2),
                   (0.247, 0.137, 0.121),
                   (0.6, 0.149, 0.0),
                   (1.0, 0.0, 0.0),
                   (0.0, 1.0, 0.0),
                   (0.0, 0.255, 0.6),
                   (1.0, 1.0, 1.0),
                   (1.0, 1.0, 0.0),
                   (0.3921, 0.8627, 1.0),
                   (0.263, 1.0, 0.639),
                   (1.0, 0.650, 0.650),
                   (0.894, 0.674, 0.474),
                   (1.0, 1.0, 0.388),
                   (0.0, 0.6, 0.329),
                   (0.631, 0.416, 0.188),
                   (0.620, 0.631, 0.188),
                   (0.407, 0.631, 0.188),
                   (0.188, 0.631, 0.365),
                   (0.188, 0.631, 0.631),
                   (0.188, 0.404, 0.631),
                   (0.435, 0.188, 0.631),
                   (0.631, 0.188, 0.416)]

# linear Maya colors hardcoded, Maya calls these from the list integer 0-31
MAYA_COLOR_LINEAR_RGB = [(0.0000, 0.0012, 0.1169),
                         (0.0000, 0.0000, 0.0000),
                         (0.0513, 0.0513, 0.0513),
                         (0.3185, 0.3185, 0.3185),
                         (0.3280, 0.0000, 0.0213),
                         (0.0000, 0.0012, 0.1169),
                         (0.0000, 0.0000, 1.0000),
                         (0.0000, 0.0615, 0.0097),
                         (0.0194, 0.0000, 0.0562),
                         (0.5771, 0.0000, 0.5771),
                         (0.2540, 0.0646, 0.0331),
                         (0.0497, 0.0168, 0.0136),
                         (0.3185, 0.0194, 0.0000),
                         (1.0000, 0.0000, 0.0000),
                         (0.0000, 1.0000, 0.0000),
                         (0.0000, 0.0529, 0.3185),
                         (1.0000, 1.0000, 1.0000),
                         (1.0000, 1.0000, 0.0000),
                         (0.1274, 0.7156, 1.0000),
                         (0.0562, 1.0000, 0.3660),
                         (1.0000, 0.3801, 0.3801),
                         (0.7756, 0.4119, 0.1908),
                         (1.0000, 1.0000, 0.1246),
                         (0.0000, 0.3185, 0.0884),
                         (0.3559, 0.1444, 0.0295),
                         (0.3424, 0.3559, 0.0295),
                         (0.1378, 0.3559, 0.0295),
                         (0.0295, 0.3559, 0.1096),
                         (0.0295, 0.3559, 0.3559),
                         (0.0295, 0.1357, 0.3559),
                         (0.1587, 0.0295, 0.3559),
                         (0.3559, 0.0295, 0.1444)]

# Maya's index colors by name for objects, Maya calls these from the list integer 0-31
MAYA_COLOR_NICENAMES = ['none',
                        'black',
                        'lightGrey',
                        'midGrey',
                        'tomatoe',
                        'darkBlue',
                        'blue',
                        'darkGreen',
                        'darkPurple',
                        'pink',
                        'brownOrange',
                        'brown',
                        'orange',
                        'red',
                        'green',
                        'royalBlue',
                        'white',
                        'yellow',
                        'babyBlue',
                        'aqua',
                        'palePink',
                        'skin',
                        'paleYellow',
                        'paleGreen',
                        'orangeBrownLight',
                        'olive',
                        'citrus',
                        'forrestGreen',
                        'java',
                        'endeavourBlue',
                        'darkOrchid',
                        'mediumRedViolet']

VP_BG_COLORS_LINEAR = [[0.0, 0.0, 0.0],
                       [0.36, 0.36, 0.36],
                       [0.613, 0.613, 0.613]]
VP_BG_GRADIENT_TOP = [0.535, 0.617, 0.702]
VP_BG_GRADIENT_BOT = [0.052, 0.052, 0.052]
VP_GRADIENT_COLORS_LINEAR = [[VP_BG_GRADIENT_TOP, VP_BG_GRADIENT_BOT]]

ZOO_BG_COLORS_LINEAR = [VP_BG_COLORS_LINEAR[0],
                        [0.16, 0.16, 0.16],
                        [0.26, 0.26, 0.26],
                        VP_BG_COLORS_LINEAR[1],
                        VP_BG_COLORS_LINEAR[2]]


def setColorSpaceLinear():
    """Sets color space color management settings to be linear as per older versions of Maya in 2022 and above"""
    if mayaenv.mayaVersion() >= 2022:
        mel.eval('colorManagementPrefs -e -rsn "scene-linear Rec.709-sRGB";')
        mel.eval('colorManagementPrefs -e -vtn "Un-tone-mapped (sRGB)";')
    else:
        output.displayWarning("This setting is for Maya 2022. "
                              "The Linear color management setting is the default in Maya 2020 and below.")


def setColorSpaceAces():
    """Sets color space color management settings to be ACES as per the new defaults in Maya in 2022 and above"""
    if mayaenv.mayaVersion() >= 2022:
        mel.eval('colorManagementPrefs -e -rsn "ACEScg";')
        mel.eval('colorManagementPrefs -e -vtn "ACES 1.0 SDR-video (sRGB)";')
    else:
        output.displayWarning("ACES color management is only in Maya 2022 and above. ")