import maya.cmds as mc
import importlib

import rjg.build.buildTest as buildTest
importlib.reload(buildTest)

def partTestSph(name='partHoinky'):
    return buildTest.buildSphere(name)