from zoo.preferences.core import prefinterface

# 1. Rename filename
# 2. Set _relativePath to the location of your pref file


class ShaderPreference(prefinterface.PreferenceInterface):
    id = "shader_interface"
    _relativePath = "prefs/maya/zoo_shader_tools.pref"


