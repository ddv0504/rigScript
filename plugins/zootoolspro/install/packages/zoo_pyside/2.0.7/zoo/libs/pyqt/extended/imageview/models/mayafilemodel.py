import os
import unicodedata
import textwrap
from functools import partial

from zoovendor.Qt import QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt.extended.imageview import items, model
from zoo.libs.pyqt.extended.imageview.items import TreeItem
from zoo.libs.utils import path, zlogging
from zoo.preferences import prefutils
from zoo.libs.zooscene import zooscenefiles
from zoovendor.six import string_types

logger = zlogging.getLogger(__name__)


class FileItem(object):
    def __init__(self, directory="", thumbnail="", file="", toolTip=""):
        self.directory = directory
        fileSplit = file.split('.')
        self.fileName = fileSplit[0]
        self.toolTip = toolTip

        self.thumbnail = thumbnail
        self._initThumbnail()
        self.ext = fileSplit[1]

    def _initThumbnail(self):
        self.thumbnail = self.thumbnail or "{}.jpg".format(self.fileName)
        if not path.isImage(os.path.join(self.directory, self.thumbnail)):
            self.thumbnail = ""

    def thumbnailPath(self):
        if self.thumbnail:
            return os.path.join(self.directory, self.thumbnail)

    def filePath(self):
        return os.path.join(self.directory, "{}.{}".format(self.fileName, self.ext))


