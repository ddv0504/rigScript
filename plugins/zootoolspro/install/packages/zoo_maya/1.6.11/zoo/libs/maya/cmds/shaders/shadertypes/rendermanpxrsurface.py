"""This module creates and manages a pxr layer shader with Substance Painter metalness style inputs.

Example use:

    from zoo.libs.maya.cmds.shaders import rendermanpxrsurface
    shadInst = rendermanpxrsurface.PxrSurface("shaderName", create=True)  # creates a new shader

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

    shadInst2 = rendermanshaders.PxrSurface("rocketShader")  # Loads existing "rocketShader" as instance

    shadInst2.assignSelected()

    shadInst2.setShaderName("newNameY")
    print(shadInst2.shaderName())

"""

from zoo.libs.maya import zapi

from zoo.libs.maya.cmds.shaders import rendermanshaders
from zoo.libs.maya.cmds.shaders.shadertypes import shaderbase

DIFFUSE_WEIGHT_ATTR = None
DIFFUSE_COLOR_ATTR = "diffuseColor"
DIFFUSE_ROUGHNESS_ATTR = "diffuseRoughness"
METALNESS_ATTR = None
SPECULAR_WEIGHT_ATTR = None
SPECULAR_COLOR_ATTR = "specularEdgeColor"
SPECULAR_ROUGHNESS_ATTR = "specularRoughness"
SPECULAR_IOR_ATTR = "specularIor"
COAT_WEIGHT_ATTR = None
COAT_COLOR_ATTR = "clearcoatEdgeColor"
COAT_ROUGHNESS_ATTR = "clearcoatRoughness"
COAT_IOR_ATTR = "clearcoatIor"


