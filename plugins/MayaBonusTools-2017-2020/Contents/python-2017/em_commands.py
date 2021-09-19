# Copyright (C) 1997-2015 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized 
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE 
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.

"""
Support scripts for the EM shelf.
"""
from maya.debug.emCorrectnessTest import emCorrectnessTest
from maya.debug.emPerformanceTest import emPerformanceTest
from maya.debug.emPerformanceTest import emPerformanceOptions as emo
import subprocess
import maya.cmds as cmds
import maya.debug.graphStructure as graphStructure
import sys
import os
import tempfile

#======================================================================
#
class dotFormatting(object):
    """
    Helper class to provide DOT language output support.
    """
    @staticmethod
    def header():
        '''Print out a header defining the basic sizing information'''
        return 'digraph G\n{\n\tnslimit = 1.0 ;\n\tsize = "7.5,10" ;\n\tdpi = 600 ;\n\toverlap = scale;\n'
    @staticmethod
    def footer():
        '''Closes out the body section'''
        return '}\n'
    @staticmethod
    def node(node, nodeFormat=''):
        '''Creates a DOT node with the given format information'''
        return '\t"%s" %s;\n' % (node, nodeFormat)
    @staticmethod
    def filledFormat():
        '''Returns a string with DOT formatting information for a simple filled greenish-blue shape'''
        return '[style=filled, penwidth=4, color=\"0.0 0.5 1.0\"]'
    @staticmethod
    def connection(srcNode, dstNode):
        '''Mark a connection between two DOT nodes'''
        return '\t"%s" -> "%s" ;\n' % (srcNode, dstNode)

#======================================================================
#
def getCycleCluster( name ):
    """
    Find the cycle cluster a node is involved in, if any.

        name: Name of node to check
    """
    return cmds.evaluationManager( cycleCluster=name )

#======================================================================
#
def dumpClusterToDot( nodesInCycle, nodesToMark, fileName ):
    """
    Take all of the nodes in a cycle cluster and dump them out in
    a DOT graph format to the named file.

        nodesInCycle : List of the nodes involved in the cycle
        nodesToMark  : Nodes in the cycle to format specially
        fileName     : Name of output file
    """
    if len(nodesInCycle) == 0:
        return False

    dot = dotFormatting()
    out = open(fileName, 'w')
    out.write( dot.header() )

    for node in nodesInCycle:
        nodeFormat = ''
        if node in nodesToMark:
            nodeFormat = dot.filledFormat()
        out.write( dot.node(node, nodeFormat) )

    for parentNode in nodesInCycle:
        children = cmds.evaluationManager( downstreamFrom=parentNode )
        for childNode in children:
            if childNode in nodesInCycle:
                out.write( dot.connection(childNode, parentNode) ) #child is dependent node

    out.write( dot.footer() )
    return True

#======================================================================
#
def openFile(pFileName):
    """
    Open up an output file with the application assigned to it by the OS.

        pFileName : File to be opened up (usually a PDF)
    """
    try:
        if sys.platform == 'win32':
            os.startfile(pFileName)
        else:
            opener ='open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, pFileName])
    except Exception,ex:
        cmds.error('Error "when trying to open the file "%s".\n"%s"\n' % (pFileName, str(ex))
                 + 'Please make sure you have an installed application capable of opening this file.')

#======================================================================
#
def createClusterGraphFile():
    """
    Scan the selected nodes for cycle clusters. If any are found then dump
    the cycles out to both DOT and PDF files.
    """
    baseFileName = '_CycleCluster_'
    selectionList = cmds.ls( selection=True )

    if len(selectionList) == 0:
        cmds.error('You must select at least one object !')

    for selNode in selectionList:
        selFileNameDOT = os.path.join( tempfile.gettempdir(), baseFileName + '.dot' )
        selFileNamePDF = os.path.join( tempfile.gettempdir(), baseFileName + '.pdf' )
        if dumpClusterToDot( getCycleCluster(selNode), selectionList, selFileNameDOT ):
            command = 'dot -Tpdf {} -o {}'.format(selFileNameDOT, selFileNamePDF)

            try:
                subprocess.call(command.split(), shell=False)
            except Exception,ex:    
                cmds.error('Error when trying to execute dot command.\n"%s"\n' % str(ex) 
                         + 'Please make sure Graphviz is installed and is in your system path.' )

            openFile(selFileNamePDF)

            break #do just one
        else:
            print 'Node {} is not involved in a cycle'.format(selNode)

