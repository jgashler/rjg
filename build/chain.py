import maya.cmds as mc
from importlib import reload

import rjg.libs.control.ctrl as rCtrl
import rjg.libs.common as rCommon
import rjg.libs.attribute as rAttr
import rjg.libs.transform as rXform
import rjg.libs.math as rMath
reload(rCtrl)
reload(rCommon)
reload(rAttr)
reload(rXform)
reload(rMath)

'''
Class used to create joint chains from a list of transforms.
'''
class Chain:
    def __init__(self, transform_list=None, label_chain=True, side='M', suffix='JNT', name='default'):
        self.transform_list = transform_list
        self.label_chain = label_chain
        self.side = side
        self.suffix = suffix
        self.name = name
        self.split_jnt_dict = None

    def create_from_transforms(self, parent_constraint=True, orient_constraint=False, point_constraint=False, scale_constraint=False, connect_scale=True, parent=False, static=False, pad='auto'):
        pose_dict = rXform.read_pose(self.transform_list)
        if pad == 'auto':
            pad = len(str(len(self.transform_list))) + 1
        if not pad and len(self.transform_list) > 1:
            mc.error("Must use padding on chains with more than one joint to avoid naming conflicts.")

        # place joints at each position in the transform list
        self.joints = []
        for i, pose in enumerate(pose_dict):
            if pad:
                name_list = [self.name, self.side, str(i+1).zfill(pad), self.suffix]
            else:
                name_list = [self.name, self.side, self.suffix]
            jnt_name = '_'.join(name_list)

            if i == 0:
                jnt = mc.joint(None, name=jnt_name)
                p_jnt = jnt
            else:
                jnt = mc.joint(p_jnt, name=jnt_name)
                p_jnt = jnt

            rXform.set_pose(jnt, pose_dict[pose])
            self.joints.append(jnt)

        # if there is another part of main skeleton to be parent, parent now
        if parent:
            mc.parent(self.joints[0], parent)

        mc.makeIdentity(self.joints[0], apply=True)

        # set contstraints
        if not static:
            if point_constraint or orient_constraint:
                parent_constraint = False

            self.constraints = []
            for src, jnt in zip(pose_dict, self.joints):
                if parent_constraint:
                    pac = mc.parentConstraint(src, jnt, mo=True)[0]
                    self.constraints.append(pac)
                elif orient_constraint and point_constraint:
                    orc = mc.orientConstraint(src, jnt, mo=True)[0]
                    poc = mc.pointConstraint(src, jnt, mo=True)[0]
                    self.constraints.append(orc)
                    self.constraints.append(poc)
                elif orient_constraint:
                    orc = mc.orientConstraint(src, jnt, mo=True)[0]
                    self.constraints.append(orc)
                elif point_constraint:
                    poc = mc.pointConstraint(src, jnt, mo=True)[0]
                    self.constraints.append(poc)
                else:
                    mc.connectAttr(src + '.translate', jnt + '.translate')
                    mc.connectAttr(src + '.rotate', jnt + '.rotate')

                if scale_constraint:
                    scc = mc.scaleConstraint(src, jnt, mo=True)[0]
                    self.constraints.append(scc)
                else:
                    if connect_scale:
                        mc.connectAttr(src + '.scale', jnt + '.scale')

        self.get_chain_lengths()

        if self.label_chain:
            self.label_side(self.joints)

    '''
    Adds an attribute to joints depending on their side.
    '''
    def label_side(self, chain):
        for jnt in chain:
            if any(self.side[0] == side for side in ['M', 'm', 'C', 'c', 'Md', 'md', 'Ct', 'ct']):
                mc.setAttr(jnt + '.side', 0)
            elif any(self.side[0] == side for side in ['L', 'l', 'Lf', 'lf']):
                mc.setAttr(jnt + '.side', 1)
            elif any(self.side[0] == side for side in ['R', 'r', 'Rt', 'rt']):
                mc.setAttr(jnt + '.side', 2)
            else:
                mc.setAttr(jnt + '.side', 3)

    def get_chain_lengths(self):
        self.bone_lengths = []

        for i in range(len(self.joints)-1):
            a = self.joints[i]
            b = self.joints[i+1]

            bone_len = rMath.distance_between(point_a=a, point_b=b)
            self.bone_lengths.append(bone_len)

        self.chain_length = sum(self.bone_lengths)

    def split_chain(self, segments=4):
        self.split_jnt_dict = {}
        for bone in self.joints[:-1]:
            split_jnts = self.split_bone(bone=bone, segments=segments)
            self.split_jnt_dict[bone] = split_jnts

    def split_bone(self, bone=None, segments=4):
        pad = len(str(segments)) + 1
        end_joint = mc.listRelatives(bone, children=True, type='joint')
        s = mc.xform(bone, q=True, ws=True, t=True)
        e = mc.xform(end_joint, q=True, ws=True, t=True)

        split_jnts = []
        for i in range(1, segments+1):
            name_list = [bone.replace('_' + self.suffix, ''), 'seg', str(i).zfill(pad), self.suffix]
            seg_name = '_'.join(name_list)
            seg_joint = mc.joint(bone, name=seg_name)
            if i > 1:
                seg_pos = [s[axis] + ((i-1) * ((e[axis] - s[axis]) / segments)) for axis in range(3)]
                mc.xform(seg_joint, ws=True, t=seg_pos)
            split_jnts.append(seg_joint)
        
        return split_jnts
    
    def twist_chain(self, start_translate, start_rotate, end_translate, end_rotate, twist_bone, twist_driver, reverse=False):
        if not mc.pluginInfo('quatNodes', q=True, loaded=True):
            mc.loadPlugin('quatNodes')

        twist_name = twist_bone.replace('_JNT', '')
        twist_loc = mc.spaceLocator(name=twist_name + '_twist_LOC')[0]
        driver_loc = mc.spaceLocator(name=twist_name + '_twist_driver_LOC')[0]
        mc.hide(twist_loc, driver_loc)

        mc.matchTransform(twist_loc, start_translate, position=True, rotation=False)
        mc.matchTransform(twist_loc, start_rotate, position=False, rotation=True)
        mc.parent(twist_loc, twist_bone)

        mc.matchTransform(driver_loc, end_translate, position=True, rotation=False)
        mc.matchTransform(driver_loc, end_rotate, position=False, rotation=True)
        mc.parent(driver_loc, twist_driver)

        mmx = mc.createNode('multMatrix', name=twist_name + '_MMX')
        dcm = mc.createNode('decomposeMatrix', name=twist_name + '_DCM')
        qte = mc.createNode('quatToEuler', name=twist_name + '_QTE')

        mc.connectAttr(driver_loc + '.worldMatrix[0]', mmx + '.matrixIn[0]')
        mc.connectAttr(twist_loc + '.parentInverseMatrix[0]', mmx + '.matrixIn[1]')
        mc.connectAttr(mmx + '.matrixSum', dcm + '.inputMatrix')
        mc.connectAttr(dcm + '.outputQuatY', qte + '.inputQuatY')
        mc.connectAttr(dcm + '.outputQuatW', qte + '.inputQuatW')
        mc.connectAttr(qte + '.outputRotateY', twist_loc + '.rotateY')
        mc.setAttr(qte + '.inputRotateOrder', 1)

        t_i = 1 / float(len(self.split_jnt_dict[twist_bone]))
        t_val = t_i
        for jnt in self.split_jnt_dict[twist_bone]:
            t_percent = t_val - t_i
            if reverse:
                t_percent = 1 - t_percent
            mdl = mc.createNode('multDoubleLinear', name=jnt + '_twist_MDL')
            mc.connectAttr(twist_loc + '.rotateY', mdl + '.input1')
            mc.setAttr(mdl + '.input2', t_percent)
            mc.connectAttr(mdl + '.output', jnt + '.rotateY')
            t_val += t_i

    def bend_chain(self, bone, ctrl_scale, spans=16, mirror=False, global_scale=None):
        if mirror:
            mirror = -1
        else:
            mirror = 1
        seg_jnt_list = self.split_jnt_dict[bone]
        end_jnt = mc.listRelatives(bone, type='joint')
        end_jnt = [ej for ej in end_jnt if ej not in seg_jnt_list][0]

        s = mc.xform(bone, q=True, ws=True, t=True)
        e = mc.xform(end_jnt, q=True, ws=True, t=True)
        m = [(s[axis] + e[axis]) / float(2) for axis in range(3)]

        pos_list = [s]
        for i in range(1, 6):
            pos = [s[axis] + (i * ((e[axis] - s[axis]) / 6)) for axis in range(3)]
            pos_list.append(pos)
        pos_list.append(e)
        b_crv = mc.curve(point=pos_list, degree=3, bezier=True, knot=[0, 0, 0, 1, 1, 1, 2, 2, 2])
        b_crv = mc.rename(bone.replace('JNT', 'bezier_CRV'))

        j_crv = mc.curve(editPoint=[s, e], degree=1)
        j_crv = mc.rename(bone.replace('JNT', 'bend_CRV'))
        mc.rebuildCurve(j_crv, replaceOriginal=True, rebuildType=0, endKnots=1, keepRange=0, keepControlPoints=False, keepEndPoints=False, keepTangents=False, spans=spans, degree=3)

        loc_list = []
        seg_inc = 1 / float(len(seg_jnt_list))
        for i, jnt in enumerate(seg_jnt_list):
            if jnt != seg_jnt_list[-1]:
                next = seg_jnt_list[i+1]
            else:
                next = end_jnt
            loc = mc.spaceLocator(name=jnt.replace('JNT', 'pos_LOC'))[0]
            pci = mc.createNode('pointOnCurveInfo', name=jnt.replace('JNT', 'PCI'))
            mc.connectAttr(j_crv + 'Shape.worldSpace[0]', pci + '.inputCurve')
            mc.connectAttr(pci + '.position', loc + '.translate')
            mc.setAttr(pci + '.parameter', seg_inc * i)
            mc.pointConstraint(loc, jnt)

            mc.setAttr(jnt + '.rotateOrder', 1)
            mc.aimConstraint(next, jnt, aimVector=[0, mirror, 0], upVector=[0, 0, 1], worldUpType='none', skip='y')
            loc_list.append(loc)

        for i, jnt in enumerate(seg_jnt_list):
            if jnt != seg_jnt_list[-1]:
                next = seg_jnt_list[i+1]
            else:
                next = end_jnt
            dist = mc.createNode('distanceBetween', name=jnt.replace('JNT', 'DIST'))
            mdn = mc.createNode('multiplyDivide', name=jnt.replace('JNT', 'MDN'))

            mc.setAttr(mdn + '.operation', 2)
            mc.connectAttr(loc_list[i] + '.worldMatrix[0]', dist + '.inMatrix1')
            mc.connectAttr(next + '.worldMatrix[0]', dist + '.inMatrix2')
            mc.connectAttr(dist + '.distance', mdn + '.input1X')
            d = mc.getAttr(dist + '.distance')

            if global_scale:
                mdl = mc.createNode('multDoubleLinear', name=jnt.replace('JNT', 'MDL'))
                mc.connectAttr(global_scale, mdl + '.input1')
                mc.connectAttr(mdl + '.output', mdn + '.input2X')
                mc.setAttr(mdl + '.input2', d)
            else:
                mc.setAttr(mdn + '.input2X', d)
            mc.connectAttr(mdn + '.outputX', jnt + '.scaleY')

        rig_grp = mc.group(b_crv, j_crv, loc_list, name=bone.replace('JNT', 'bendy_rig_GRP'))
        ctrl_grp = mc.group(empty=True, name=bone.replace('JNT', 'CTRL_GRP'))
        mc.matchTransform(ctrl_grp, bone)
        mc.hide(rig_grp)

        mc.setAttr(rig_grp + '.inheritsTransform', 0)
        mc.setAttr(ctrl_grp + '.inheritsTransform', 0)

        dcm = mc.createNode('decomposeMatrix', name=bone.replace('JNT', 'DCM'))
        mc.connectAttr(bone + '.worldMatrix[0]', dcm + '.inputMatrix')
        for attr in ['translate', 'rotate', 'scale']:
            mc.connectAttr(dcm + '.output' + attr.capitalize(), ctrl_grp + '.' + attr)
        
        attr_util = rAttr.Attribute(add=False)
        mid_ctrl = rCtrl.Control(parent=ctrl_grp, shape='circle', side=None, suffix='CTRL', name=bone.replace('JNT', 'bendy'), axis='y', group_type='main', 
                                 rig_type='bendy', translate=m, rotate=bone, ctrl_scale=ctrl_scale*0.8)
        s_tan = rCtrl.Control(parent=ctrl_grp, shape='square', side=None, suffix='CTRL', name=bone.replace('JNT', 'start_tangent'), axis='y', group_type=2, 
                                 rig_type='tangent', translate=b_crv + '.cv[1]', rotate=bone, ctrl_scale=ctrl_scale*0.6)
        e_tan = rCtrl.Control(parent=ctrl_grp, shape='square', side=None, suffix='CTRL', name=bone.replace('JNT', 'end_tangent'), axis='y', group_type=2, 
                                 rig_type='tangent', translate=b_crv + '.cv[5]', rotate=bone, ctrl_scale=ctrl_scale*0.6)
        
        attr_util.lock_and_hide(node=mid_ctrl.ctrl, translate=False, rotate=False, scale='XZ')
        attr_util.lock_and_hide(node=s_tan.ctrl, translate=False)
        attr_util.lock_and_hide(node=e_tan.ctrl, translate=False)

        curvature = rAttr.Attribute(node=mid_ctrl.ctrl, type='double', value=1, min=0.001, max=3, keyable=True, name='curvature')
        tangent_vis = rAttr.Attribute(node=mid_ctrl.ctrl, type='bool', value=False, keyable=True, name='tangentVisibility')
        mc.connectAttr(tangent_vis.attr, s_tan.top + '.visibility')
        mc.connectAttr(tangent_vis.attr, e_tan.top + '.visibility')

        mc.xform(mid_ctrl.top, ws=True, pivots=s)
        mc.xform(s_tan.top, ws=True, pivots=s)
        mc.xform(e_tan.top, ws=True, pivots=e)
        #print(s_tan.control_dict)
        mc.xform(s_tan.control_dict['rig_groups'][0], ws=True, pivots=s)
        mc.xform(e_tan.control_dict['rig_groups'][0], ws=True, pivots=e)

        mc.wire(j_crv, wire=b_crv, dropoffDistance=[0, 5000], crossingEffect=0, localInfluence=0, name=j_crv + '_wire')

        mc.cluster(b_crv + '.cv[0]', bindState=True, weightedNode=(bone, bone), name=b_crv + '_start_CLS')
        mc.cluster(b_crv + '.cv[1]', bindState=True, weightedNode=(s_tan.ctrl, s_tan.ctrl), name=b_crv + '_start_tangent_CLS')
        mc.cluster(b_crv + '.cv[2:4]', bindState=True, weightedNode=(mid_ctrl.ctrl, mid_ctrl.ctrl), name=b_crv + '_mid_CLS')
        mc.cluster(b_crv + '.cv[5]', bindState=True, weightedNode=(e_tan.ctrl, e_tan.ctrl), name=b_crv + '_end_tangent_CLS')
        mc.cluster(b_crv + '.cv[6]', bindState=True, weightedNode=(bone, bone), name=b_crv + '_end_CLS')

        sb_cls = mc.cluster(b_crv + 'BaseWire.cv[1]', name=b_crv + '_base_start_CLS')[1]
        eb_cls = mc.cluster(b_crv + 'BaseWire.cv[5]', name=b_crv + '_base_end_CLS')[1]

        mc.xform(sb_cls, ws=True, pivots=s)
        mc.xform(eb_cls, ws=True, pivots=e)
        mc.parent(sb_cls, eb_cls, rig_grp)

        for axis in 'xyz':
            mc.connectAttr(curvature.attr, sb_cls + '.s' + axis)
            mc.connectAttr(curvature.attr, eb_cls + '.s' + axis)
        mc.connectAttr(curvature.attr, s_tan.top + '.sy')
        mc.connectAttr(curvature.attr, e_tan.top + '.sy')

        return {'control':ctrl_grp, 'module':rig_grp}

    def create_blend_chain(self, switch_node, chain_a, chain_b, translate=True, rotate=True, scale=True):
        self.create_from_transforms(static=True)

        self.switch = rAttr.Attribute(node=switch_node, type='double', min=0, max=1, keyable=True, name='switch')

        i = 0
        for a, b in zip(chain_a, chain_b):
            bcn_name = self.joints[i].replace(self.suffix, '')
            if translate:
                bcn = mc.createNode('blendColors', name=bcn_name + '_translate_BCN')
                mc.connectAttr(a + '.t', bcn + '.color1')
                mc.connectAttr(b + '.t', bcn + '.color2')
                mc.connectAttr(self.switch.attr, bcn + '.blender')
                mc.connectAttr(bcn + '.output', self.joints[i] + '.t')
            if rotate:
                bcn = mc.createNode('blendColors', name=bcn_name + '_rotate_BCN')
                mc.connectAttr(a + '.r', bcn + '.color1')
                mc.connectAttr(b + '.r', bcn + '.color2')
                mc.connectAttr(self.switch.attr, bcn + '.blender')
                mc.connectAttr(bcn + '.output', self.joints[i] + '.r')
            if scale:
                bcn = mc.createNode('blendColors', name=bcn_name + '_scale_BCN')
                mc.connectAttr(a + '.s', bcn + '.color1')
                mc.connectAttr(b + '.s', bcn + '.color2')
                mc.connectAttr(self.switch.attr, bcn + '.blender')
                mc.connectAttr(bcn + '.output', self.joints[i] + '.s')

            i += 1

    def create_from_curve(self, joint_num=5, curve=None, aim_vector=(0, 1, 0), up_vector=(0, 0, 1), world_up_vector=(0, 0, 1), stretch=None):
        if not curve:
            mc.error('Please provide a valid curve along which to build joints.')

        self.joints = []

        pad = len(str(joint_num)) + 1
        inc = 1 / (joint_num + 1)
        par = None

        for i in range(joint_num):
            name_list = [self.name, self.side, str(i + 1).zfill(pad), self.suffix]
            joint_name = '_'.join(name_list)

            joint = mc.joint(None, name=joint_name)
            pos = rXform.findPosOnCurve(curve, i * inc)
            mc.setAttr(joint + '.translate', *pos)

            if par:
                aim = mc.aimConstraint(joint, par, aim=aim_vector, upVector=up_vector, worldUpType='vector', worldUpVector=world_up_vector)
                mc.delete(aim)
                mc.parent(joint, par)

            par = joint
            self.joints.append(joint)

        mc.makeIdentity(self.joints[0], rotate=0, apply=True)
        mc.setAttr(self.joints[-1] + '.jointOrient', 0, 0, 0)

        if self.label_chain:
            self.label_side(self.joints)



