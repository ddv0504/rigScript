from . import iconlib
from ...core.util import env

if env.isInBlender():
    icon = iconlib.BlenderIcon().icon
    iconDataForName = iconlib.BlenderIcon().iconDataForName
    iconPathForName = iconlib.BlenderIcon().iconPathForName
    iconColorized = iconlib.BlenderIcon().iconColorized
    iconColorizedLayered = iconlib.BlenderIcon().iconColorizedLayered
    iconPath = iconlib.BlenderIcon().iconPath
    blenderIcon = iconlib.BlenderIcon().blenderIcon
    clearIcons = iconlib.BlenderIcon().clearIcons
    initIcons = iconlib.BlenderIcon().initBlenderIcons
else:

    icon = iconlib.Icon().icon
    iconDataForName = iconlib.Icon().iconDataForName
    iconPathForName = iconlib.Icon().iconPathForName
    iconColorized = iconlib.Icon().iconColorized
    iconColorizedLayered = iconlib.Icon().iconColorizedLayered
    iconPath = iconlib.Icon().iconPath
