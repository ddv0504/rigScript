from zoo.apps.uninstallerui import uninstaller
from zoo.libs.utils import zlogging


logger = zlogging.getLogger(__name__)


def launch():
    """Load the artist GUI for hive.
    :return:
    :rtype: :class:`artistui.HiveArtistUI`
    """
    uninstallerui = uninstaller.UninstallerUi()

    return uninstallerui


def scriptEditorLaunch():
    from zoo.apps.toolpalette import run
    a = run.show()
    return a.executePluginById("zoo.uninstaller", **{})