class MayaFileModel(model.ItemModel):
    parentClosed = QtCore.Signal(bool)
    doubleClicked = QtCore.Signal(str)
    itemSelectionChanged = QtCore.Signal(str, object)
    refreshRequested = QtCore.Signal()

    def __init__(self, view, directory=None, extensions=None, chunkCount=20, uniformIcons=False, extVis=False):
        """ Overridden base model to handle loading of the ThumbnailView widget data eg. specific files/images

        This class is the most basic form of the Thumbnail model which is attached to a ThumbnailView

        A directory given and is populated with "png", "jpg", or "jpeg" images.

        Tooltips are also generated from the file names

        This class can be overridden further for custom image loading in subdirectories such as .zooScene files.

        :param view: The viewer to assign this model data?
        :type view: thumbwidget.ThumbListView
        :param directory: The directory full path where the .zooScenes live
        :type directory: str
        :param chunkCount: The number of images to load at a time into the ThumbnailView widget
        :type chunkCount: int
        :param extensions: The image file extensions to override, otherwise will be ["png", "jpg", "jpeg"]
        :type extensions: list of basestring
        :param uniformIcons: False keeps the images non-square.  True the icons will be square, clipped on longest axis
        :type uniformIcons: bool
        """
        super(MayaFileModel, self).__init__(parent=view)
        self.view = view
        self.extensions = extensions
        self.chunkCount = chunkCount
        self.currentFilesList = []  # the files loaded in the viewer, empty while initializing
        self.infoDictList = None  # usually used for generating tooltips
        self.toolTipList = None  # list of tooltips to match each images
        self.currentImage = None  # the current image name selected (no image highlighted on creation)
        self.fileItems = None  # type: list[FileItem]
        self._nameExtVis = extVis  # Show name extensions
        self.directory = None
        self.themePref = prefutils.coreInterface()
        self.threadPool = QtCore.QThreadPool.globalInstance()
        self.lastFilter = ""
        self.uniformIcons = uniformIcons
        self.dynamicLoading = True  # Dynamic icon loading
        self.items = []  # type: list[TreeItem]
        self._emptyThumbnail = iconlib.iconPath("emptyThumbnail")["sizes"][200]["path"]
        self.filterOutSuffixList = []  # for filtering out suffixes of certain files.  Used with renderers

        # load the images
        if directory is not None:
            self.setDirectory(directory, True)

    def setDirectory(self, directory, refresh=True):
        """Used to set or change the directory"""
        self.directory = directory
        if refresh:
            self.refreshList()

    def refreshList(self):
        """ Refreshes the icon list if contents have been modified, does not change the root directory
        """
        self.view.setUpdatesEnabled(False)
        self.clear()
        self.refreshModelData()
        self.loadData()
        self.view.setUpdatesEnabled(True)

    def setFilterSuffixList(self, filterOutSuffixList):
        """Sets the filterOutSuffixList for filtering out certain files by suffix, ie for renderers"""
        self.filterOutSuffixList = filterOutSuffixList

    def _infoDictionaries(self):
        """Returns a list of info dictionaries for each .zooScene file.

        These dictionaries contain information such as author, tag, descriptions etc

        Overrides base class

        :return infoDictList: A list of info dictionaries for each .zooScene file
        :rtype infoDictList: list(dict)
        """
        return  # ???
        return zooscenefiles.infoDictionaries(self.fileItems, self.directory)

    def clear(self):
        """Clears the images and data from the model, usually used while refreshing
        """
        # remove any threads that haven't started yet
        self.threadPool.clear()

        while not self.threadPool.waitForDone():
            continue
        # clear any items, this is necessary to get python to GC alloc memory
        self.items = []
        self.loadedCount = 0
        self.currentFilesList = []
        super(MayaFileModel, self).clear()

    def fileList(self):
        """Updates the self.fileItems, overridden method

        :param filterOutSuffixList: A list of file suffixes that will be skipped, eg ["redshift", "renderman"]
        :type filterOutSuffixList: list(str)
        """
        self.extensions = ["ma", "mb"]
        if not isinstance(self.extensions, list):
            raise ValueError("Extensions must be list, \"{}\" type given \"{}\" ".format(type(self.extensions),
                                                                                         self.extensions))

        dirs = path.directories(self.directory, absolute=True)

        self.fileItems = []
        for d in dirs:
            for file in path.filesByExtension(d, self.extensions, sort=True):
                if self.filterOutSuffixList:
                    noExtension = os.path.splitext(file)[0]
                    suffix = noExtension.split("_")[-1]
                    if suffix in self.filterOutSuffixList:
                        continue
                self.fileItems.append(FileItem(d, file=file))

    def filterList(self, text, tag=None):
        """ Returns a list of ints of rows that gets shown or hidden in the search

        :param text:
        :type text:
        :param tag: Type of tag to search through. Eg. File name, author, description etc
        :type tag: basestring or list
        :return:
        :rtype:
        """
        filterList = list()
        tag = tag or "filename"
        if isinstance(tag, string_types):
            tag = [tag]

        fileNames = self.fileNames()
        for i in range(len(self.fileItems)):
            for t in tag:
                if t == "filename":
                    for j, fileName in enumerate(fileNames):
                        if text.lower() in fileName.lower():
                            filterList.append(j)
                else:
                    pass
                    # todo
                    # if text.lower() in self.infoDictList[i][t.lower()].lower():
                    #     filterList.append(i)

        for i in range(len(fileNames)):
            self.view.thumbWidget.setRowHidden(i, i not in filterList)  # Show row if not in filterList

        self.lastFilter = text

        return filterList

    def refreshModelData(self):
        """Refreshes the model's data

        TODO: Needs to create/recreate the thumbnail lists, tooltips and infoDict data
        """
        self.fileList()  # updates self.fileNameList
        # self.infoDictList = self._infoDictionaries()
        # self.currentFilesList = self._thumbnails()

        # self._toolTips()  # generates self.toolTipList # todo: add this into fileList
        self.refreshRequested.emit()

    def lazyLoadFilter(self):
        """Breaks up the lists self.currentFilesList, self.fileNameList, self.toolTipList for lazy loading.

        Can be overridden, usually to choose if the display names should have extensions or not
        Default is no extensions on display names

        :rtype: list[FileItem]
        """
        if len(self.fileItems) < self.loadedCount:
            filesToLoad = self.fileItems
        else:
            filesToLoad = self.fileItems[self.loadedCount: self.loadedCount + self.chunkCount]

        return filesToLoad

    def fileNames(self):
        """ Just get the filenames from file

        :return:
        :rtype:
        """
        return [n.fileName for n in self.fileItems]

    def setExtensionVisibility(self, show):
        """ Show/Hide extension visibility in the item names
        """
        self._nameExtVis = show

    def loadData(self):
        """ Overridden method that prepares the images for loading and viewing.

        Is filtered first via self.lazyLoadFilter()

        From base class documentation:

            Lazy loading happens either on first class initialization and any time the vertical bar hits the max value,
            we then grab the current the new file chunk by files[self.loadedCount: loadedCount + self.chunkCount] that
            way we are only loading a small amount at a time.
            Since this is an example of how to use the method , you can approach it in any way you wish but for each item you
            add you must initialize a item.BaseItem() or custom subclass and a item.treeItem or subclass which handles the
            qt side of the data per item

        """

        if self.lastFilter != "":  # Don't load any new data if theres a search going on
            return

        filesToLoad = self.lazyLoadFilter()

        loaded = self.loadedCount
        # Load the files
        for i, f in enumerate(filesToLoad):
            thumbnail = f.thumbnailPath() or self._emptyThumbnail
            workerThread = items.ThreadedIcon(iconPath=thumbnail)
            # create an item for the image type
            # todo: maybe use BaseItem instead of FileItem
            it = items.BaseItem(name=f.fileName, iconPath=thumbnail, description=f.toolTip, filePath=f.filePath())

            # it.metadata = self.infoDictList[loaded + i]  # todo
            qitem = self.createItem(item=it)
            workerThread.signals.updated.connect(partial(self.setItemIconFromImage, qitem))
            self.parentClosed.connect(workerThread.finished)

            it.iconThread = workerThread

            if self.dynamicLoading is False:
                self.threadPool.start(workerThread)
            self.loadedCount += 1

        if len(filesToLoad) > 0:
            self.reset()

    def createItem(self, item):
        """Custom wrapper Method to create a ::class`items.TreeItem`, add it to the model items and class appendRow()
        :param item:
        :type item: ::class:`baseItem`
        :return:
        :rtype: ::class:`items.TreeItem`
        """
        tItem = TreeItem(item=item, themePref=self.themePref, squareIcon=self.uniformIcons)
        self.items.append(tItem)
        self.appendRow(tItem)
        return tItem

    def itemTexts(self):
        """ Get all the item texts and put them into a generator

        :return:
        :rtype:
        """
        return (item.itemText() for item in self.items)

    def indexFromText(self, text):
        """ Get Item from text

        :param text:
        :type text:
        :return:
        :rtype:
        """
        for it in self.items:
            if it.itemText() == text:
                return self.indexFromItem(it)

    def setUniformItemSizes(self, enabled):
        """ Set uniform item sizes

        Make the items square if true, if false it will keep the images original aspect ratio for the items

        :param enabled:
        :type enabled:
        :return:
        :rtype:
        """
        self.uniformIcons = enabled
        for it in self.items:
            it.squareIcon = enabled

    def setItemIconFromImage(self, item, image):
        """Custom method that gets called by the thread

        :param item:
        :type item: :class:`TreeItem`
        :param image: The Loaded QImage
        :type image: QtGui.QImage
        """
        item.applyFromImage(image)

    def doubleClickEvent(self, modelIndex, item):
        """Gets called by the listview when an item is doubleclicked
        :param modelIndex:
        :type modelIndex: QtCore.QModelIndex
        :param item:
        :type item: TreeItem
        :return self.currentImage:  The current image with it's name and file extension
        :rtype self.currentImage:  str
        """
        self.currentImage = item._item.name
        self.doubleClicked.emit(self.currentImage)
        return self.currentImage

    def onSelectionChanged(self, modelIndex, item):
        """Gets called by the listview when an item is changed, eg left click or rightclick
        :param modelIndex:
        :type modelIndex: QtCore.QModelIndex
        :param item:
        :type item: TreeItem
        """
        try:  # can error while renaming files and the change no longer exists so ignore if so
            self.currentImage = item._item.name
            self.itemSelectionChanged.emit(self.currentImage, item._item)
            return self.currentImage
        except AttributeError:
            pass

    def closeEvent(self, event):
        """Closes the model

        :param event:
        :type event:
        """
        if self.qModel is not None:
            self.qModel.clear()
            self.qModel.parentClosed.emit(True)
        super(MayaFileModel, self).closeEvent(event)
