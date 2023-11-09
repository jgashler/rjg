import maya.cmds as mc
from importlib import reload

import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr
import rjg.libs.space as rSpace
reload(rCtrl)
reload(rAttr)
reload(rSpace)

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
    mc.setAttr(c_shapes[0] + '.overrideColorRGB', 1, 0, 0)
    mc.setAttr(c_shapes[1] + '.overrideColorRGB', 0, 1, 0)
    mc.setAttr(c_shapes[2] + '.overrideColorRGB', 0, 0, 1)

    for type, ctrl_list in type_dict.items():
        rAttr.Attribute(node=c_ctrl.ctrl, type='separator', name=type)
        color = rAttr.Attribute(node=c_ctrl.ctrl, type='double3', value=0, keyable=True, min=0, max=1, name=type + 'Color', children_name='RGB')
        for ctrl in ctrl_list:
            for shape in mc.listRelatives(ctrl, shapes=True, type='nurbsCurve'):
                mc.setAttr(shape + '.overrideEnabled', 1)
                mc.setAttr(shape + '.overrideRGBColors', 1)
                mc.connectAttr(color.attr, shape + '.overrideColorRGB')

    set_color_defaults(c_ctrl.ctrl)
    return c_ctrl.ctrl

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

def add_display_type(node, value, name, target):
    dt = rAttr.Attribute(node=node, type='enum', value=value, enum_list=['Normal', 'Template', 'Reference'], keyable=True, name=name)
    mc.setAttr(target + '.overrideEnabled', 1)
    mc.connectAttr(dt.attr, target + '.overrideDisplayType')


def add_vis_ctrl():
    attr_util = rAttr.Attribute(add=False)
    type_dict = get_ctrl_types()

    if mc.objExists('M_global_CTRL'):
        par = ('M_global_CTRL')
    else:
        par = 'RIG'

    vis_ctrl = rCtrl.Control(parent=par, shape='gear_3D', side=None, name='vis', suffix='CTRL', axis='y', group_type=None, rig_type='global')
    attr_util.lock_and_hide(node=vis_ctrl.ctrl)

    v_shapes = mc.listRelatives(vis_ctrl.ctrl, shapes=True)
    for shape in v_shapes:
        mc.setAttr(shape + '.overrideEnabled', 1)
        mc.setAttr(shape + '.overrideRGBColors', 1)
    mc.setAttr(v_shapes[0] + '.overrideColorRGB', 1, 0, 0)

    model_vis = rAttr.Attribute(node=vis_ctrl.ctrl, type='bool', value=1, keyable=True, name='modelVis')
    skel_vis = rAttr.Attribute(node=vis_ctrl.ctrl, type='bool', value=1, keyable=True, name='skelVis')
    rig_vis = rAttr.Attribute(node=vis_ctrl.ctrl, type='bool', value=0, keyable=True, name='rigVis')
    rAttr.Attribute(node=vis_ctrl.ctrl, type='separator', value=0, name='displayType')

    mc.connectAttr(model_vis.attr, 'MODEL.visibility')
    mc.connectAttr(skel_vis.attr, 'SKEL.visibility')

    add_display_type(node=vis_ctrl.ctrl, value=2, name='modelDisplay', target='MODEL')
    add_display_type(node=vis_ctrl.ctrl, value=2, name='skelDisplay', target='SKEL')

    for module in mc.ls('*_MODULE'):
        mc.connectAttr(rig_vis.attr, module + '.visibility')

    part_dict = {}
    for c in mc.ls('*_CONTROL'):
        part = c.split('_')[1]
        side = c.split('_')[0]
        if part in part_dict:
            part_dict[part].append(side)
        else:
            part_dict[part] = [side]

    for part, sides in part_dict.items():
        p_vis = rAttr.Attribute(node=vis_ctrl.ctrl, type='bool', value=1, keyable=True, name=part + '_Vis')
        for side in sides:
            mc.connectAttr(p_vis.attr, '{}_{}_CONTROL.visibility'.format(side, part))
        
    rAttr.Attribute(node=vis_ctrl.ctrl, type='separator', value=0, name='controlType')

    for type, ctrl_list in type_dict.items():
        t_vis = rAttr.Attribute(node=vis_ctrl.ctrl, type='bool', value=1, keyable=True, name=type + '_Vis')
        for ctrl in ctrl_list:
            shapes = mc.listRelatives(ctrl, shapes=True, path=True)
            for shape in shapes:
                if mc.nodeType(shape) == 'nurbsCurve':
                    mc.connectAttr(t_vis.attr, shape + '.visibility')

    return vis_ctrl.ctrl
        


