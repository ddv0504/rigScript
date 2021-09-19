ARNOLD = "Arnold"
REDSHIFT = "Redshift"
RENDERMAN = "Renderman"
VIEWPORT2 = "Viewport"
MAYA = "Maya"

RENDERER_SUFFIX = {ARNOLD: "ARN",
                   REDSHIFT: "RS",
                   RENDERMAN: "PXR"
                   }

RENDERER_NICE_NAMES = [ARNOLD, REDSHIFT, RENDERMAN]
ALL_RENDERER_NAMES = RENDERER_NICE_NAMES + [VIEWPORT2]

DFLT_RNDR_MODES = [("arnold", ARNOLD), ("redshift", REDSHIFT), ("renderman", RENDERMAN)]  # icon, nicename

RENDERER_SUFFIX_DICT = dict(RENDERER_SUFFIX)
RENDERER_SUFFIX_DICT[VIEWPORT2] = "VP2"  # adds the viewport suffix, technically it's not a renderer shader suffix

RENDERER_PLUGIN = {REDSHIFT: "redshift4maya",
                   RENDERMAN: "RenderMan_for_Maya",
                   ARNOLD: "mtoa"}

# ----------- SHADER TYPES ------------------------
# Maya ------------------
SHAD_TYPE_BLINN = "blinn"
SHAD_TYPE_LAMBERT = "lambert"
SHAD_TYPE_PHONG = "phong"
SHAD_TYPE_PHONGE = "phongE"
SHAD_TYPE_STANDARD = "standardSurface"
# Arnold ------------------
SHAD_TYPE_AISTANDARD = "aiStandardSurface"
# Redshift ------------------
SHAD_TYPE_REDSHIFTM = "redshiftMaterial"
# Renderman ------------------
SHAD_TYPE_PXRSURFACE = "pxrSurface"
SHAD_TYPE_PXRLAYER = "pxrLayerSurface"

# Default Shaders that come with Maya ---------------------
DEFAULT_MAYA_SHADER_TYPES = [SHAD_TYPE_LAMBERT, SHAD_TYPE_BLINN, SHAD_TYPE_STANDARD, SHAD_TYPE_PHONG, SHAD_TYPE_PHONGE,
                             "rampShader", "anisotropic", "ShaderfxShader", "StingrayPBS", "hairPhysicalShader",
                             "hairTubeShader", "layeredShader", "oceanShader", "shadingMap", "surfaceShader",
                             "useBackground"]
# Zoo Supported Shader Types -------------------------
MAYA_SHADER_TYPES = [SHAD_TYPE_LAMBERT, SHAD_TYPE_BLINN, SHAD_TYPE_STANDARD, SHAD_TYPE_PHONG, SHAD_TYPE_PHONGE]
RENDERMAN_SHADER_TYPES = [SHAD_TYPE_PXRSURFACE, SHAD_TYPE_PXRLAYER]
ARNOLD_SHADER_TYPES = [SHAD_TYPE_AISTANDARD]
REDSHIFT_SHADER_TYPES = [SHAD_TYPE_REDSHIFTM]

# All zoo supported shader types in a dict by renderer --------------------
RENDERER_SHAD_TYPES = {MAYA: MAYA_SHADER_TYPES,
                       REDSHIFT: REDSHIFT_SHADER_TYPES,
                       RENDERMAN: RENDERMAN_SHADER_TYPES,
                       ARNOLD: ARNOLD_SHADER_TYPES}
