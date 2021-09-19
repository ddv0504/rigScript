import shutil

from maya import cmds
from zoo.core import api
from zoo.core.manager import currentConfig
import os
import glob

from zoo.libs.maya.utils import general
from zoo.libs.utils import zlogging
from zoo.preferences import prefutils

from zoo.core.util import env

logger = zlogging.getLogger(__name__)


class UninstallerCore(object):

    def __init__(self):
        super(UninstallerCore, self).__init__()
        self.coreInterface = prefutils.coreInterface()

    def uninstall(self, zootools, assets, prefs, customPackages):
        """ Uninstall

        :param zootools:
        :param assets:
        :param prefs:
        :param customPackages:
        :return:
        """
        self._initVars()

        if zootools:
            self.deleteModFiles()
            cmds.unloadPlugin("zootools.py")
            cmds.unloadPlugin("zooundo.py")
            self.deleteZooTools()
            self.deleteShelf()

        # Delete Mod (modFiles)
        if prefs:
            self.deletePrefs()  # this crashes maya for some reason

        if assets:
            self.deleteAssets()

        if customPackages:
            self.deleteCustomPackages()

        self.finishUp()
        return True

    def _initVars(self):
        """ Get all the required variables before disabling zoo tools

        :return:
        """
        self._zoo = currentConfig()
        self._prefsPath = self.coreInterface.prefsPath()
        self._zooPrefsRoot = self.coreInterface.defaultPreferencePath()
        self._resolver = api.currentConfig().resolver
        self._assetPath = self.coreInterface.assetPath()
        self._shelvesDir = general.userShelfDir()

    def deleteCustomPackages(self):
        print("Todo: Delete custom packages")
        for name, pkg in self._resolver.cache.items():
            print(name, pkg)

    def deletePrefs(self):

        logger.info("Delete preferences: '{}'".format(self._prefsPath))
        self.deleteFolder(self._prefsPath, walk=True)

    def checkPreferenceFolder(self):
        # Delete prefs if there are no files left
        if len(os.listdir(self._zooPrefsRoot)) == 0:
            os.rmdir(self._zooPrefsRoot)

    def finishUp(self):
        """ Finish up the uninstall script

        :return:
        """
        self.checkPreferenceFolder()
        cmds.pluginInfo("zootools.py", remove=1, e=1)

    def deleteAssets(self):
        """ Delete the assets

        :return:
        """

        logger.info("Deleting assets: '{}'".format(self._assetPath))
        self.deleteFolder(self._assetPath)

    @classmethod
    def deleteFolder(cls, path, walk=False):
        """ Delete folder if it exists

        :param path:
        :return:
        """
        if os.path.exists(path):
            try:
                shutil.rmtree(path, ignore_errors=False)
            except:
                import traceback
                import maya.api.OpenMaya as om2
                traceback.print_exc()
                om2.MGlobal.displayWarning("Unable to delete '{}'".format(path))

    def deleteZooTools(self):
        """ Delete zoo tools pro

        :return:
        """
        # Delete scripts (zooPath)
        zooPath = self._zoo.rootPath
        logger.info("Deleting ZooToolsPro: '{}'".format(zooPath))
        self.deleteFolder(zooPath)

    def deleteShelf(self):
        """ Deletes the zoo tools pro shelf

        :return:
        """
        shelfPath = os.path.join(self._shelvesDir, "shelf_ZooToolsPro.mel")
        if os.path.exists(shelfPath):
            os.remove(shelfPath)
            logger.info("Deleting ZooToolsPro shelf")

    def modDirs(self):
        pathStr = os.getenv("MAYA_MODULE_PATH")
        if env.isWindows():
            return pathStr.split(';')
        else:
            return pathStr.split(':')

    def deleteModFiles(self):
        """ Delete the mod files

        :return:
        """
        modFiles = []
        modDirs = self.modDirs()
        for m in modDirs:
            mod = glob.glob(os.path.join(m, "zootoolspro.mod"))
            if mod:
                modFiles += mod

        # Todo go through each mod file and delete zootoolspro, warn user
        from zoo.libs.maya.utils.files import ModFile
        for path in modFiles:
            mod = ModFile(path)
            # os.path.join(mod.resolvedScriptsPath, "zootoolspro") # zoo tools pro here
            # print(mod.resolvedScriptsPath)

        # Delete all the mod files
        for m in modFiles:
            logger.info("Deleting Mod: '{}'".format(m))
            os.remove(m)
