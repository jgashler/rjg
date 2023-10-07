import maya.cmds as mc
from importlib import reload

import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr
reload(rCtrl)
reload(rAttr)

def get_ctrl_types():
    type_dict = {}
    for x in mc.ls('*.ctrlDict'):
        ctrl = rCtrl.Control(ctrl=x.split('.')[0])
        if ctrl.rig_type in type_dict:
            type_dict[ctrl.rig_type].append(ctrl.ctrl)
        else:
            type_dict[ctrl.rig_type] = [ctrl.ctrl]

    return type_dict

def add_color_attrs():
    attr_util = rAttr.Attribute(add=False)
    type_dict = get_ctrl_types()

    if mc.objExists('M_global_CTRL'):
        par = ('M_global_CTRL')
    else:
        par = 'RIG'

    c_ctrl = rCtrl.Control(parent=par, shape='gear_3D', side=None, name='color', suffix='CTRL', axis='y', group_type=None, rig_type='global')
    attr_util.lock_and_hide(node=c_ctrl.ctrl)

    c_shapes = mc.listRelatives(c_ctrl.ctrl, shapes=True)
    for shape in c_shapes:
        mc.setAttr(shape + '.overrideEnabled', 1)
        mc.setAttr(shape + '.overrideRGBColors', 1)
    mc.setAttr(shape + '.overrideColorRGB', 1, 0, 0)
    mc.setAttr(shape + '.overrideColorRGB', 0, 1, 0)
    mc.setAttr(shape + '.overrideColorRGB', 0, 0, 1)

    for type, ctrl_list in type_dict.items():
        rAttr.Attribute(node=c_ctrl.ctrl, type='separator', name=type)
        color = rAttr.Attribute(node=c_ctrl.ctrl, type='double3', value=0, keyable=True, min=0, max=1, name=type + 'Color', children_name='RGB')
        for ctrl in ctrl_list:
            for shape in mc.listRelatives(ctrl, shapes=True, type='nurbsCurve'):
                mc.setAttr(shape + '.overrideEnabled', 1)
                mc.setAttr(shape + '.overrideRGBColors', 1)
                mc.connectAttr(color.attr, shape + '.overrideColorRGB')

    set_color_defaults(c_ctrl.ctrl)

def set_color_defaults(ctrl):
    color_dict = {
        'gimbal'    : (0.00, 0.45, 0.00),
        'root_01'   : (0.00, 1.00, 0.00),
        'root_02'   : (0.00, 1.00, 0.10),
        'global'    : (1.00, 0.25, 1.00),
        'pivot'     : (1.00, 0.25, 0.00),
        'primary'   : (1.00, 1.00, 0.00),
        'bendy'     : (1.00, 0.20, 0.40),
        'tangent'   : (0.85, 0.15, 0.00),
        'offset'    : (0.75, 0.00, 0.00),
        'pv'        : (0.00, 1.00, 1.00),
        'fk'        : (0.00, 0.00, 1.00),
        'secondary' : (1.00, 0.20, 0.20),
        'l_eye'     : (0.10, 0.10, 0.70),
        'r_eye'     : (0.70, 0.10, 0.10),
        'c_eye'     : (0.70, 0.70, 0.10),
    }

    for type, value in color_dict.items():
        color = '{}.{}Color'.format(ctrl, type)
        if mc.objExists(color):
            mc.setAttr(color , *value)


