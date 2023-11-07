import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.build.fk as rFk
import rjg.libs.attribute as rAttr
reload(rModule)
reload(rChain)
reload(rFk)
reload(rAttr)

class fk_chain(rModule.RigModule, rFk.Fk):
    def __init__(self, side=None, part=None, guide_list=None, gimbal=None, offset=None, pad='auto', ctrl_scale=1, remove_last=True, 
                 fk_shape='circle', gimbal_shape='circle', offset_shape='square', model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.guide_list = guide_list
        self.gimbal = gimbal
        self.offset = offset
        self.pad = pad
        self.remove_last = remove_last
        self.fk_shape = fk_shape
        self.gimbal_shape = gimbal_shape
        self.offset_shape = offset_shape

        if self.pad == 'auto':
            self.pad = len(str(len(self.guide_list))) + 1
        
        self.create_module()


    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        self.build_fk_ctrls()
        mc.parent(self.fk_ctrls[0].top, self.control_grp)

    def output_rig(self):
        self.build_fk_chain()
        mc.parent(self.fk_joints[0], self.module_grp)

    def skeleton(self):
        fk_chain = rChain.Chain(transform_list=self.fk_joints, side=self.side, suffix='JNT', name=self.part)
        fk_chain.create_from_transforms(parent=self.skel)

        if self.remove_last:
            mc.delete(self.fk_ctrls[-1].top)
            self.bind_joints = fk_chain.joints[:-1]
        else:
            self.bind_joints = fk_chain.joints

        self.tag_bind_joints(self.bind_joints)

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['insert fk chain plug here'], name='skeletonPlugs', children_name=[self.bind_joints[0]])