# Renderer nice names
ARNOLD = "Arnold"
RENDERMAN = "Renderman"
REDSHIFT = "Redshift"

# Render shader suffix
SHADER_SUFFIX_DICT = {REDSHIFT: "RS",
                      ARNOLD: "ARN",
                      RENDERMAN: "PXR"}

# default keys for the generic shader dicts
DIFFUSE = 'gDiffuseColor_srgb'
DIFFUSEWEIGHT = 'gDiffuseWeight'
METALNESS = 'gMetalness'
SPECWEIGHT = 'gSpecWeight'
SPECCOLOR = 'gSpecColor_srgb'
SPECROUGHNESS = 'gSpecRoughness'
SPECIOR = 'gSpecIor'
COATCOLOR = 'gCoatColor_srgb'
COATWEIGHT = 'gCoatWeight'
COATROUGHNESS = 'gCoatRoughness'
COATIOR = 'gCoatIor'

GEN_KEY_LIST = [DIFFUSE, DIFFUSEWEIGHT, METALNESS,
                SPECWEIGHT, SPECCOLOR, SPECROUGHNESS, SPECIOR,
                COATCOLOR, COATWEIGHT, COATROUGHNESS, COATIOR]

# Default keys for simple textures
TEXTURE_NODE = "textureNode"  # The name of the node connected to the shader
TEXTURE_SOURCE_ATTRIBUTE = "textureSourceAttr"  # The source attribute of the texture connecting to the shader
TEXTURE_DESTINATION_GEN_KEY = "textureDestinationGenKey"

# Shader types
REDSHIFTMATERIAL = "RedshiftMaterial"
PXRSURFACE = "PxrSurface"
PXRLAYEREDSURFACE = "PxrLayeredSurface"
AISTANDARDSURFACE = "aiStandardSurface"

RENDERERSHADERS = {REDSHIFT: [REDSHIFTMATERIAL],
                   RENDERMAN: [PXRSURFACE],
                   ARNOLD: [AISTANDARDSURFACE]}

SHADERMATCHPREFIX = "duplctS"

SHADERNAME = "shaderName"
OBJECTSFACES = "objectFaces"
ATTRSHADERDICT = "attributesShaderDict"

RENDERER_SHADERS_DICT = {REDSHIFT: ["RedshiftMaterial"],
                         RENDERMAN: ["PxrSurface",
                                     "PxrLayeredSurface"],
                         ARNOLD: ["aiStandardSurface"]}

ATTRS_REDSHIFT_MATERIAL = {DIFFUSE: "diffuse_color",
                           DIFFUSEWEIGHT: "diffuse_weight",
                           METALNESS: "refl_metalness",
                           SPECWEIGHT: "refl_weight",
                           SPECCOLOR: "refl_color",
                           SPECROUGHNESS: "refl_roughness",
                           SPECIOR: "refl_ior",
                           COATCOLOR: "coat_color",
                           COATWEIGHT: "coat_weight",
                           COATROUGHNESS: "coat_roughness",
                           COATIOR: "coat_ior"}

ATTRS_AI_STANDARD_SURFACE = {DIFFUSE: "baseColor",
                             DIFFUSEWEIGHT: "base",
                             METALNESS: "metalness",
                             SPECWEIGHT: "specular",
                             SPECCOLOR: "specularColor",
                             SPECROUGHNESS: "specularRoughness",
                             SPECIOR: "specularIOR",
                             COATCOLOR: "coatColor",
                             COATWEIGHT: "coat",
                             COATROUGHNESS: "coatRoughness",
                             COATIOR: "coatIOR"}

ATTRS_PXR_SURFACE = {DIFFUSE: "diffuseColor",
                     DIFFUSEWEIGHT: "diffuseGain",
                     METALNESS: METALNESS,  # doesn't exist!!
                     SPECWEIGHT: SPECWEIGHT,  # doesn't exist!!
                     SPECCOLOR: "specularEdgeColor",
                     SPECROUGHNESS: "specularRoughness",
                     SPECIOR: "specularIor",
                     COATCOLOR: "clearcoatEdgeColor",
                     COATWEIGHT: COATWEIGHT,  # doesn't exist!!
                     COATROUGHNESS: "clearcoatRoughness",
                     COATIOR: "clearcoatIor"}

# Displacement Dictionary keys for attributes and values
DISP_ATTR_TYPE = "type"
DISP_ATTR_DIVISIONS = "divisions"
DISP_ATTR_SCALE = "scale"
DISP_ATTR_AUTOBUMP = "autoBump"
DISP_ATTR_IMAGEPATH = "imagePath"
DISP_ATTR_BOUNDS = "bounds"
DISP_ATTR_RENDERER = "zooRenderer"

# Displacement Network globals, network names and attributes
NW_DISPLACE_NODE = "zooDisplacementNetwork"
NW_DISPLACE_MESH_ATTR = "zooDisplaceMeshConnect"
NW_DISPLACE_SG_ATTR = "zooDisplaceSGConnect"
NW_DISPLACE_FILE_ATTR = "zooDisplaceFileConnect"
NW_DISPLACE_PLACE2D_ATTR = "zooDisplacePlace2dConnect"
NW_DISPLACE_NODE_ATTR = "zooDisplaceNode"

NW_ATTR_LIST = [NW_DISPLACE_MESH_ATTR, NW_DISPLACE_SG_ATTR, NW_DISPLACE_FILE_ATTR, NW_DISPLACE_PLACE2D_ATTR,
                NW_DISPLACE_NODE_ATTR]

# Default keys for simple textures
TEXTURE_NODE = "textureNode"  # The name of the node connected to the shader
TEXTURE_SOURCE_ATTRIBUTE = "textureSourceAttr"  # The source attribute of the texture connecting to the shader
TEXTURE_DESTINATION_GEN_KEY = "textureDestinationGenKey"
