import maya.cmds as mc
from importlib import reload

def match_pose(node, translate=None, rotate=None, scale=None):
    print(type(translate))

    if isinstance(translate, list) or isinstance(translate, tuple):
        if len(translate) == 3:
            mc.setAttr(node + ".translate", *translate)
        else:
            mc.error("Please provide x, y, z translate values.")
    elif not translate:
        pass
    elif mc.objExists(translate):
        src = mc.xform(translate, query=True, worldSpace=True, translation=True)
        mc.xform(node, worldSpace=True, translation=src)
    else:
        mc.error("Input for translate not valid. Please give coordinates or provide a valid object.")

    if isinstance(rotate, list) or isinstance(rotate, tuple):
        if len(rotate) == 3:
            mc.setAttr(node + ".rotate", *rotate)
        else:
            mc.error("Please provide x, y, z rotate values.")
    elif not rotate:
        pass
    elif mc.objExists(rotate):
        src = mc.xform(rotate, query=True, worldSpace=True, rotation=True)
        mc.xform(node, worldSpace=True, rotation=src)
    else:
        mc.error("Input for rotate not valid. Please give coordinates or provide a valid object.")

    if isinstance(scale, list) or isinstance(scale, tuple):
        if len(scale) == 3:
            mc.setAttr(node + ".scale", *scale)
        else:
            mc.error("Please provide x, y, z scale values.")
    elif not scale:
        pass
    elif mc.objExists(scale):
        src = mc.xform(scale, query=True, worldSpace=True, scale=True)
        mc.xform(node, worldSpace=True, scalen=src)
    else:
        mc.error("Input for scale not valid. Please give coordinates or provide a valid object.")