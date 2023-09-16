import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.build.fk as rFk
reload(rModule)
reload(rAttr)
reload(rChain)
reload(rFk)

class Finger(rModule.RigModule, rFk.Fk):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, model_path=None, guide_path=None, pad='auto', remove_last=True, fk_shape='circle'):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.pad = pad
        self.remove_last = remove_last
        self.fk_shape = fk_shape
        self.gimbal = None
        self.offset = None

        if self.pad == 'auto':
            self.pad = len(str(len(self.guide_list))) + 1

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        #self.add_plugs()

    def control_rig(self):
        self.build_fk_controls()
        mc.parent(self.fk_ctrls[0], self.control_group)

    def output_rig(self):
        self.build_fk_chain()
        mc.parent(self.fk_joints[0], self.module_grp)

    def skeleton(self):
        fk_chain = rChain.Chain(transform_list=self.fk_joints, side=self.side, suffix='JNT', name=self.part)
        fk_chain.create_from_transforms(parent=self.skel, scale_constraint=False)

        if self.remove_last:
            mc.delete(self.fk_ctrks[-1].top)
            self.bind_joints = fk_chain.joints[:-1]
        else:
            self.bind_joints = fk_chain.joints

        self.tag_bind_joints(self.bind_joints)

    def add_plugs(self):
        pass
