import maya.cmds as mc

'''
gets shapes under selected node
returns list of shapes, or None of there are no shapes
'''
def get_shapes(node):

    shape_list = mc.listRelatives(node, shapes=True, noIntermediate=True)

    if not shape_list:
        shape_list = mc.ls(node, shapes=True)

    if shape_list:
        return shape_list
    else:
        return None
    
    
'''
gets transform under selected node
returns the transform, or None of there are no shapes
'''    
def get_transform(node):
    if node:
        if mc.objectType(node) == 'transform':
            transform = node
        else:
            transform = mc.listRelatives(node, type="transform", parent=True)[0]

        return transform
    
    else:
        return None