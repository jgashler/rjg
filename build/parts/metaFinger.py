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

class MetaFinger(rModule.RigModule, rFk.Fk):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, model_path=None, guide_path=None, pad='auto', remove_last=True, fk_shape='circle', hand=None, up_par=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)
        self.__dict__.update(locals())

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
        self.add_plugs()

    def control_rig(self):
        self.build_fk_controls()
        mc.parent(self.fk_ctrls[0].top, self.control_grp)

    def output_rig(self):
        self.build_fk_chain()
        mc.parent(self.fk_joints[0], self.module_grp)

        meta_pos = [self.hand, self.guide_list[0]]
        meta_chain = rChain.Chain(transform_list=meta_pos, side=self.side, suffix='JNT', name=self.part + 'Metacarpal')
        self.meta_chain = meta_chain.create_from_transforms(parent=self.module_grp, static=True)

        up_loc = mc.spaceLocator(name=self.base_name + '_UP_LOC')[0]
        mc.matchTransform(up_loc, self.meta_chain[0])
        mc.xform(up_loc, t=[0, 10, 0], relative=True)

        mc.pointConstraint(self.fk_joints[0], self.meta_chain[1], mo=True)
        mc.aimConstraint(self.fk_joints[0], self.meta_chain[0], mo=True, worldUpType=1, worldUpObject=up_loc)
        mc.parent(up_loc, self.up_par)
        mc.hide(up_loc)


    def skeleton(self):
        finger_chain = rChain.Chain(transform_list = [self.meta_chain[0]]+self.fk_joints, side=self.side, suffix='JNT', name=self.part)
        finger_chain.create_from_transforms(parent=self.skel, scale_constraint=False)

        if self.remove_last:
            mc.delete(self.fk_ctrls[-1].top)
            self.bind_joints = finger_chain.joints[:-1]
        else:
            self.bind_joints = finger_chain.joints

        self.tag_bind_joints(self.bind_joints)


    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['hand_' + self.side + '_JNT'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        driver_list = ['hand_' + self.side + '_01_switch_JNT']
        driven_list = [self.base_name + '_01_fk_CTRL_CNST_GRP']
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)

        driver_list = ['hand_' + self.side + '_01_switch_JNT']
        driven_list = [self.meta_chain[0]]
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pocRigPlugs', children_name=driven_list)