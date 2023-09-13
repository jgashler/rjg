import maya.cmds as mc
# import math


def vector_from_two_points(point_a=None, point_b=None):
    pos_a = get_world_pose(point_a)
    pos_b = get_world_pose(point_b)

    return [b-a for a, b in zip(pos_a, pos_b)]

def get_world_pose(pos):
    if isinstance(pos, list) or isinstance(pos, tuple) and len(pos) == 3:
        pass
    elif isinstance(pos, str) or isinstance(pos, unicode):
        pos = mc.xform(pos,
                         query=True,
                         worldSpace=True,
                         translation=True)
    else:
        mc.error('Must provide cartesian position or transform node for pos.')

    return pos

def vector_length(vector=[]):
    return pow(sum([pow(n, 2) for n in vector]), 0.5)

def distance_between(point_a=None, point_b=None):
    vector_ab = vector_from_two_points(point_a, point_b)
    distance = vector_length(vector_ab)
    return distance