class PxrSurface(shaderbase.ShaderBase):
    """Manages the creation and set/get attribute values for the PxrSurface
    """

    def __init__(self, shaderName="", node=None, genAttrDict=None, create=False, ingest=False, message=True):
        """Either loads a shader or creates it.

        To create a new shader:
            create=True and node=False to create a new shader

        To load a shader by zapiNode name
            node="zapiNode" (should be a shader node) and ingest=True

        To load a shader by string:
            shaderName="shaderName" and ingest=True

        :param shaderName: The name of the shader to load or create
        :type shaderName: str
        :param node: A zapi node as an object
        :type node: zoo.libs.maya.zapi.base.DGNode
        :param genAttrDict: The generic attribute dictionary with attribute values to set only if creating
        :type genAttrDict: dict(str)
        :param create: If True then create a new shader False will load the shader and nodes in the instance
        :type create: bool
        :param ingest: If True then shaders should be passed in as a string name (shaderName) or zapi node (node).
        :type ingest: bool
        :param message: Report a message to the user only if creating
        :type message: bool
        """
        super(PxrSurface, self).__init__(shaderName=shaderName,
                                               node=node,
                                               genAttrDict=genAttrDict,
                                               create=create,
                                               ingest=ingest,
                                               message=message)

    def knownShader(self):
        """Returns True as this shader is supported by Zoo Tools"""
        return True

    # -------------------
    # Create Assign Delete
    # -------------------

    def createShader(self, message=True):
        """Creates a PxrSurface node network and loads the nodes as class variables

        Overridden method.

        :param message: Report a message to the user when the shader is created
        :type message: bool
        """
        shaderName = rendermanshaders.createPxrSurface(shaderName=self.shaderNameVal, message=message)
        self.shaderNode = zapi.nodeByName(shaderName)
        self.shaderNameVal = shaderName
        self.applyCurrentSettings()

    # -------------------
    # Setters Getters - Attributes
    # -------------------

    def setDiffuseWeight(self, value):
        """Sets the diffuse weight

        :param value: The diffuse weight value 0.0-1.0
        :type value: float
        """
        # TODO - combine with diffuse color
        self.diffuseWeightVal = value

    def diffuseWeight(self):
        """Returns the current diffuse weight

        :return value: The diffuse weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        # TODO - combine with diffuse color
        return self.diffuseWeightVal

    def setDiffuse(self, color):
        """Sets the diffuse color

        :param color: The color in linear float color, (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        # TODO - combine with diffuse color
        if self.setAttrColor(DIFFUSE_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.diffuseVal = color

    def diffuse(self):
        """Returns the diffuse color

        :return color: The diffuse color as linear float rgb (0.1, 0.5, 1.0), None if textured/connected
        :rtype color: list(float)
        """
        # TODO - combine with diffuse color
        color = self.getAttrColor(DIFFUSE_COLOR_ATTR)
        if color is not None:
            self.diffuseVal = color
        return color

    def setMetalness(self, value):
        """Sets the metalness value.  Does not exist on this shader, record anyway

        :param value: The metalness value 0-1.0
        :type value: float
        """
        self.metalnessVal = value

    def metalness(self):
        """Returns the metalness value.  Does not exist on this shader but is stored anyway.

        :return value: The metalness value 0-1.0, None if textured/connected
        :rtype value: float
        """
        return self.metalnessVal

    def setSpecWeight(self, value):
        """Sets the specular weight value

        :param value: Specular Weight value 0-1.0
        :type value: float
        """
        # TODO - combine with spec color
        self.specWeightVal = value

    def specWeight(self):
        """Returns the specular weight value

        :return value:  Specular Weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        # TODO - combine with spec color
        return self.specWeightVal

    def setSpecColor(self, color):
        """Sets the specular color

        :param color: Specular color in linear float rgb (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        # TODO - combine with spec color
        if self.setAttrColor(SPECULAR_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.specColorVal = color

    def specColor(self):
        """Returns the specular color

        :return color: Specular color in linear float rgb (0.5, 1.0, 0.0), None if textured/connected
        :rtype color: list(float)
        """
        # TODO - combine with spec color
        color = self.getAttrColor(SPECULAR_COLOR_ATTR)
        if color is not None:
            self.specColorVal = color
        return color

    def setSpecRoughness(self, value):
        """Sets the specular roughness value

        :param value: The specular roughness value 0-1.0
        :type value: float
        """
        if self.setAttrScalar(SPECULAR_ROUGHNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.specRoughnessVal = value

    def specRoughness(self):
        """Returns the specular roughness value

        :return value: The specular roughness value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(SPECULAR_ROUGHNESS_ATTR)
        if color is not None:
            self.specRoughnessVal = color
        return color

    def setSpecIOR(self, value):
        """Sets the specular IOR value

        :param value: The specular IOR value, 1.0 - 20.0
        :type value: float
        """
        color = [value, value, value]  # convert to a color
        if self.setAttrColor(SPECULAR_IOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.specIORVal = value

    def specIOR(self):
        """Sets the specular IOR

        :return value: The specular IOR value, 1.0 - 20.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrColor(SPECULAR_IOR_ATTR)
        if color is None:
            return None
        self.specIORVal = color[0]
        return color[0]

    def setCoatWeight(self, value):
        """Sets the clear coat weight

        :param value: The clear coat weight value 0-1.0
        :type value: float
        """
        # TODO - combine with coat color
        self.coatWeightVal = value

    def coatWeight(self):
        """Returns the clear coat weight

        :return value: The clear coat weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        # TODO - combine with coat color
        return self.coatWeightVal

    def setCoatColor(self, color):
        """Sets the clear coat color

        :param color: Clear coat color in linear float rgb (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        # TODO - combine with coat color
        if self.setAttrColor(COAT_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.coatColorVal = color

    def coatColor(self):
        """Returns the clear coat color

        :return color: Clear coat color in linear float rgb (0.5, 1.0, 0.0), None if textured/connected
        :rtype color: list(float)
        """
        # TODO - combine with coat color
        color = self.getAttrColor(COAT_COLOR_ATTR)
        if color is not None:
            self.coatColorVal = color
        return color

    def setCoatRoughness(self, value):
        """Sets the clear coat roughness value

        :param value: The clear coat roughness value 0 -1.0
        :type value: float
        """
        if self.setAttrScalar(COAT_ROUGHNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.coatRoughnessVal = value

    def coatRoughness(self):
        """Returns the clear coat roughness value

        :return value: The clear coat roughness value 0 -1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(COAT_ROUGHNESS_ATTR)
        if color is not None:
            self.coatRoughnessVal = color
        return color

    def setCoatIOR(self, value):
        """Sets the clear coat IOR value

        :param value: The clear coat IOR value, 1.0 - 20.0
        :type value: float
        """
        color = [value, value, value]  # convert to a color
        if self.setAttrColor(COAT_IOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.coatIORVal = value

    def coatIOR(self):
        """Returns the clear coat IOR value

        Renderman stores IOR as a color, in our case we just apply the IOR to all color channels.

        :return value: The clear coat IOR value, 1.0 - 20.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrColor(COAT_IOR_ATTR)
        if color is None:
            return None
        self.coatIORVal = color[0]
        return color[0]
