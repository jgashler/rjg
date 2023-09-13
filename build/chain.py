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

    def create_from_transforms(self, parent_contstraint=True, orient_constraint=False, point_constraint=False, scale_constraint=False, connect_scale=True, parent=False, static=False, pad='auto'):
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
                parent_contstraint = False

            self.constraints = []
            for src, jnt in zip(pose_dict, self.joints):
                if parent_contstraint:
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


            

