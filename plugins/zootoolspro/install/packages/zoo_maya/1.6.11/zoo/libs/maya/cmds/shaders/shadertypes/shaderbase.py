"""This module creates and manages a shader with generic inputs.  This is the base class and is intended to be
extended/overidden by each shader type.

"""
import maya.cmds as cmds

from zoo.libs.maya import zapi

from zoo.libs.maya.cmds.shaders import shaderutils
from zoo.libs.maya.cmds.shaders.shdmultconstants import DIFFUSE, DIFFUSEWEIGHT, METALNESS, SPECWEIGHT, SPECCOLOR, \
    SPECROUGHNESS, SPECIOR, COATCOLOR, COATWEIGHT, COATROUGHNESS, COATIOR
from zoo.libs.utils import colour


class ShaderBase(object):
    """Main class that manages the creation setting and getting of attrs for a shader with generic inputs
    """

    def __init__(self, shaderName="", node=None, genAttrDict=None, create=False, ingest=False, message=True):
        """Either loads a shader or creates it.

        To create a new shader:
            create=True and node=False to create a new shader

        To load a shader by zapiNode name
            node="zapiNode" (should be a shader node) and ingest=True

        To load a shader by string:
            shaderName="shaderName" and ingest=True

        :param shader: The string name of the shader to load or create
        :type shader: str
        :param node: Optional zapi node object and will load not create the instance
        :type node: :class:`zapi.DGNode`
        :param genAttrDict: The generic attribute dictionary with attribute values to set only if creating
        :type genAttrDict: dict(str)
        :param create: If True then create a new shader False will load the shader nodes in the instance
        :type create: bool
        :param ingest: If True then create a new shader False will load the shader nodes in the instance
        :type ingest: bool
        :param message: Report a message to the user only if creating
        :type message: bool
        """
        super(ShaderBase, self).__init__()
        # Ingest existing shader ----------------------------------
        if node and ingest:  # Passed in an existing zapi node
            self.shaderNameVal = node.fullPathName()
            self._allNodes(self.shaderNameVal)  # gets all nodes in the network and sets them
            self.pullShaderSettings()
            return
        if shaderName and ingest:  # Use the shader name to ingest into the instance
            self.shaderNameVal = shaderName
            self._allNodes(self.shaderNameVal)  # gets all nodes in the network and sets them
            self.pullShaderSettings()
            return
        # Create a new instance and possible new shader ------------------------------------
        self.shaderNameVal = shaderName
        if not shaderName:
            self.shaderNameVal = "newShader"
        # See also self.setDefaults()  # sets the shader default attributes
        self.diffuseVal = [0.5, 0.5, 0.5]
        self.diffuseWeightVal = 1.0
        self.metalnessVal = 0.0
        self.specColorVal = [1.0, 1.0, 1.0]
        self.specWeightVal = 1.0
        self.specRoughnessVal = 0.2
        self.specIORVal = 1.5
        self.coatColorVal = [1.0, 1.0, 1.0]
        self.coatRoughnessVal = 0.1
        self.coatWeightVal = 0.0
        self.coatIORVal = 1.5
        if create:  # Create a new shader -----------------
            self.createShader(message=message)
        if genAttrDict:  # override the dictionary values
            self.setShaderValues(genAttrDict, apply=False)
        if create:
            self.applyCurrentSettings()

    # -------------------
    # Base Methods
    # -------------------

    def exists(self):
        """Tests to see if the shader connected to the instance exists

        :return shaderExists: True if the shader exists in the scene, False if not.
        :rtype shaderExists: bool
        """
        try:
            self.shaderNode.fullPathName()
            return True
        except (AttributeError, RuntimeError) as e:  # shader has been deleted or not created
            return False

    def shaderType(self):
        """Returns the type of the shader node. Must have been created

        :return shaderType:  The type of the current shader, must be alive. Eg. "standardSurface"
        :rtype shaderType: str
        """
        return cmds.nodeType(self.shaderNode.fullPathName())

    def knownShader(self):
        """Returns True if the shader is supported by Zoo Tools, should be overridden"""
        return False

    def setDefaults(self):
        """Sets the defaults internally, the shader does not need to be created"""
        self.diffuseVal = [0.5, 0.5, 0.5]
        self.diffuseWeightVal = 1.0
        self.metalnessVal = 0.0
        self.specColorVal = [1.0, 1.0, 1.0]
        self.specWeightVal = 1.0
        self.specRoughnessVal = 0.2
        self.specIORVal = 1.5
        self.coatColorVal = [1.0, 1.0, 1.0]
        self.coatRoughnessVal = 0.1
        self.coatWeightVal = 0.0
        self.coatIORVal = 1.5

    def applyCurrentSettings(self):
        """Applies the current settings"""
        self.setDiffuse(self.diffuseVal)
        self.setDiffuseWeight(self.diffuseWeightVal)
        self.setMetalness(self.metalnessVal)
        self.setSpecColor(self.specColorVal)
        self.setSpecWeight(self.specWeightVal)
        self.setSpecRoughness(self.specRoughnessVal)
        self.setSpecIOR(self.specIORVal)
        self.setCoatColor(self.coatColorVal)
        self.setCoatRoughness(self.coatRoughnessVal)
        self.setCoatWeight(self.coatWeightVal)
        self.setCoatIOR(self.coatIORVal)

    def pullShaderSettings(self):
        """Pulls the current attributes from the current shader, shader must exist"""
        self.diffuseVal = self.diffuse()
        self.diffuseWeightVal = self.diffuseWeight()
        self.metalnessVal = self.metalness()
        self.specColorVal = self.specColor()
        self.specWeightVal = self.specWeight()
        self.specRoughnessVal = self.specRoughness()
        self.specIORVal = self.specIOR()
        self.coatColorVal = self.coatColor()
        self.coatRoughnessVal = self.coatRoughness()
        self.coatWeightVal = self.coatWeight()
        self.coatIORVal = self.coatIOR()

    def _allNodes(self, shader):
        """Gets all the node/s from the shader name and sets as class variables.

        :param shader: The name of the shader
        :type shader: str
        """
        if cmds.objExists(shader):
            self.shaderNode = zapi.nodeByName(shader)
        else:
            self.shaderNode = None
        # override if need to add more nodes

    # -------------------
    # Attributes And Texture Checks
    # -------------------

    def setAttrColor(self, attributeName, color):
        """Sets a color attribute, returns None if textured or unusable

        :param attributeName: The maya attribute name
        :type attributeName: str
        :param color: A color in linear float (0.5, 0.5, 0.5)
        :type color: list(float)
        :return attributeSet: True if the attribute was set, False if not due to textured or locked
        :rtype attributeSet: bool
        """
        if not self.attrSettable(attributeName):
            return False
        cmds.setAttr(".".join([self.shaderNode.fullPathName(), attributeName]),
                     color[0], color[1], color[2],
                     type="double3")
        return True

    def setAttrScalar(self, attributeName, value):
        """Sets a scalar single value attribute, returns None if textured/connected

        :param attributeName: The maya attribute name
        :type attributeName: str
        :param value: A single float value
        :type value: float
        :return attributeSet: True if the attribute was set, False if not due to textured or locked
        :rtype attributeSet: bool
        """
        if not self.attrSettable(attributeName):
            return False
        cmds.setAttr(".".join([self.shaderNode.fullPathName(), attributeName]), value)
        return True

    def getAttrColor(self, attributeName):
        """Gets the color of an attribute, returns None if textured/connected

        :param attributeName: The maya attribute name
        :type attributeName: str
        :return color:  The color returned, if textured or locked returns None
        :rtype color: list(float)
        """
        if cmds.listConnections(".".join([self.shaderNode.fullPathName(), attributeName])):
            return None
        return cmds.getAttr(".".join([self.shaderNode.fullPathName(), attributeName]))[0]

    def getAttrScalar(self, attributeName):
        """Gets the value of an float or int attribute

        :param attributeName: The maya attribute name
        :type attributeName: str
        :return value: The value returned, if textured of locked returns None
        :rtype value: float or int
        """
        if cmds.listConnections(".".join([self.shaderNode.fullPathName(), attributeName])):
            return None
        return cmds.getAttr(".".join([self.shaderNode.fullPathName(), attributeName]))

    def attrSettable(self, attributeName):
        """Tests if the attribute name is settable, if False it's textured or locked

        :param attributeName: The maya attribute name
        :type attributeName: str
        :return settable: True and the attribute is settable, False and the attribute is locked or textured
        :rtype settable: str
        """
        return cmds.getAttr(".".join([self.shaderNode.fullPathName(), attributeName]), settable=True)

    def attrDisconnectTexture(self, attributeName):
        pass

    # -------------------
    # Create Assign Delete
    # -------------------

    def createShader(self, message=True):
        """Creates the shader.  Should be overridden
        """
        pass

    def deleteShader(self):
        """Deletes the shader

        Should be overridden if multiple nodes to be deleted
        """
        cmds.delete(self.shaderNode.fullPathName())
        self.shaderNode = None

    def assign(self, objFaceList):
        """Assign the shader to a list of geometry or components.

        :param objFaceList: A list of objects or faces or both
        :type objFaceList: list(str)
        """
        shaderutils.assignShader(objFaceList, self.shaderNode.fullPathName())

    def assignSelected(self):
        """Assign the shader to the current selection"""
        cmds.hyperShade(assign=self.shaderNode.fullPathName())

    # -------------------
    # Setters Getters - Misc
    # -------------------

    def setShaderValues(self, genAttrDict, apply=True):
        """Sets the shader with attribute values from a generic shader dictionary, keys are from shdmultconstants

        :param genAttrDict: The generic attribute dictionary with attribute values to set (optional)
        :type genAttrDict: dict(str)
        """
        # Set values, the shader may not be built, if not then apply should be set to default
        if DIFFUSE in genAttrDict:
            self.diffuseVal = genAttrDict[DIFFUSE]
        if DIFFUSEWEIGHT in genAttrDict:
            self.diffuseWeightVal = genAttrDict[DIFFUSEWEIGHT]
        if METALNESS in genAttrDict:
            self.metalnessVal = genAttrDict[METALNESS]
        if SPECWEIGHT in genAttrDict:
            self.specWeightVal = genAttrDict[SPECWEIGHT]
        if SPECCOLOR in genAttrDict:
            self.specColorVal = genAttrDict[SPECCOLOR]
        if SPECROUGHNESS in genAttrDict:
            self.specRoughnessVal = genAttrDict[SPECROUGHNESS]
        if SPECIOR in genAttrDict:
            self.specIORVal = genAttrDict[SPECIOR]
        if COATCOLOR in genAttrDict:
            self.coatColorVal = genAttrDict[COATCOLOR]
        if COATWEIGHT in genAttrDict:
            self.coatWeightVal = genAttrDict[COATWEIGHT]
        if COATROUGHNESS in genAttrDict:
            self.coatRoughnessVal = genAttrDict[COATROUGHNESS]
        if COATIOR in genAttrDict:
            self.coatIORVal = genAttrDict[COATIOR]
        if apply:  # Sets the shader attributes to the above settings
            self.applyCurrentSettings()

    def shaderValues(self):
        """Returns values of the shader attribute in a generic shader dictionary, keys are from shdmultconstants

        :return genAttrDict: A dictionary of generic shader keys with values as per shdmultconstants
        :rtype genAttrDict: dict(str)
        """
        genAttrDict = dict()
        genAttrDict[DIFFUSE] = self.diffuse()
        genAttrDict[DIFFUSEWEIGHT] = self.diffuseWeight()
        genAttrDict[METALNESS] = self.metalness()
        genAttrDict[SPECWEIGHT] = self.specWeight()
        genAttrDict[SPECCOLOR] = self.specColor()
        genAttrDict[SPECROUGHNESS] = self.specRoughness()
        genAttrDict[SPECIOR] = self.specIOR()
        genAttrDict[COATCOLOR] = self.coatColor()
        genAttrDict[COATWEIGHT] = self.coatWeight()
        genAttrDict[COATROUGHNESS] = self.coatRoughness()
        genAttrDict[COATIOR] = self.coatIOR()
        return genAttrDict

    def setShaderName(self, newName):
        """Renames the shader"""
        if self.exists():
            shaderName = cmds.rename(self.shaderNode.fullPathName(), newName)
            self.shaderNameVal = shaderName
        else:
            self.shaderNameVal = newName

    def shaderName(self):
        """Returns and updates the shader's name"""
        if self.exists():
            self.shaderNameVal = self.shaderNode.fullPathName()
            return self.shaderNameVal
        else:
            return self.shaderNameVal

    # -------------------
    # Setters Getters - Attributes
    # -------------------

    def setDiffuse(self, value):
        pass

    def setDiffuseSrgb(self, value):
        self.setDiffuse(colour.convertColorSrgbToLinear(value))

    def diffuse(self):
        return None

    def diffuseSrgb(self):
        if self.diffuseVal:
            return colour.convertColorLinearToSrgb(self.diffuseVal)
        return None

    def setDiffuseWeight(self, value):
        pass

    def diffuseWeight(self):
        return None

    def setMetalness(self, value):
        pass

    def metalness(self):
        return None

    def setSpecWeight(self, value):
        pass

    def specWeight(self):
        return None

    def setSpecColor(self, value):
        pass

    def setSpecColorSrgb(self, value):
        self.setSpecColor(colour.convertColorSrgbToLinear(value))

    def specColor(self):
        return None

    def specColorSrgb(self):
        if self.specColorVal:
            return colour.convertColorLinearToSrgb(self.specColorVal)
        return None

    def setSpecRoughness(self, value):
        pass

    def specRoughness(self):
        return None

    def setSpecIOR(self, value):
        pass

    def specIOR(self):
        return None

    def setCoatColor(self, value):
        pass

    def setCoatColorSrgb(self, value):
        self.setCoatColor(colour.convertColorSrgbToLinear(value))

    def coatColor(self):
        return None

    def coatColorSrgb(self):
        if self.coatColorVal:
            return colour.convertColorLinearToSrgb(self.coatColorVal)
        return None

    def setCoatWeight(self, value):
        pass

    def coatWeight(self):
        return None

    def setCoatRoughness(self, value):
        pass

    def coatRoughness(self):
        return None

    def setCoatIOR(self, value):
        pass

    def coatIOR(self):
        return None
