import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr
reload(rModule)
reload(rChain)
reload(rCtrl)
reload(rAttr)

class LookEyes(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=None, shape='circle', model_path=None, guide_path=None, par_ctrl=None, par_jnt=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.par_ctrl = par_ctrl
        self.par_jnt = par_jnt

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        self.left_look_ctrl = rCtrl.Control(parent=self.control_grp, shape='circle', side='L', suffix='CTRL', name='look', axis='z', group_type='main', rig_type='primary', translate=self.guide_list[2], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.left_look_ctrl.tag_as_controller()

        self.right_look_ctrl = rCtrl.Control(parent=self.control_grp, shape='circle', side='R', suffix='CTRL', name='look', axis='z', group_type='main', rig_type='primary', translate=self.guide_list[3], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.right_look_ctrl.tag_as_controller()

        left = self.guide_list[2]
        right = self.guide_list[3]

        lX, lY, lZ = mc.getAttr(left + '.translateX'), mc.getAttr(left + '.translateY'), mc.getAttr(left + '.translateZ')
        rX, rY, rZ = mc.getAttr(right + '.translateX'), mc.getAttr(right + '.translateY'), mc.getAttr(right + '.translateZ')
        look_avg = ( (lX + rX)/2, (lY + rY)/2, (lZ +rZ)/2 )

        self.main_look_ctrl = rCtrl.Control(parent=self.control_grp, shape='square', side='M', suffix='CTRL', name='lookMain', axis='z', group_type='main', rig_type='primary', translate=look_avg, rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)
        self.main_look_ctrl.tag_as_controller()

        mc.addAttr(self.right_look_ctrl.ctrl, ln='blink', at='double', min=0, max=1, dv=0)
        mc.setAttr(self.right_look_ctrl.ctrl + '.blink', e=True, keyable=True)
        mc.addAttr(self.left_look_ctrl.ctrl, ln='blink', at='double', min=0, max=1, dv=0)
        mc.setAttr(self.left_look_ctrl.ctrl + '.blink', e=True, keyable=True)

        mc.parent(self.right_look_ctrl.top, self.left_look_ctrl.top, self.main_look_ctrl.ctrl)

    def output_rig(self):
        look_eyes_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')

        mc.matchTransform(look_eyes_grp, self.main_look_ctrl.ctrl)

        self.left_eyeball_jnt = mc.joint(self.guide_list[0], name='eye_L_JNT')
        mc.parent(self.left_eyeball_jnt, look_eyes_grp)
        self.right_eyeball_jnt = mc.joint(self.guide_list[1], name='eye_R_JNT')
        mc.parent(self.right_eyeball_jnt, look_eyes_grp)

        # self.left_eyelid_jnt = mc.joint(self.guide_list[0], name='eyelid_L_JNT')
        # mc.xform(self.left_eyelid_jnt, r=True, t=[0, 0.01, 0])
        # mc.parent(self.left_eyelid_jnt, look_eyes_grp)
        # self.right_eyelid_jnt = mc.joint(self.guide_list[1], name='eyelid_R_JNT')
        # mc.xform(self.right_eyelid_jnt, r=True, t=[0, 0.01, 0])
        # mc.parent(self.right_eyelid_jnt, look_eyes_grp)

        mc.aimConstraint(self.left_look_ctrl.ctrl, self.left_eyeball_jnt, mo=True)
        mc.aimConstraint(self.right_look_ctrl.ctrl, self.right_eyeball_jnt, mo=True)

    def skeleton(self):
        self.left_chain = rChain.Chain(transform_list=[self.left_eyeball_jnt], side='L', suffix='JNT', name='eyeBind')
        self.left_chain.create_from_transforms(parent=self.skel, pad=False)

        self.right_chain = rChain.Chain(transform_list=[self.right_eyeball_jnt], side='R', suffix='JNT', name='eyeBind')
        self.right_chain.create_from_transforms(parent=self.skel, pad=False)

        # self.left_lid_chain = rChain.Chain(transform_list=[self.left_eyelid_jnt], side='L', suffix='JNT', name='eyelidBind')
        # self.left_lid_chain.create_from_transforms(parent=self.skel, pad=False)

        # self.right_lid_chain = rChain.Chain(transform_list=[self.right_eyelid_jnt], side='R', suffix='JNT', name='eyelidBind')
        # self.right_lid_chain.create_from_transforms(parent=self.skel, pad=False)

        # self.bind_joints = self.right_lid_chain.joints + self.left_lid_chain.joints
        # self.tag_bind_joints(self.bind_joints)


    def add_plugs(self):
        # rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_jnt]*4, name='skeletonPlugs', children_name=[self.left_chain.joints[0], self.right_chain.joints[0], self.left_lid_chain.joints[0], self.right_lid_chain.joints[0]])#children_name=[self.left_eyeball_jnt, self.right_eyeball_jnt])

        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_ctrl], name='pacRigPlugs', children_name=['lookMain_M_CTRL_CNST_GRP'])

        mc.parent('lookEyes_M_JNT_GRP', 'head_M_JNT')