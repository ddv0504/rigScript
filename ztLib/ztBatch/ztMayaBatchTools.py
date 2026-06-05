import os
import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
import shiboken2

# Batch Utilities
def playblast(output_path, width=1920, height=1080, frame=1, format='qt', compression='jpeg', quality=100, viewer=True, showOrnaments=True, offScreen=True, percent=100, *args):

    # Initialize Maya
    import maya.standalone
    maya.standalone.initialize( name='python' )
    print('Maya Initialized')
    import maya.cmds as cmds
    # Playblast
    # Set the current time slider range
    cmds.playblast( frame=frame, format=format, compression=compression, quality=quality, width=width, height=height, viewer=viewer, showOrnaments=showOrnaments, offScreen=offScreen, percent=percent, filename=output_path )
    print('Playblast Complete')

def render(*args):
    # Render
    cmds.render( render=True )
    print('Render Complete')

def renderSequence(*args):
    # Render Sequence
    cmds.render( renderSequence=True )
    print('Render Sequence Complete')


# Maya Batch Commands
def batchCommand(*args):
    # Batch Command
    print('Batch Command Complete')

# Command Line
def commandLine(*args):
    # Initialize Maya
    import maya.standalone
    maya.standalone.initialize( name='python' )
    print('Maya Initialized')
    
    # Command Line
    print('Command Line Complete')
# Playblast use commandline
def playblastCommandLine(*args):
    # Initialize Maya
    import maya.standalone
    maya.standalone.initialize( name='python' )
    print('Maya Initialized')
    
    # Playblast
    # Set the current time slider range
    cmds.playblast( frame=1, format='qt', compression='jpeg', quality=100, width=1920, height=1080, viewer=True, showOrnaments=True, offScreen=True, percent=100, filename='C:/Users/zt/Desktop/Playblast.mov' )
    print('Playblast Complete')

if __name__ == '__main__':
    playblast('C:/Users/zt/Desktop/Playblast.mov')
    