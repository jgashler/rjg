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
            

