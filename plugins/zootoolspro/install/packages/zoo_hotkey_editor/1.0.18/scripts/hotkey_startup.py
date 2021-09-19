from zoo.apps.hotkeyeditor.core import keysets


def startup(package):
    """ Updates the hotkeys on start up if it has already been installed.

    :param package:
    :return:
    """

    keysets.KeySetManager().updateDefaults()
