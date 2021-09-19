from zoo.core.util import env
from zoo.libs.plugin.envregistry import EnvRegistry
from zoo.apps.toolpalette import palette


paletteUI = None


class PaletteRegistry(EnvRegistry):
    """ Artist Palette registry

    """
    registryEnv = "ZOO_ARTIST_PALETTE_PATH"
    interface = palette.ToolPalette
    variableName = "application"

    def palette(self):
        """ Retrieves the palette based on the host application

        :return:
        :rtype: type[palette.ToolPalette]
        """
        return [c for c in self.classes if env.application() == c.application][0]


def show():
    """ Returns the paletteUI

    :return:
    :rtype: :class:`zoo.apps.maya_integrate.palette.MayaPalette` or :class:`zoo.apps.blender_integrate.palette.BlenderPalette`
    """
    global paletteUI
    if paletteUI:
        return paletteUI
    paletteRegistry = PaletteRegistry()
    paletteRegistry.discover()
    instance = paletteRegistry.palette()
    paletteUI = instance()
    return paletteUI


def close():
    global paletteUI
    try:
        paletteUI.shutdown()
    except AttributeError:
        # happens when zootoolsUi global is none
        pass
    paletteUI = None