#======================================================================
#
def createEvaluationGraphFile():
    """
    Scan the entire evaluation graph and dump out a DOT and PDF format
    description of the graph.
    """
    outDOT = os.path.join(tempfile.gettempdir(), u'EvaluationGraph.dot')
    outPDF = os.path.join(tempfile.gettempdir(), u'EvaluationGraph.pdf')

    currentSceneGraph = graphStructure.graphStructure(None, False, True)
    currentSceneGraph.writeAsDot( outDOT )
    command = 'dot -Tpdf {} -o {}'.format(outDOT, outPDF)

    try:
        subprocess.call(command.split(), shell=False)
    except Exception,ex:    
        cmds.error('Error when trying to execute dot command.\n"%s"\n' % str(ex) 
                 + 'Please make sure Graphviz is installed and is in your system path.' )

    openFile(outPDF)

#======================================================================
#
def toggleSelectedDGNodeHasNoEffectWithNormalMode():
    """
    If the first selected DG node is in "HasNoEffect" mode then put all
    selected nodes into "Normal" mode, otherwise put all selected nodes
    into "HasNoEffect" mode.
    """
    selectionList = cmds.ls( selection=True )
    newState = 1

    if len(selectionList) > 0:
        if cmds.getAttr( selectionList[0]+".nodeState" ) == 1:
            newState = 0

    for name in selectionList:
        cmds.setAttr( name+".nodeState", newState )

#======================================================================
#
def runEMPerformanceTest():
    """
    Run the emPerformanceTest on the current scene. The resulting
    output will be shown in the script editor window.

    The raw performance data consists of two rows, the first containing the
    names of the data collected and the second consisting of the values
    for each data collection item.

    This raw list is filtered so that only the most useful data is shown.
    This includes the frames per second for playback in each of DG, EMS,
    and EMP modes. For the unfiltered results see the emPerformanceTest
    script.
    """
    options = emo()
    options.setViewports( [emo.VIEWPORT_2] )
    options.setReportProgress( True )
    options.setTestTypes( [emo.TEST_PLAYBACK] )
    csv = emPerformanceTest(None, 'csv', options)
    rowDictionary = dict(zip(csv[0].split(',')[1:], csv[1].split(',')[1:]))

    startFrameTitle = 'Start Frame'
    endFrameTitle = 'End Frame'
    rateTitles = { 'VP2 Playback DG Avg'  : 'DG '
                 , 'VP2 Playback EMS Avg' : 'EMS'
                 , 'VP2 Playback EMP Avg' : 'EMP'
                 }

    frameCount = 0.0
    # No frame range so only the time taken can be reported
    rateFormat = '%g seconds for playback'
    if startFrameTitle in rowDictionary and endFrameTitle in rowDictionary:
        try:
            frameCount = float(rowDictionary[endFrameTitle]) - float(rowDictionary[startFrameTitle]) + 1.0
            rateFormat = '%g fps'
        except Exception:
            print 'WARNING: Frame range (%s, %s) not recognized' % (rowDictionary[endFrameTitle]
                                                                  , rowDictionary[startFrameTitle])

    print '\nPlayback Speeds'
    print '=' * 15
    for (title, name) in rateTitles.iteritems():
        try:
            playbackTime = float(rowDictionary[title])
            rate = playbackTime if frameCount == 0.0 else frameCount/playbackTime
            rateStr = rateFormat % rate
        except Exception, ex:
            rateStr = 'Unknown'
        print '    %s = %s' % (name, rateStr)

#======================================================================
#
def runEMCorrectnessTest():
    """
    Run the emCorrectnessTest on the current scene. The resulting
    output will be shown in the script editor window.
    """
    results = emCorrectnessTest(verbose=True, modes=['ems','emp','emp+deformer','ems-dynamics'], maxFrames=300)
    print  '\nEM Correctness results'
    print  '=' * 22
    modeNames = {'ems':'EM Serial'
               , 'emp':'EM Parallel'
               , 'emp+deformer':'EM Parallel with Deformer Evaluator enabled'
               , 'ems-dynamics':'EM Serial with Dynamics fallback disabled'}
    for (resultType,result) in results.iteritems():
        if len(result[1]) > 0:
            print '%s Changes' % modeNames[resultType]
            print '    ' + '\n    '.join( result[1] )

    # Put the summary at the end for easier reading
    for (resultType,result) in results.iteritems():
        print '%d change%s in %s' % (len(result[1])
                                  , ['s',''][len(result[1])==1]
                                  ,  modeNames[resultType])

