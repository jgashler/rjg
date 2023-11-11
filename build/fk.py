import maya.cmds as mc
from importlib import reload

import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
reload(rChain)
reload(rCtrl)

class Fk:
    def __init__(self, side=None, part=None, guide_list=None, gimbal=None, offset=None, pad='auto', ctrl_scale=1, remove_last=True, 
                 add_joints=True, fk_shape='circle', gimbal_shape='circle', offset_shape='square'):
        self.side = side
        self.part = part
        self.base_name = part + "_" + side
        
        self.guide_list = guide_list
        self.gimbal = gimbal
        self.offset = offset
        self.pad = pad
        self.ctrl_scale = ctrl_scale
        self.remove_last = remove_last
        self.add_joints = add_joints
        self.fk_shape = fk_shape
        self.gimbal_shape = gimbal_shape
        self.offset_shape = offset_shape

        if self.pad == 'auto':
            self.pad = len(str(len(self.guide_list))) + 1
        
        if self.guide_list:
            if not isinstance(self.guide_list, list):
                self.guide_list = [self.guide_list]

    def build_fk(self):
        self.build_fk_controls()

        if self.add_joints:
            self.build_fk_chain()

        if self.remove_last:
            mc.delete(self.fk_ctrls[-1].top)

    '''
    Builds up to three layers of controls for each joint: fk, gimbal, and offset. Innermost will be the constraint target for joints.
    '''
    def build_fk_controls(self):
        self.fk_ctrls = []
        self.gim_ctrls = []
        self.ofst_ctrls = []

        for i, pose in enumerate(self.guide_list):
            num = str(i+1).zfill(self.pad)
            if pose == self.guide_list[0]:
                par = None
            fk = rCtrl.Control(parent=par, shape=self.fk_shape, side=None, suffix='CTRL', name=self.base_name + "_" + num + "_fk", axis='y', group_type='main', 
                       rig_type='fk', translate=pose, rotate=pose, ctrl_scale=self.ctrl_scale)
            par = fk.ctrl
            self.fk_ctrls.append(fk)
            fk.tag_as_controller()

            # output_ctrls: constraint target for joints
            self.output_ctrls = self.fk_ctrls

            if self.gimbal:
                gim = rCtrl.Control(parent=par, shape=self.gimbal_shape, side=None, suffix='CTRL', name=self.base_name + "_" + num + "_gimbal", axis='y', group_type='main', 
                       rig_type='gimbal', translate=pose, rotate=pose, ctrl_scale=self.ctrl_scale*0.8)
                par = gim.ctrl
                self.gim_ctrls.append(gim)
                self.output_ctrls = self.gim_ctrls
                gim.tag_as_controller()

            if self.offset:
                ofst = rCtrl.Control(parent=par, shape=self.offset_shape, side=None, suffix='CTRL', name=self.base_name + "_" + num + "_offset", axis='y', group_type='main', 
                       rig_type='offset', translate=pose, rotate=pose, ctrl_scale=self.ctrl_scale*0.55)
                self.ofst_ctrls.append(ofst)
                self.output_ctrls = self.ofst_ctrls
                ofst.tag_as_controller()

    '''
    Places and constrains joints at each control location.
    '''
    def build_fk_chain(self):
        transform_list = [oc.ctrl for oc in self.output_ctrls]
        self.fk_chain = rChain.Chain(transform_list=transform_list, side=self.side, suffix='fk_JNT', name=self.part)
        self.fk_chain.create_from_transforms(parent_constraint=True, scale_constraint=False)
        self.fk_joints = self.fk_chain.joints

