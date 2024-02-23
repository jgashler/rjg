import maya.cmds as mc
from importlib import reload

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.build.fk as rFk
import rjg.build.ik as rIk
import rjg.libs.attribute as rAttr

reload(rModule)
reload(rChain)
reload(rFk)
reload(rIk)
reload(rAttr)

class BipedLimb(rModule.RigModule, rIk.Ik, rFk.Fk):
    def __init__(self,side=None,part=None,guide_list=None, ctrl_scale=1,create_ik=True,create_fk=True,stretchy=True,twisty=True,bendy=True,segments=4,
                 sticky=None, solver=None, pv_guide='auto', offset_pv=0, slide_pv=None, gimbal=True, offset=True, 
                 pad='auto', fk_shape='circle', gimbal_shape='circle', offset_shape='square', model_path=None, guide_path=None):
        super(BipedLimb, self).__init__(side=side, part=part, guide_list=guide_list, ctrl_scale=ctrl_scale, model_path=model_path, guide_path=guide_path)

        self.__dict__.update(locals())

        if self.twisty or self.bendy and not self.segments:
            self.segments = 4

        if self.pad == 'auto':
            self.pad = len(str(len(self.guide_list))) + 1

        self.create_module()

    def create_module(self):
        super(BipedLimb, self).create_module()

        self.check_solvers()
        self.check_pv_guide()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    def control_rig(self):
        # fk
        if self.create_fk:
            self.build_fk_controls()
            mc.parent(self.fk_ctrls[0].top, self.control_grp)

        # ik
        if self.create_ik:
            self.pv_control = self.build_ik_controls()
            mc.parent(self.ik_ctrl_grp, self.control_grp)

    def output_rig(self):
        self.limb_grp = mc.group(em=True, parent=self.module_grp,
                                   name=self.base_name + '_RIG_GRP')
        mc.matchTransform(self.limb_grp, self.guide_list[0])

        # fk
        if self.create_fk:
            self.build_fk_chain()
            mc.parent(self.fk_joints[0], self.limb_grp)
            self.src_chain = self.fk_chain
            self.src_joints = self.fk_joints
            up_twist = self.fk_ctrls[0].ctrl
            lo_twist = self.fk_ctrls[-1].ctrl


        # ik
        if self.create_ik:
            self.build_ik_chain()
            self.build_ikh(scale_attr=self.global_scale)
            mc.parent(self.ikh, self.ik_joints[0], self.limb_grp)
            self.src_chain = self.ik_chain
            self.src_joints = self.ik_joints
            up_twist = self.base_ctrl.ctrl
            lo_twist = self.main_ctrl.ctrl

        if self.create_ik and self.create_fk:
            blend_chain = rChain.Chain(transform_list=self.src_joints,
                                        side=self.side,
                                        suffix='switch_JNT',
                                        name=self.part)

            blend_chain.create_blend_chain(switch_node=self.base_name,
                                           chain_a=self.fk_joints,
                                           chain_b=self.ik_joints)
            mc.parent(blend_chain.joints[0], self.limb_grp)
            self.src_chain = blend_chain
            self.src_joints = blend_chain.joints

            # twist
            up_twist = mc.spaceLocator(name=self.base_name + '_up_twist_LOC')[0]
            lo_twist = mc.spaceLocator(name=self.base_name + '_lo_twist_LOC')[0]
            mc.matchTransform(up_twist, self.guide_list[0])
            mc.matchTransform(lo_twist, self.guide_list[-1])

            rev = mc.createNode('reverse', name=self.base_name + '_REV')
            pac = mc.parentConstraint(self.fk_ctrls[-1].ctrl,
                                        self.main_ctrl.ctrl,
                                        lo_twist, maintainOffset=True)[0]
            wal = mc.parentConstraint(pac, query=True, weightAliasList=True)
            mc.setAttr(pac + '.interpType', 2)
            mc.connectAttr(blend_chain.switch.attr, rev + '.inputY')
            mc.connectAttr(rev + '.outputY', pac + '.' + wal[1])
            mc.connectAttr(blend_chain.switch.attr, pac + '.' + wal[0])
            mc.parent(lo_twist, up_twist, self.limb_grp)
            mc.hide(lo_twist, up_twist)

            # vis switch
            mc.connectAttr(blend_chain.switch.attr, rev + '.inputZ')
            mc.connectAttr(blend_chain.switch.attr,
                             self.fk_ctrls[0].top + '.visibility')
            mc.connectAttr(rev + '.outputZ', self.ik_ctrl_grp + '.visibility')



        if self.segments:
            self.src_chain.split_chain(segments=self.segments)
            self.src_joints = []
            for jnt in self.src_chain.joints[:-1]:
                split_list = self.src_chain.split_jnt_dict[jnt]
                for s_jnt in split_list:
                    self.src_joints.append(s_jnt)
            self.src_joints.append(self.src_chain.joints[-1])

        if self.twisty:
            # up limb
            self.src_chain.twist_chain(start_translate=self.src_chain.joints[1],
                                       start_rotate=self.src_chain.joints[0],
                                       end_translate=self.src_chain.joints[0],
                                       end_rotate=self.src_chain.joints[0],
                                       twist_bone=self.src_chain.joints[0],
                                       twist_driver=up_twist,
                                       reverse=True)
            # lo limb
            self.src_chain.twist_chain(start_translate=self.src_chain.joints[2],
                                       start_rotate=self.src_chain.joints[1],
                                       end_translate=self.src_chain.joints[2],
                                       end_rotate=self.src_chain.joints[1],
                                       twist_bone=self.src_chain.joints[1],
                                       twist_driver=lo_twist)

        if self.bendy:
            if self.side == 'Rt':
                mirror = True
            else:
                mirror = False
            bend_01 = self.src_chain.bend_chain(bone=self.src_chain.joints[0],
                                                ctrl_scale=self.ctrl_scale,
                                                mirror=mirror,
                                                global_scale=self.global_scale.attr)
            bend_02 = self.src_chain.bend_chain(bone=self.src_chain.joints[1],
                                                ctrl_scale=self.ctrl_scale,
                                                mirror=mirror,
                                                global_scale=self.global_scale.attr)
            mc.parent(bend_01['control'], bend_02['control'],
                        self.control_grp)
            mc.parent(bend_01['module'], bend_02['module'], self.module_grp)

    def skeleton(self):
        limb_chain = rChain.Chain(transform_list=self.src_joints,
                                   side=self.side,
                                   suffix='JNT',
                                   name=self.part)
        if self.create_fk:
            poc = True
        else:
            poc = False
        limb_chain.create_from_transforms(orient_constraint=True,
                                          point_constraint=poc,
                                          scale_constraint=False,
                                          parent=self.skel)
        self.bind_joints = limb_chain.joints

        self.tag_bind_joints(self.bind_joints[:-1])
  
    def add_plugs(self):
        #print(self.pv_control)
        if self.part == 'leg':
            par = 'COG_M_JNT'
            driver_list = ['waist_M_CTRL',
                           'waist_M_CTRL', 
                           'waist_M_CTRL', 
                           self.base_name + '_IK_BASE_CTRL', 
                           'foot_' + self.side + '_01_ik_JNT',
                           'root_02_M_CTRL']
            driven_list = [self.limb_grp, 
                           self.base_name + '_IK_BASE_CTRL_CNST_GRP', 
                           self.base_name + '_01_fk_CTRL_CNST_GRP',
                           self.base_name + '_up_twist_LOC',
                           self.base_name + '_IK_MAIN_CTRL_CNST_GRP',
                           self.pv_control + '_CNST_GRP']
            hide_list = [self.base_name + '_IK_MAIN_CTRL_CNST_GRP',
                         self.base_name + '_IK_BASE_CTRL_CNST_GRP',
                         self.fk_ctrls[-1].top]
            pv_targets = ['CHAR',
                          'global_M_CTRL',
                          'root_02_M_CTRL',
                          'COG_M_CTRL',
                          'leg_' + self.side + '_IK_BASE_CTRL',
                          'foot_' + self.side + '_02_' + self.side + '_CTRL',
                          '2']
            pv_names = ['world', 'global', 'root', 'hip', 'leg', 'foot', 'default_value']
            ik_ctrl = ['foot_' + self.side + '_01_' + self.side + '_CTRL']
        elif self.part == 'arm':
            par = 'clavicle_' + self.side + '_02_JNT'
            driver_list = ['clavicle_' + self.side + '_02_driver_JNT',
                           'clavicle_' + self.side + '_02_driver_JNT',
                           'clavicle_' + self.side + '_02_driver_JNT',
                           'hand_' + self.side + '_01_ik_JNT',
                           'root_02_M_CTRL']
            driven_list = [self.limb_grp,
                           self.base_name + '_IK_BASE_CTRL_CNST_GRP',
                           self.base_name + '_up_twist_LOC',
                           self.base_name + '_IK_MAIN_CTRL_CNST_GRP',
                           self.pv_control + '_CNST_GRP']
            hide_list = [self.base_name + '_IK_MAIN_CTRL_CNST_GRP',
                         self.base_name + '_IK_BASE_CTRL_CNST_GRP']
            #hide_list = None
            pv_targets = ['CHAR',
                          'global_M_CTRL',
                          'root_02_M_CTRL',
                          'chest_M_01_CTRL',
                          'hand_' + self.side + '_local_CTRL',
                          '2']
            pv_names = ['world', 'global', 'root', 'hip', 'hand', 'default_value']
            ik_ctrl = ['hand_' + self.side + '_01_CTRL']

            rAttr.Attribute(node=self.part_grp, type='plug', value=['clavicle_' + self.side + '_02_driver_JNT'], name='pocRigPlugs', children_name=['arm_' + self.side + '_01_fk_CTRL_CNST_GRP'])
            target_list = ['chest_M_01_CTRL', 'chest_M_02_CTRL', 'clavicle_' + self.side + '_02_driver_JNT', '0']
            name_list = ['chest01', 'chest02', 'clavicle', 'default_value']
            orient_names = ['orient' + name.title() for name in name_list]
            rAttr.Attribute(node=self.part_grp, type='plug', value=target_list, name=self.fk_ctrls[0].ctrl + '_orient', children_name=orient_names)
        elif 'finger' in self.part:
            #print("plugging finger!")
            par = 'hand_' + self.side + '_JNT'
            driver_list = ['hand_' + self.side + '_JNT',
                           'hand_' + self.side + '_JNT',
                           'hand_' + self.side + '_JNT',
                           'root_02_M_CTRL',
                           'root_02_M_CTRL']
            driven_list = [self.limb_grp,
                           self.base_name + '_IK_BASE_CTRL_CNST_GRP',
                           self.base_name + '_01_fk_CTRL_CNST_GRP',
                           self.pv_control + '_CNST_GRP',
                           self.base_name + '_IK_MAIN_CTRL_CNST_GRP']
            hide_list = [self.base_name + '_IK_BASE_CTRL_CNST_GRP']
            pv_targets = ['CHAR',
                          'global_M_CTRL',
                          'root_02_M_CTRL',
                          'chest_M_01_CTRL',
                          'hand_' + self.side + '_local_CTRL',
                          '2']
            pv_names = ['world', 'global', 'root', 'hip', 'hand', 'default_value']
            ik_ctrl = None

        else:
            par = 'insert limb plug here'
            driver_list = ['driver list']
            driven_list = ['driven list']
            hide_list = ['hide list']
            ik_ctrl = ['ik ctrl']

        switch_attr = self.part.lower() + self.side.capitalize() + '_IKFK'
        rAttr.Attribute(node=self.part_grp, type='plug', value=[par], name='skeletonPlugs', children_name=[self.bind_joints[0]])
        rAttr.Attribute(node=self.part_grp, type='plug', value=driver_list, name='pacRigPlugs', children_name=driven_list)
        rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(hide_list)], name='hideRigPlugs', children_name=['hideNodes']) if hide_list else None
        rAttr.Attribute(node=self.part_grp, type='plug', value=pv_targets, name=self.pv_ctrl.ctrl + '_parent', children_name=pv_names)
        rAttr.Attribute(node=self.part_grp, type='plug', value=[switch_attr], name='switchRigPlugs', children_name=['ikFkSwitch'])
        rAttr.Attribute(node=self.part_grp, type='plug', value=ik_ctrl, name='transferAttributes', children_name=[self.main_ctrl.ctrl]) if ik_ctrl else None