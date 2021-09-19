"""The new shadermultirenderer, will take over from shader multi renderer

Author: Andrew Silke"""
from maya import cmds

from zoo.libs.maya import zapi

from zoo.libs.maya.cmds.renderer import rendererconstants as cnstnts
from zoo.libs.maya.cmds.shaders.shadertypes import arnoldstandardsurface, redshiftredshiftmaterial, \
    rendermanpxrsurface, rendermanpxrlayersurface, mayastandardsurface, shaderbase

RENDERMAN = cnstnts.RENDERMAN
REDSHIFT = cnstnts.REDSHIFT
ARNOLD = cnstnts.ARNOLD
MAYA = cnstnts.MAYA


def shaderInstance(renderer="", shaderName="shaderName", genAttrDict=None, create=True, ingest=False, node=None,
                   shaderType="", message=True):
    """Creates a single shader instance depending on the renderer.

    Either loads a shader or creates it.

            To create a new shader:
                create=True and node=False to create a new shader

            To load a shader by zapiNode name
                node="zapiNode" (should be a shader node) ingest=True

            To load a shader by string:
                shaderName="shaderName" and ingest=True

    This is a python object used for managing and assigning individual shaders.

    Example use:

        from zoo.libs.maya.cmds.shaders import shadermulti
        shadInst = shadermulti.shaderInstance("Arnold")  # creates a new shader of the default Arnold shader type

        shadInst2.setShaderName("blueShader")
        shadInst2.assignSelected()  # assigns the shader to geo

        shadInst.setDiffuse([0.0, 0.0, 1.0])  # sets diffuse color to blue
        shadInst.setDiffuseWeight(1.0)

        shadInst.setMetalness(1.0)  # sets metalness to be on

        shadInst.setSpecWeight(1.0)
        shadInst.setSpecColor([1, 1, 1])
        shadInst.setSpecRoughness(1.0)
        shadInst.setSpecIOR(1.3)

        shadInst.setCoatWeight(0.0)
        shadInst.setCoatIOR(1.5)
        shadInst.setCoatRoughness(.1)
        shadInst.setCoatColor([1, 1, 1])

        shadInst2 = shadermulti.shaderInstance("rocketShader", create=False)  # Loads existing "rocketShader" as instance

        shadInst2.assignSelected()

        shadInst2.setShaderName("newNameY")
        print(shadInst2.shaderName())

    :param renderer: The name of the renderer "Arnold", "Redshift", "Renderman"
    :type renderer: str
    :param shaderName: The name of the shader to load or create
    :type shaderName: str
    :param genAttrDict: The generic attribute dictionary with attribute values to set only if creating
    :type genAttrDict: dict(str)
    :param create: If True then create a new shader False will load the shader and nodes in the instance
    :type create: bool
    :param ingest: If True then shaders should be passed in as a string name (shaderName) or zapi node (node).
    :type ingest: bool
    :param node: A zapi node as a python object
    :type node: zoo.libs.maya.zapi.base.DGN
    :param shaderType: For renderers when there are multiple shader types eg. "pxrSurface". "" uses default for renderer
    :type shaderType: str
    :param message: Report a message to the user only if creating
    :type message: bool

    :return shaderInstance: The python object of the shader instance
    :rtype: zoo.libs.maya.cmds.shaders.shaderbase.ShaderBase
    """
    shaderInstance = None
    """if renderer == MAYA:
        # TODO Not implimented yet
        if shaderType == cnstnts.SHAD_TYPE_STANDARD or shaderType == "":
            shaderInstance = mayastandardsurface.StandardSurface(shaderName,
                                                                 genAttrDict=genAttrDict,
                                                                 create=create,
                                                                 ingest=ingest,
                                                                 node=node,
                                                                 message=message)"""
    if renderer == ARNOLD:
        if shaderType == cnstnts.SHAD_TYPE_AISTANDARD or shaderType == "":
            shaderInstance = arnoldstandardsurface.AiStandardSurface(shaderName,
                                                                     genAttrDict=genAttrDict,
                                                                     create=create,
                                                                     ingest=ingest,
                                                                     node=node,
                                                                     message=message)
    elif renderer == REDSHIFT:
        if shaderType == cnstnts.SHAD_TYPE_REDSHIFTM or shaderType == "":
            shaderInstance = redshiftredshiftmaterial.RedshiftMaterial(shaderName,
                                                                       genAttrDict=genAttrDict,
                                                                       create=create,
                                                                       ingest=ingest,
                                                                       node=node,
                                                                       message=message)

    elif renderer == RENDERMAN:  # can also do
        if shaderType == cnstnts.SHAD_TYPE_PXRSURFACE or shaderType == "":
            shaderInstance = rendermanpxrsurface.PxrSurface(shaderName,
                                                            genAttrDict=genAttrDict,
                                                            create=create,
                                                            ingest=ingest,
                                                            node=node,
                                                            message=message)
        """elif shaderType == cnstnts.SHAD_TYPE_PXRLAYER:
            # TODO Not implimented yet
            shaderInstance = rendermanpxrlayersurface.PxrLayerMetalness(shaderName,
                                                                        genAttrDict=genAttrDict,
                                                                        create=create,
                                                                        ingest=ingest,
                                                                        node=node,
                                                                        message=message)"""
    if not shaderInstance and ingest is True:
        # Unknown shader type so use shaderbase.ShaderBase, it can still store the shader's basic properties.
        shaderInstance = shaderbase.ShaderBase(shaderName,
                                               genAttrDict=genAttrDict,
                                               create=create,
                                               ingest=ingest,
                                               node=node,
                                               message=message)
    return shaderInstance


def shaderInstanceAutoRenderer(shaderName="", node=None, message=True):
    """Ingests a shader as an instance from an existing shader, and automatically assigns the renderer and shader type.

    :param shaderName: An optional name of the shader to load or create, can also use node
    :type shaderName: str
    :param node: An optional zapi node as a python object, can also use shaderName
    :type node: zoo.libs.maya.zapi.base.DGNode
    :param message: Report a message to the user only if creating
    :type message: bool

    :return shaderInstance: The python object of the shader instance, will be None if the shader is not recognised
    :rtype: zoo.libs.maya.cmds.shaders.shaderbase.ShaderBase
    """
    shadInst = None
    if node:  # get zapi node
        shaderName = node.fullPathName()
    nodeType = cmds.nodeType(shaderName)
    # Maya Shaders ------------------------------------------
    if nodeType == cnstnts.SHAD_TYPE_STANDARD:
        shadInst = shaderInstance(MAYA, shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    # Arnold Shaders ------------------------------------------
    elif nodeType == cnstnts.SHAD_TYPE_AISTANDARD:
        shadInst = shaderInstance(ARNOLD, shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    # Redshift Shaders ------------------------------------------
    elif nodeType == cnstnts.SHAD_TYPE_REDSHIFTM:
        shadInst = shaderInstance(REDSHIFT, shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    # Renderman Shaders ------------------------------------------
    elif nodeType == cnstnts.SHAD_TYPE_PXRSURFACE:
        shadInst = shaderInstance(RENDERMAN, shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    elif nodeType == cnstnts.SHAD_TYPE_PXRLAYER:
        shadInst = shaderInstance(RENDERMAN, shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    if not shadInst:  # shader is not recognised
        shadInst = shaderInstance(renderer="", shaderName=shaderName, genAttrDict=None, create=False, ingest=True,
                                  node=None, shaderType=nodeType, message=message)
    return shadInst
