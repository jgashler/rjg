import maya.cmds as mc
from importlib import reload
from collections import OrderedDict

'''
moves all transform attributes of node to those specified

param node: node to transform
param translate: object, list, or tuple. if list or tuple, must be of length 3 (x, y, z) and translate will be changed to those values in world space
                 if object, node will inherit all worldspace translate values of the object
param rotate: same as translate, but applied to node's rotation
param scale: same as translate, but applied to node's scale
'''
def match_pose(node, translate=None, rotate=None, scale=None):
    #print(type(translate))

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

'''
populates an OrderedDict with {node : world space matrix}
'''
def read_pose(nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]
    pose_dict = OrderedDict()

    for node in nodes:
        pose_dict[node] = mc.xform(node, q=True, worldSpace=True, matrix=True)
    return pose_dict

'''
sets worldspace matrix of an object
'''
def set_pose(node, matrix):
    mc.xform(node, worldSpace=True, matrix=matrix)

'''
given a curve and a percentage along the curve, return the worldspace position of that point on the curve
'''
def findPosOnCurve(curve, u_val):
    pci = mc.createNode("pointOnCurveInfo", n='tmp_pci')
    mc.connectAttr(curve + 'Shape.worldSpace[0]', pci + '.inputCurve')
    mc.setAttr(pci + '.turnOnPercentage', 1)
    mc.setAttr(pci + '.parameter', u_val)
    pos = mc.getAttr(pci + '.position')[0]
    mc.delete(pci)
    return pos