def assemble_skeleton():
    for part in mc.listRelatives('RIG'):
        if mc.objExists(part + '.skeletonPlugs'):
            children = mc.listAttr(part + '.skeletonPlugs')
            for child in children[1:]:
                plug = part + '.' + child
                par = mc.getAttr(plug)
                if 'mc.' in par:
                    par = eval(par)
                    mc.setAttr(plug, par, type='string')
                if mc.objExists(par):
                    mc.parent(child, par)
                else:
                    mc.warning(par + ' does not exist. Skipping...')

def add_global_scale(global_ctrl='global_M_CTRL'):
    gs_list = mc.ls('*.globalScale')
    gs = rAttr.Attribute(node=global_ctrl, type='double', value=1, keyable=True, min=0.001, name='globalScale')
    mc.connectAttr(gs.attr, 'SKEL.sx')
    mc.connectAttr(gs.attr, 'SKEL.sy')
    mc.connectAttr(gs.attr, 'SKEL.sz')
    mc.connectAttr(gs.attr, global_ctrl + '.sx')
    mc.connectAttr(gs.attr, global_ctrl + '.sy')
    mc.connectAttr(gs.attr, global_ctrl + '.sz')
    gs.lock_and_hide(translate=False, rotate=False)
    
    for ps in gs_list:
        part = ps.split('.')[0]
        mc.connectAttr(gs.attr, ps)
        mc.connectAttr(ps, part + '.sx')
        mc.connectAttr(ps, part + '.sy')
        mc.connectAttr(ps, part + '.sz')

def assemble_rig():
    mc.parent('chest_M_01_CTRL', 'hip_M_01_CTRL')
    mc.parent('head_M_01_CTRL', 'chest_M_01_CTRL')

    for part in mc.listRelatives('RIG'):

        plug_types = ['hideRigPlugs', 'deleteRigPlugs']
        for pt in plug_types:
            if mc.objExists(part + '.' + pt):
                driven_list = mc.listAttr(part + '.' + pt)[1:]
                for driven in driven_list:
                    plug = part + '.' + driven
                    node_list = mc.getAttr(plug)
                    node_list = node_list.split(' ')
                    #print(node_list[0])
                    if pt == 'hideRigPlugs':
                        #mc.hide(node for node in node_list)
                        for node in node_list:
                            #print(node)
                            mc.hide(node)
                    elif pt == 'deleteRigPlugs':
                        #mc.delete(node for node in node_list)
                        for node in node_list:
                            mc.delete(node)
                    else:
                        mc.warning(pt + ' plug type not found. Skipping...')

        plug_types = ['pacRigPlugs', 'pacPocRigPlugs', 'pocRigPlugs', 'orcRigPlugs']
        for pt in plug_types:
            if mc.objExists(part + '.' + pt):
                driven_list = mc.listAttr(part + '.' + pt)[1:]
                for driven in driven_list:
                    plug = part + '.' + driven
                    driver = mc.getAttr(plug)
                    if 'mc.' in driver:
                        driver = eval(driver)
                        mc.setAttr(plug, driver, type='string')
                    if mc.objExists(driver):
                        if pt == 'pacRigPlugs':
                            mc.parentConstraint(driver, driven, mo=True)
                        elif pt == 'pacPocRigPlugs':
                            mc.parentConstraint(driver, driven, skipRotate=['x', 'y', 'z'], mo=True)
                        elif pt == 'pocRigPlugs':
                            if '_point' in driven:
                                driven = driven.replace('_point', '')
                            mc.pointConstraint(driver, driven, mo=True)
                        elif pt == 'orcRigPlugs':
                            if '_orient' in driven:
                                driven = driven.replace('_orient', '')
                            mc.orientConstraint(driver, driven, mo=True)
                        else:
                            mc.warning(pt + ' plug type does not exist. Skipping...')
                    else:
                        mc.warning(driver + ' driver does not exist. Skipping...')

        plug_types = ['parent', 'point', 'orient']
        for pt in plug_types:
            for ctrl in mc.ls(part + '*.ctrlDict'):
                ctrl = ctrl.split('.')[0]
                attr_name = '{}.{}_{}'.format(part, ctrl, pt)
                if mc.objExists(attr_name):
                    name_list = mc.listAttr(attr_name)
                    driver = name_list[0].split('.')[0]
                    if mc.objExists(part + '.' + driver):
                        driver = rCtrl.Control(ctrl=driver.replace('_'+pt, ''))
                        target_list = []
                        for name in name_list[1:]:
                            plug = part + '.' + name
                            target = mc.getAttr(plug)
                            if 'mc.' in target:
                                target = eval(target)
                                mc.setAttr(plug, target, type='string')
                            target_list.append(target)
                        value = int(target_list[-1])
                        name_list = [name.replace(pt, '').lower() for name in name_list[1:-1]]
                        if all(mc.objExists(obj) for obj in target_list[:-1]):
                            rSpace.space_switch(node=driver.top, driver=driver.ctrl, target_list=target_list[:-1], name_list=name_list, name=pt + 'Space', constraint_type=pt, value=value)

        if mc.objExists(part + '.transferAttributes'):
            driven_list = mc.listAttr(part + '.transferAttributes')[1:]
            for driven in driven_list:
                plug = part + '.' + driven
                transfer_node = mc.getAttr(plug)
                attr_list = mc.listAttr(driven, userDefined=True)
                for attr in attr_list:
                    if attr != 'ctrlDict':
                        src_attr = rAttr.Attribute(add=False, node=driven, name=attr, transfer_to=transfer_node)
                        src_attr.transfer_attr()

