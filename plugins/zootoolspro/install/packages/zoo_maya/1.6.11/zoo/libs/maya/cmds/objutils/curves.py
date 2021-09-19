import maya.mel as mel
from maya import cmds


def createCurveContext(degrees=3, bezier=0):
    """Enters the create curve context (user draws cvs).  Uses mel. Cubic Has option for curve degrees.

    More options can be added later.

    :param degrees: The curve degrees of the curve.  3 is Bezier, 1 is linear.
    :type degrees: int
    :param bezier: when the curves has 3 degrees make the curve bezier.  Default 0 is cubic.
    :type bezier: int
    """
    mel.eval("curveCVToolScript 4;\n"
             "curveCVCtx -e -d {} -bez {} `currentCtx`;".format(str(degrees), str(bezier)))


def splineIkHandleContext(spans=2):
    """ Create Spline Ik Handle

    :param spans:
    :type spans:
    :return:
    :rtype:
    """
    cmds.IKSplineHandleTool()
    cmds.ikSplineHandleCtx("ikSplineHandleContext", e=1, numSpans=spans, priorityH=1, weightH=1, poWeightH=1,
                           autoPriorityH=0, snapHandleH=1, forceSolverH=1, stickyH="off",
                           createCurve=1, simplifyCurve=1, rootOnCurve=1, twistType="linear", createRootAxis=0,
                           parentCurve=1, snapCurve=0, rootTwistMode=0)

