import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.build.ik as rIk
import rjg.libs.attribute as rAttr
reload(rModule)
reload(rChain)
reload(rIk)
reload(rAttr)

class IkChain(rModule.RigModule, rIk.Ik):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, sticky=None, solver=None, pv_guide='auto', offset_pv=0, slide_pv=None, 
                 stretchy=True, twisty=None, bendy=None, segments=None, model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.__dict__.update(locals())
        
        if self.twisty or self.bendy and not self.segments:
            self.segments = 4

        self.create_module()

    def create_module(self):
        super().create_module()

        self.check_solvers()
        self.check_pv_guide()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

        if self.pv_guide:
            mc.parent(self.guide_group, self.control_grp)

    def control_rig(self):
        self.build_ik_controls()
        mc.parent(self.ik_ctrl_grp, self.control_grp)

    def output_rig(self):
        self.build_ik_chain()
        self.src_joints = self.ik_joints

        if self.segments:
            self.ik_chain.split_chain(segments=self.segments)
            self.src_joints = []

            for ik_joint in self.ik_joints[:-1]:
                split_list = self.ik_chain.split_jnt_dict[ik_joint]
                for s_joint in split_list:
                    self.src_joints.append(s_joint)
            self.src_joints.append(self.ik_joints[-1])

        if self.twisty:
            self.ik_chain.twist_chain(start_translate=self.ik_chain.joints[1], start_rotate=self.ik_chain.joints[0],
                                      end_translate=self.ik_chain.joints[0], end_rotate=self.ik_chain.joints[0],
                                      twist_bone=self.ik_chain.joints[0], twist_driver=self.base_ctrl.ctrl, reverse=True)
            self.ik_chain.twist_chain(start_translate=self.ik_chain.joints[2], start_rotate=self.ik_chain.joints[1],
                                      end_translate=self.ik_chain.joints[2], end_rotate=self.ik_chain.joints[1],
                                      twist_bone=self.ik_chain.joints[1], twist_driver=self.main_ctrl.ctrl)
            
        if self.bendy:
            bend_01 = self.ik_chain.bend_chain(bone=self.ik_chain.joints[0], ctrl_scale=self.ctrl_scale, global_scale=self.global_scale.attr)
            bend_02 = self.ik_chain.bend_chain(bone=self.ik_chain.joints[1], ctrl_scale=self.ctrl_scale, global_scale=self.global_scale.attr)

            mc.parent(bend_01['control'], bend_02['control'], self.control_grp)
            mc.parent(bend_01['module'], bend_02['module'], self.module_grp)

        self.build_ikh(scale_attr=self.global_scale)
        mc.parent(self.ikh, self.ik_joints[0], self.module_grp)

    def skeleton(self):
        ik_chain = rChain.Chain(transform_list=self.src_joints, side=self.side, suffix='JNT', name=self.part)
        ik_chain.create_from_transforms(orient_constraint=True, point_constraint=True, scale_constraint=False, parent=self.skel)
        self.bind_joints = ik_chain.joints
        self.tag_bind_joints(self.bind_joints[:-1])

    def add_plugs(self):
        rAttr.Attribute(node=self.part_grp, type='plug', value=['insert ik chain plug here'], name='skeletonPlugs', children_name=[self.bind_joints[0]])
