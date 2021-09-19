"""
Folder Hierarchy::

    root
        |-hotkeys
        |-tools
            |- toolName
                    |-settingOne.json
                    |SettingTwoFolder
                                |-setting.json

"""
import os
import copy
import shutil
from collections import OrderedDict
from zoovendor import six
from zoo.libs.utils import filesystem
from zoo.libs.utils import zlogging
from zoo.libs.utils import path as zoopath


logger = zlogging.getLogger(__name__)


class RootAlreadyExistsError(Exception):
    pass


class RootDoesntExistError(Exception):
    pass


class InvalidSettingsPath(Exception):
    pass


class InvalidRootError(Exception):
    pass


class ToolSet(object):
    """
    .. code-block:: python

        # Create some roots
        tset = ToolSet()

        # the order you add roots is important
        tset.addRoot(os.path.expanduser("~/Documents/maya/2018/scripts/zootools_preferences"), "userPreferences")

        # create a settings instance, if one exists already within one of the roots that setting will be used unless you
        # specify the root to use, in which the associated settingsObject for the root will be returned
        newSetting = tset.createSetting(relative="tools/tests/helloworld",
                                        root="userPreferences",
                                        data={"someData": "hello"})
        print os.path.exists(newSetting.path())
        print newSetting.path()
        # lets open a setting
        foundSetting = tset.findSetting(relative="tools/tests/helloworld", root="userPreferences")

    """

    def __init__(self):
        self.roots = OrderedDict()
        self.extension = ".json"

    def rootNameForPath(self, path):
        p = os.path.normpath(path)
        for name, root in self.roots.items():
            if os.path.normpath(root).startswith(p):
                return name

    def root(self, name):
        if name not in self.roots:
            raise RootDoesntExistError("Root by the name: {} doesn't exist".format(name))
        return self._resolveRoot(self.roots[name])

    def _resolveRoot(self, root):
        root = six.text_type(root)
        return os.path.expandvars(os.path.expanduser(root)).replace("\\", "/")

    def addRoot(self, fullPath, name):
        """ Add root

        :param fullPath:
        :param name:
        :return:
        """
        if name in self.roots:
            raise RootAlreadyExistsError("Root already exists: {}".format(name))
        absRoot = self._resolveRoot(fullPath)
        if not os.path.exists(absRoot):
            raise RootDoesntExistError("Root Path Doesn't exist: {}".format(absRoot))
        self.roots[name] = fullPath

    def deleteRoot(self, root):
        """Deletes the root folder location and all files.

        :param root: the root name to delete
        :type root: str
        :return:
        :rtype: bool
        """
        rootPath = self.root(root)
        try:
            shutil.rmtree(rootPath)
        except OSError:
            logger.error("Failed to remove the preference root: {}".format(rootPath),
                         exc_info=True)
            return False
        return True

    def findSetting(self, relativePath, root=None, extension=None):
        """Finds a settings object by searching the roots in reverse order.

        The first path to exist will be the one to be resolved. If a root is specified
        and the root+relativePath exists then that will be returned instead

        :param relativePath:
        :type relativePath: str
        :param root: The Root name to search if root is None then all roots in reverse order will be search until a \
        settings is found.
        :type root: str or None
        :return:
        :rtype: :class:`SettingObject`
        """
        relativePath = six.text_type(relativePath)
        relativePath = zoopath.withExtension(relativePath, extension or self.extension)
        try:
            if root is not None:
                rootPath = self.roots.get(root)
                if rootPath is not None:
                    resolvedRoot = self._resolveRoot(rootPath)
                    fullpath = os.path.normpath(os.path.join(resolvedRoot, relativePath))
                    if not os.path.exists(fullpath):
                        return SettingObject(rootPath, relativePath)
                    return self.open(rootPath, relativePath)
            else:
                for name, p in reversed(self.roots.items()):
                    # we're working with an ordered dict
                    resolvedRoot = self._resolveRoot(p)
                    fullpath = os.path.join(resolvedRoot, relativePath)
                    if not os.path.exists(fullpath):
                        continue
                    return self.open(resolvedRoot, relativePath)
        except ValueError:
            logger.error("Failed to load: {} due to syntactical issue", exc_info=True)
            raise

        return SettingObject("", relativePath)

    def settingFromRootPath(self, relativePath, rootPath):
        fullpath = os.path.join(rootPath, relativePath)
        if not os.path.exists(fullpath):
            return self.open(rootPath, relativePath)
        return SettingObject("", relativePath)

    def createSetting(self, relative, root, data):
        setting = self.findSetting(relative, root)
        setting.update(data)
        return setting

    def open(self, root, relativePath, extension=None):
        relativePath = zoopath.withExtension(relativePath, extension or self.extension)
        fullPath = os.path.join(root, relativePath)
        if not os.path.exists(fullPath):
            raise InvalidSettingsPath(fullPath)
        data = filesystem.loadJson(fullPath)
        return SettingObject(root, relativePath, **data)


class SettingObject(dict):
    """Settings class to encapsulate the json data for a given setting
    """

    def __init__(self, root, relativePath=None, **kwargs):
        relativePath = relativePath or ""
        _, ext = os.path.splitext(relativePath)
        if not ext:
            relativePath = os.path.extsep.join((relativePath, "json"))
        kwargs["relativePath"] = relativePath
        kwargs["root"] = root
        super(SettingObject, self).__init__(**kwargs)

    def rootPath(self):
        if self.root:
            return self.root
        return ""

    def path(self):
        return os.path.join(self.root, self["relativePath"])

    def isValid(self):
        if self.root is None:
            return False
        elif os.path.exists(self.path()):
            return True
        return False

    def __repr__(self):
        return "<{}> root: {}, path: {}".format(self.__class__.__name__, self.root, self.relativePath)

    def __cmp__(self, other):
        return self.name == other and self.version == other.version

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(SettingObject, self).__getattribute__(item)

    def __setattr__(self, key, value):
        self[key] = value

    def save(self, indent=False, sort=False):
        """Saves file to disk as json

        :param indent: If True format the json nicely (indent=2)
        :type indent: bool
        :return fullPath: The full path to the saved .json file
        :rtype fullPath: str
        """
        root = self.root

        if not root:
            return ""

        fullPath = os.path.join(root, self.relativePath)
        filesystem.ensureFolderExists(os.path.dirname(fullPath))
        output = copy.deepcopy(self)
        del output["root"]
        del output["relativePath"]
        numSplit = len(os.path.splitext(os.path.basename(fullPath)))
        if not numSplit > 0:
            fullPath = fullPath + "json"
        if not indent:
            filesystem.saveJson(output, fullPath, sort_keys=sort)
        else:
            filesystem.saveJson(output, fullPath, indent=2, sort_keys=sort)

        return self.path()