def add_rig_sets():
    rig_set = mc.sets(name='rig_SET', empty=True)
    ctrl_set = mc.sets(name='control_SET', empty=True)
    cache_set = mc.sets(name='cache_SET', empty=True)
    mc.sets(ctrl_set, add=rig_set)
    mc.sets(cache_set, add=rig_set)

    for part in mc.listRelatives('RIG'):
        part_set = mc.sets(mc.ls(part+'*_CTRL'), name=part + '_SET')
        mc.sets(part_set, add=ctrl_set)

    mc.sets('MODEL', add=cache_set)

def add_switch_ctrl():
    attr_util = rAttr.Attribute(add=False)

    if mc.objExists('global_M_CTRL'):
        par = 'global_M_CTRL'
    else:
        par = 'RIG'

    s_ctrl = rCtrl.Control(parent=par, shape='cube', side=None, suffix='CTRL', name='switch', axis='y', group_type=None, rig_type='global')
    attr_util.lock_and_hide(node=s_ctrl.ctrl)

    # add color

    for part in mc.listRelatives('RIG'):
        if mc.objExists(part + '.switchRigPlugs'):
            switch_name = mc.getAttr(part + '.ikFkSwitch')
            if mc.objExists(s_ctrl.ctrl + '.' + switch_name):
                switch_attr = rAttr.Attribute(node=s_ctrl.ctrl, name=switch_name, add=False)
            else:
                switch_attr = rAttr.Attribute(node=s_ctrl.ctrl, type='double', value=0, keyable=True, min=0, max=1, name=switch_name)
            mc.connectAttr(switch_attr.attr, part + '.switch')

    return s_ctrl.ctrl



def final(vis_ctrl=True, color_ctrl=True, switch_ctrl=True, constrain_model=True):
    if color_ctrl:
        c_ctrl = add_color_attrs()
    if switch_ctrl:
        s_ctrl = add_switch_ctrl()
    if vis_ctrl:
        v_ctrl = add_vis_ctrl()
    assemble_skeleton()
    assemble_rig()
    add_global_scale()
    add_rig_sets()

    util_grp = mc.group(empty=True, name='utility_M', parent='RIG')
    mc.parent(c_ctrl, s_ctrl, v_ctrl, util_grp)

    if constrain_model:
        if mc.objExists('root_M_JNT'):
            mc.parentConstraint('root_M_JNT', 'MODEL', mo=True)
            mc.scaleConstraint('root_M_JNT', 'MODEL', mo=True)