def stretch_segment(jnt, start, end, stretch_driver=None, global_scale=None):
    dist = mc.createNode("distanceBetween", name=jnt.replace('JNT', 'DIST'))
    mdn = mc.createNode("multiplyDivide", name=jnt.replace('JNT', 'MDN'))

    mc.setAttr(mdn + '.operation', 2)
    mc.connectAttr(start + '.worldMatrix[0]', dist + '.inMatrix1')
    mc.connectAttr(end + '.worldMatrix[0]', dist + '.inMatrix2')
    mc.connectAttr(dist + '.distance', mdn + '.input1X')
    d = mc.getAttr(dist + '.distance')

    if global_scale:
        mdl = mc.createNode('multDoubleLinear', name=jnt.replace('JNT', 'MDL'))
        mc.connectAttr(global_scale, mdl + '.input1')
        mc.connectAttr(mdl + '.output', mdn + '.input2X')
        mc.setAttr(mdl + '.input2', d)
    else:
        mc.setAttr(mdn + '.input2', d)

    if stretch_driver:
        bta = mc.createNode('blendTwoAttr', name=jnt.replace('JNT', 'BTA'))
        mc.setAttr(bta + '.input[0]', 1)
        mc.connectAttr(mdn + '.outputX', bta + '.input[1]')
        mc.connectAttr(stretch_driver, bta + '.attributesBlender')
        mc.connectAttr(bta + '.output', jnt + '.scaleY')
    else:
        mc.connectAttr(mdn + '.outputX', jnt + '.scaleY')
    