from zoo.apps.uninstallerui import core
from zoo.libs.maya.qt import mayaui
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets import elements
from zoovendor.Qt import QtWidgets, QtCore


class UninstallerUi(elements.ZooWindow):

    def __init__(self, title="Uninstall", parent=None):
        super(UninstallerUi, self).__init__(title=title, parent=parent)

        self.core = core.UninstallerCore()

        self.connections()

    def _initUi(self):
        """

        :return:
        """
        super(UninstallerUi, self)._initUi()
        self.mainLayout = elements.vBoxLayout(margins=(15, 15, 15, 15))
        self.setMainLayout(self.mainLayout)

        buttonLayout = elements.hBoxLayout()
        checkboxLayout = elements.vBoxLayout(margins=(0, 0, 10, 0))

        self.titleLabel = elements.HeaderLabel(text="Uninstall Zoo Tools Pro",
                                               parent=self)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(QtWidgets.QLabel("Thank you for using Zoo Tools Pro. You may re-install at any time."))
        self.mainLayout.addSpacing(15)
        self.zootoolsChkBox = elements.LabelDividerCheckBox(text="Zoo Tools Pro", checked=True)
        checkboxLayout.addWidget(self.zootoolsChkBox)
        checkboxLayout.addWidget(QtWidgets.QLabel("Scripts & Module"))
        checkboxLayout.addSpacing(10)
        self.prefsChkBox = elements.LabelDividerCheckBox(text="Preferences: Preferences", checked=True)
        checkboxLayout.addWidget(self.prefsChkBox)
        checkboxLayout.addWidget(QtWidgets.QLabel("Preferences"))
        checkboxLayout.addSpacing(10)
        self.assetsChkBox = elements.LabelDividerCheckBox(text="Preferences: Assets", checked=False)
        checkboxLayout.addWidget(self.assetsChkBox)
        checkboxLayout.addWidget(QtWidgets.QLabel("The assets"))
        checkboxLayout.addSpacing(10)
        self.customPackagesChkBox = elements.LabelDividerCheckBox(text="Custom Packages", checked=False)
        checkboxLayout.addWidget(self.customPackagesChkBox)
        checkboxLayout.addWidget(QtWidgets.QLabel("Custom Packages"))
        checkboxLayout.addSpacing(20)
        checkboxLayout.addStretch(1)

        self.mainLayout.addLayout(checkboxLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.uninstallBtn = elements.styledButton(text="Uninstall", icon="trash")
        self.cancelBtn = elements.styledButton(text="Cancel", icon="crossXFat")
        buttonLayout.addWidget(self.uninstallBtn)
        buttonLayout.addWidget(self.cancelBtn)

    def connections(self):
        """ Connections

        :return:
        """
        self.uninstallBtn.leftClicked.connect(self.uninstall)
        self.cancelBtn.leftClicked.connect(self.close)

    def uninstall(self):
        """ Uninstall button

        :return:
        """
        oldText = self.uninstallBtn.text()
        mayaWindow = mayaui.getMayaWindow()
        zootools = self.zootoolsChkBox.checkbox.isChecked()
        assets = self.assetsChkBox.checkbox.isChecked()
        prefs = self.prefsChkBox.checkbox.isChecked()
        customPackages = self.customPackagesChkBox.checkbox.isChecked()
        self.uninstallBtn.setText("Uninstalling...")
        uninstalled = self.core.uninstall(zootools, assets, prefs, customPackages)
        if uninstalled:
            flags = QtWidgets.QMessageBox.StandardButton.Ok

            QtWidgets.QMessageBox.information(mayaWindow,
                                              "Uninstalled ZooToolsPro",
                                              "Zoo Tools Pro has been uninstalled. Thank you for using ZooToolsPro.",
                                              flags)
        self.uninstallBtn.setText(oldText)
