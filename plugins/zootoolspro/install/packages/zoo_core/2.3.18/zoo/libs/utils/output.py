import sys
def _zooLoaded():
    if sys.version_info[0] < 3:
        import imp
        try:
            imp.find_module('zoo')
            found = True
        except ImportError:
            found = False
    else:
        import importlib
        spam_spec = importlib.util.find_spec("zoo")
        found = spam_spec is not None

    return found


if _zooLoaded():
    from zoo.core.util import env

if env.isInMaya():
    from maya.api import OpenMaya as om2
elif env.isInBlender():
    pass


# todo maybe put this into core?
def displayInfo(txt, operator=None):
    """ Display info based on application

    :param txt: Info text
    :param operator: Operator for blender. Required if using blender
    :type operator: bpy.types.Operator
    :return:
    """
    if _zooLoaded():
        if env.isInMaya():
            om2.MGlobal.displayInfo(txt)
        elif env.isInBlender() and operator is not None:
            operator.report({"INFO"}, txt)
        else:
            print("Info: {}".format(txt))
    else:
        print("Info: {}".format(txt))


def displayWarning(txt, operator=None):
    """ Display Warning based on application

    :param txt: warning
    :param operator: Operator for blender. Required if using blender
    :type operator: bpy.types.Operator
    :return:
    """

    if _zooLoaded():
        if env.isInMaya():
            om2.MGlobal.displayWarning(txt)
        elif env.isInBlender() and operator is not None:
            operator.report({"WARNING"}, txt)
        else:
            print("Warning: {}".format(txt))
    else:
        print("Warning: {}".format(txt))


def displayError(txt, operator=None):
    """ Display Error based on application

    :param txt: error
    :param operator: Operator for blender. Required if using blender
    :type operator: bpy.types.Operator
    :return:
    """
    if _zooLoaded():
        if env.isInMaya():
            om2.MGlobal.displayError(txt)
        elif env.isInBlender() and operator is not None:
            operator.report({"ERROR"}, txt)
        else:
            print("ERROR: {}".format(txt))
    else:
        print("ERROR: {}".format(txt))

