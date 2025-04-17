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

class Arbitrary3(rModule.RigModule):
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
        
        Gtranslate = mc.xform(self.guide_list, q=True, ws=True, t=True) #mc.getAttr(self.guide_list + '.translate')
        #print(Gtranslate)
        #print(self.guide_list)
        Grotate = mc.getAttr(self.guide_list + '.rotate')
        #print(Grotate)

        self.arbit_ctrl = rCtrl.Control(parent=self.control_grp, shape='circle', side=self.side, suffix='CTRL', name=self.base_name, axis='z', group_type='main', rig_type='primary', translate=Gtranslate, rotate=Grotate[0], ctrl_scale=self.ctrl_scale)
        self.arbit_ctrl.tag_as_controller()

    def output_rig(self):
        arbit_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(arbit_jnt_grp, self.arbit_ctrl.ctrl)

        self.arbit_jnt = mc.joint(arbit_jnt_grp, name=self.arbit_ctrl.ctrl.replace('CTRL', 'JNT'))
        #mc.parentConstraint(self.arbit_ctrl.ctrl, self.arbit_jnt, mo=True)

    def skeleton(self):
        arbit_chain = rChain.Chain(transform_list=[self.arbit_jnt], side=self.side, suffix='JNT', name=self.part)
        arbit_chain.create_from_transforms(parent=self.skel, pad=False)
        self.bind_joints = arbit_chain.joints
        self.tag_bind_joints(self.bind_joints)


    def add_plugs(self):
        #rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_jnt], name='skeletonPlugs', children_name=[self.bind_joints[0]])

        #rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_ctrl], name='pacRigPlugs', children_name=[self.base_name + '_' + self.side + '_CTRL_CNST_GRP'])
        pass