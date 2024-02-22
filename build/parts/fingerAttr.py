import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.libs.attribute as rAttr
import rjg.libs.control.ctrl as rCtrl
reload(rModule)
reload(rAttr)
reload(rCtrl)

class FingerAttr(rModule.RigModule):
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, model_path=None, guide_path=None):
        super().__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)
        self.__dict__.update(locals())
        self.base_name = self.part + '_' + self.side

        self.create_module()

    def create_module(self):
        super().create_module()

        self.control_rig()
        #self.output_rig()
        #self.skeleton()
        #self.add_plugs()

    def control_rig(self):
        self.ctrl = rCtrl.Control(parent=self.control_grp, shape='double_arrow', side=self.side, suffix='CTRL', name=self.part, axis='x', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)

        #roll = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='roll')

        self.thumb_curl = rAttr.Attribute(node = self.ctrl.ctrl, type='double', min=None, max=None, value=0, keyable=True, name='thumbCurl')
        self.pointer_curl = rAttr.Attribute(node = self.ctrl.ctrl, type='double', min=None, max=None, value=0, keyable=True, name='pointerCurl')
        self.middle_curl = rAttr.Attribute(node = self.ctrl.ctrl, type='double', min=None, max=None, value=0, keyable=True, name='middleCurl')
        self.ring_curl = rAttr.Attribute(node = self.ctrl.ctrl, type='double', min=None, max=None, value=0, keyable=True, name='ringCurl')
        self.pinky_curl = rAttr.Attribute(node = self.ctrl.ctrl, type='double', min=None, max=None, value=0, keyable=True, name='pinkyCurl')

        

    def output_rig(self):
        self.build_fk_chain()
        mc.parent(self.fk_joints[0], self.module_grp)

        meta_pos = [self.hand, self.guide_list[0]]
        meta_chain = rChain.Chain(transform_list=meta_pos, side=self.side, suffix='JNT', name=self.part + 'Metacarpal')
        self.meta_chain = meta_chain.create_from_transforms(parent=self.module_grp, static=True)

        mc.pointConstraint(self.fk_joints[0], self.meta_chain[1], mo=True)
        mc.aimConstraint(self.fk_joints[0], self.meta_chain[0], mo=True)

    def skeleton(self):
        pass


    def add_plugs(self):
        '''
        rAttr.Attribute(node=self.part_grp, type='plug', value=['hand_' + self.side + '_JNT'], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        driver_list = ['hand_' + self.side + '_01_switch_JNT', 'hand_' + self.side + '_01_switch_JNT']
        #driven_list = [self.base_name + '_01_fk_CTRL_CNST_GRP']
        driven_list = [self.base_name + '_01_fk_CTRL_CNST_GRP', self.meta_chain[0]]#, self.base_name + '_01_JNT']

        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)
        '''