import os

import maya.api.OpenMaya as om2

from zoovendor.Qt import QtWidgets

from zoo.libs.utils import filesystem
from zoo.apps.preferencesui import prefmodel
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt import uiconstants as uic

from zoo.preferences.core import preference
from zoo.apps.model_assets import assetconstants as ac
from zoo.apps.model_assets import assetdirectories


class ZooMayaScenesPrefsWidget(prefmodel.SettingWidget):
    categoryTitle = "Maya Scenes"  # The main title of the Maya Scenes preferences section and also side menu item

    def __init__(self, parent=None, setting=None):
        """Builds the Maya Scenes Section of the preferences window.

        :param parent: the parent widget
        :type parent: Qt.QtWidgets
        """
        super(ZooMayaScenesPrefsWidget, self).__init__(parent, setting)
        # Maya Scenes Pref Object self.lsPrefsObj stores and saves all the .prefs json data
        self.prefsData = preference.findSetting(ac.RELATIVE_MAYA_PREFS_FILE, None)
        # Check assets folders and updates if they don't exist
        self.prefsData = assetdirectories.buildUpdateMayaScenesPrefs(self.prefsData)
        self.uiWidgets()  # Builds the widgets
        self.uiLayout()  # Adds widgets to the layouts
        # Save, Apply buttons are automatically connected to the self.serialize() method
        # Reset Button is automatically connected to the self.revert() method
        self.uiConnections()

    # -------------------
    # WIDGETS LAYOUT
    # -------------------

    def uiWidgets(self):
        """Builds all the widgets needed in the GUI"""
        # Retrieve data from user's .prefs json -------------------------
        mayaScenesPath = self.prefsData["settings"][ac.PREFS_KEY_MAYA_SCENES]
        # Maya Scenes Path -----------------------------------------
        toolTip = "The location of the Maya Scenes. \n" \
                  "Folder with the Maya Scenes folders."
        self.mayaScenesLbl = elements.Label("Maya Scenes Folder", parent=self, toolTip=toolTip)
        self.mayaScenesTxt = elements.StringEdit(label="",
                                                editText=mayaScenesPath,
                                                toolTip=toolTip)
        toolTip = "Browse to change the Maya Scenes folder."
        self.mayaScenesBrowseSetBtn = elements.styledButton("",
                                                           "browse",
                                                           toolTip=toolTip,
                                                           parent=self,
                                                           minWidth=uic.BTN_W_ICN_MED)
        toolTip = "Reset the Maya Scenes folder to it's default location."
        self.mayaScenesResetBtn = elements.styledButton("",
                                                       "refresh",
                                                       toolTip=toolTip,
                                                       parent=self,
                                                       minWidth=uic.BTN_W_ICN_MED)
        toolTip = "Explore, open the directory in your OS browser."
        self.mayaScenesExploreBtn = elements.styledButton("",
                                                         "globe",
                                                         toolTip=toolTip,
                                                         parent=self,
                                                         minWidth=uic.BTN_W_ICN_MED)

    def uiLayout(self):
        """Adds all the widgets to layouts for the GUI"""
        mainLayout = elements.vBoxLayout(self,
                                         margins=(uic.WINSIDEPAD, uic.WINTOPPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Maya Scenes Path Layout ------------------------------------
        mayaScenesPathLayout = elements.hBoxLayout()
        mayaScenesPathLayout.addWidget(self.mayaScenesBrowseSetBtn)
        mayaScenesPathLayout.addWidget(self.mayaScenesResetBtn)
        mayaScenesPathLayout.addWidget(self.mayaScenesExploreBtn)
        # Path Grid Top Layout ----------------------------------------------
        pathGridLayout = elements.GridLayout(
            margins=(0, 0, 0, uic.SXLRG),
            columnMinWidth=(0, 120),
            columnMinWidthB=(2, 120))
        pathGridLayout.addWidget(self.mayaScenesLbl, 0, 0)
        pathGridLayout.addWidget(self.mayaScenesTxt, 0, 1)
        pathGridLayout.addLayout(mayaScenesPathLayout, 0, 2)
        # Add to Main Layout  -----------------------------------
        mainLayout.addLayout(pathGridLayout)
        mainLayout.addStretch(1)

    # -------------------
    # LOGIC
    # -------------------

    def getDefaultFolders(self):
        """Returns the default folder paths as created from the global user preferences directory

        userPreferences path + /assets/ + maya_scenes_folderNames:

            userPath/zoo_preferences/assets/maya_scenes

        :return mayaScenesDefaultPath: The full path of the userPreferences + assets directory + maya scenes directory
        :rtype mayaScenesDefaultPath: str
        """
        userPrefsPath = str(preference.root("user_preferences"))
        assetsFolderPath = os.path.join(userPrefsPath, ac.ASSETS_FOLDER_NAME)
        mayaScenesDefaultPath = os.path.join(assetsFolderPath, ac.MAYA_FOLDER_NAME)
        return mayaScenesDefaultPath

    def setMayaScenesPathDefault(self):
        """Sets the UI widget path text to the default Maya Scenes path"""
        mayaScenesDefaultPath = self.getDefaultFolders()[1]
        self.mayaScenesTxt.setText(mayaScenesDefaultPath)

    def browseChangeMayaScenesFolder(self):
        """Browse to change/set the Maya Scenes Folder"""
        directoryPath = self.mayaScenesTxt.text()
        if not os.path.isdir(directoryPath):  # if dir doesn't exist set to home directory
            directoryPath = os.environ['HOME']
        newDirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Set the `Maya Scenes` folder", directoryPath)
        if newDirPath:
            self.mayaScenesTxt.setText(newDirPath)

    def exploreMayaScenesFolder(self):
        """Opens an os window for browsing files on disk in the users operating system"""
        filesystem.openDirectory(self.mayaScenesTxt.text())
        om2.MGlobal.displayInfo("OS window opened to the `Maya Scenes` folder location")

    # -------------------
    # SAVE, APPLY, RESET
    # -------------------

    def serialize(self):
        """ Save the current settings to the preference file, used for both Apply and Save buttons

        Automatically connected to the preferences window buttons via model.SettingWidget
        """
        if not self.prefsData.isValid():
            om2.MGlobal.displayError("The preferences object is not valid")
            return
        self.prefsData["settings"][ac.PREFS_KEY_MAYA_SCENES] = self.mayaScenesTxt.text()
        path = self.prefsData.save(indent=True)  # save and format nicely
        om2.MGlobal.displayInfo("Success: Maya Scenes preferences Saved To Disk '{}'".format(path))

    def revert(self):
        """Reverts to the previous settings, resets the GUI to the previously saved settings

        Automatically connected to the preferences window revert button via model.SettingWidget
        """
        self.mayaScenesTxt.setText(self.prefsData["settings"][ac.PREFS_KEY_MAYA_SCENES])

    def adminSave(self):
        """Method for admin saving internally to Zoo Tools Pro, not connected
        """
        pass

    # -------------------
    # CONNECTIONS
    # -------------------

    def uiConnections(self):
        """Setup the custom connections for the Maya Scenes Preferences GUI

        # Save, Apply buttons are automatically connected to the self.serialize() methods
        # Reset Button is automatically connected to the self.revert() method
        """
        # reset paths small buttons
        self.mayaScenesResetBtn.clicked.connect(self.setMayaScenesPathDefault)
        # browse paths small buttons
        self.mayaScenesBrowseSetBtn.clicked.connect(self.browseChangeMayaScenesFolder)
        # explore paths small buttons
        self.mayaScenesExploreBtn.clicked.connect(self.exploreMayaScenesFolder)
