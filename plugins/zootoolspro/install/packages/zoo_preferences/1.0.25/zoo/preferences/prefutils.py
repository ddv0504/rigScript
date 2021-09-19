def coreInterface():
    """ Get the core interface

    :return: Returns the preference interface "core_interface"
    :rtype: :class:`preferences.interface.preference_interface.ZooToolsPreference`
    """
    from zoo.preferences.core import preference
    return preference.interface("core_interface")


def generalInterface():
    """ Get the general settings

    :return: Returns the preference interface "general_interface"
    :rtype: :class:`preferences.interface.general_interface.GeneralPreferences`
    """
    from zoo.preferences.core import preference
    return preference.interface("general_interface")
