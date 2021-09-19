from zoo.preferences.core import prefinterface


class GeneralPreferences(prefinterface.PreferenceInterface):
    id = "general_interface"
    _relativePath = "prefs/maya/general_settings.pref"
    _settings = None

    def primaryRenderer(self):
        """ Primary Renderer

        :return:
        :rtype: basestring
        """
        return self.settings()['primaryRenderer']
