import maya.cmds as mc
from importlib import reload

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
reload(rAttr)
reload(rChain)
reload(rChain)
reload(rGuide)

class Ik:
    def __init__(self, side=None, part=None, guide_list=None, ctrl_scale=1, sticky=None, solver=None, pv_guide='auto', offset_pv=0, slide_pv=None, stretchy=None):
        self.side = side
        self.part = part
        self.base_name = part + '_' + side

        self.guide_list=guide_list
        self.ctrl_scale = ctrl_scale
        self.sticky = sticky
        self.solver = solver
        self.pv_guide = pv_guide
        self.offset_pv = offset_pv
        self.slide_pv = slide_pv
        self.stretchy = stretchy

        self.check_solvers()
        self.check_pv_guide()

        if self.guide_list:
            if not isinstance(self.guide_list, list):
                self.guide_list = [self.guide_list]

    def build_ik(self):
        self.build_ik_controls()
        self.build_ik_chain()
        self.build_ikh()

    def check_solvers(self):
        if not self.sticky:
            self.sticky = 'sticky'
        if not self.solver:
            self.solver = 'ikRPsolver'

        if self.solver == 'ikRPsolver':
            self.s_name = 'RP'
        elif self.solver == 'ikSCsolver':
            self.s_name = 'SC'
            self.pv_guide = False
        elif self.solver == 'ikSplineSolver':
            self.s_name = 'spline'
        elif self.solver == 'ikSpringSolver':
            self.s_name = 'spring'
        else:
            mc.error("Invalid solver specified.")

    def check_pv_guide(self):
        if self.pv_guide == 'auto':
            self.pv_guide = rGuide.create_pv_guide(guide_list=self.guide_list, name=self.base_name, slide_pv=self.slide_pv, offset_pv=self.offset_pv, delete_setup=True)
            #self.pv_guide = rGuide.clean_pv_guide(guide_list=self.guide_list, name=self.base_name, offset_pv=self.offset_pv)

    def build_ik_controls(self):
        attr_util = rAttr.Attribute(add=False)
        self.ik_ctrl_grp = mc.group(empty=True, name=self.base_name + "_IK_CTRL_GRP")
        self.base_ctrl = rCtrl.Control(parent=self.ik_ctrl_grp, shape='cube', side=None, suffix='CTRL', name=self.base_name +"_IK_BASE", axis='y', group_type='main', rig_type='primary', translate=self.guide_list[0], ctrl_scale=self.ctrl_scale)
        attr_util.lock_and_hide(node=self.base_ctrl.ctrl, translate=False, rotate=False)
        self.base_ctrl.tag_as_controller()
        
        self.main_ctrl = rCtrl.Control(parent=self.ik_ctrl_grp, shape='cube', side=None, suffix='CTRL', name=self.base_name +"_IK_MAIN", axis='y', group_type='main', rig_type='primary', translate=self.guide_list[-1], ctrl_scale=self.ctrl_scale)
        attr_util.lock_and_hide(node=self.main_ctrl.ctrl, translate=False, rotate=False)
        self.main_ctrl.tag_as_controller()

        if self.pv_guide:
            self.pv_ctrl = rCtrl.Control(parent=self.ik_ctrl_grp, shape='locator_3D', side=None, suffix='CTRL', name=self.base_name +"_IK_PV", axis='y', group_type='main', rig_type='pv', translate=self.pv_guide, ctrl_scale=self.ctrl_scale)
            attr_util.lock_and_hide(node=self.pv_ctrl.ctrl, translate=False)
            self.pv_ctrl.tag_as_controller()

        return self.pv_ctrl.ctrl

    def build_ik_chain(self):
        self.ik_chain = rChain.Chain(transform_list=self.guide_list, side=self.side, suffix=self.s_name + '_JNT', name=self.part)
        self.ik_chain.create_from_transforms(static=True)
        self.ik_joints = self.ik_chain.joints

    def build_ikh(self, scale_attr=None, constrain=True):
        self.ikh = mc.ikHandle(name=self.base_name + "_IKH", startJoint=self.ik_joints[0], endEffector=self.ik_joints[-1], sticky=self.sticky, solver=self.solver)[0]

        if constrain:
            mc.parentConstraint(self.base_ctrl.ctrl, self.ik_joints[0], mo=True)
            mc.parentConstraint(self.main_ctrl.ctrl, self.ikh, mo=True)

        if self.pv_guide:
            mc.poleVectorConstraint(self.pv_ctrl.ctrl, self.ikh)
            guide = rGuide.create_line_guide(a=self.pv_ctrl.ctrl, b=self.ik_joints[1], name=self.base_name)
            self.guide_group = mc.group(guide['curve'], guide['clusters'], parent=self.ik_ctrl_grp, name=self.base_name+"_GUIDE_GRP")
            mc.setAttr(guide['curve'] + ".inheritsTransform", 0)

        if self.stretchy:
            if not scale_attr:
                scale_attr = rAttr.Attribute(node=self.base_ctrl.ctrl, type='double', value=1, keyable=True, name='globalScale')
            
            self.stretch_switch = rAttr.Attribute(node=self.main_ctrl.ctrl, type='double', value=0, keyable=True, name='stretch', max=1, min=0)

            dist = mc.createNode('distanceBetween', name=self.base_name + "_stretch_DIST")
            mdn = mc.createNode('multiplyDivide', name=self.base_name + "_stretch_MDN")
            mdl = mc.createNode('multDoubleLinear', name=self.base_name + "_stretch_MDL")
            cond = mc.createNode('condition', name=self.base_name + "_stretch_COND")
            bta = mc.createNode('blendTwoAttr', name=self.base_name + "_stretch_switch_BTA")

            # connect ik controls to drive distance calculation
            mc.connectAttr(self.base_ctrl.ctrl + '.worldMatrix[0]', dist + '.inMatrix1')
            mc.connectAttr(self.main_ctrl.ctrl + '.worldMatrix[0]', dist + '.inMatrix2')

            # connect global scale attr to MDL in order to normalize scale
            mc.connectAttr(scale_attr.attr, mdl + '.input1')
            mc.setAttr(mdl + '.input2', self.ik_chain.chain_length)

            # connect dist and mdn/mdl
            mc.connectAttr(dist + '.distance', mdn + '.input1X')
            mc.connectAttr(mdl + '.output', mdn + '.input2X')
            mc.setAttr(mdn + '.operation', 2)

            # condition: if (start/end len == total len) stretch
            mc.connectAttr(dist + '.distance', cond + '.firstTerm')
            mc.connectAttr(mdl + '.output', cond + '.secondTerm')
            mc.connectAttr(mdn + '.outputX', cond + '.colorIfTrueR')
            mc.setAttr(cond + '.operation', 3)

            # connect condition output to bta blend value
            mc.setAttr(bta + '.input[0]', 1)
            mc.connectAttr(cond + '.outColorR', bta + '.input[1]')
            mc.connectAttr(self.stretch_switch.attr, bta + '.attributesBlender')

            # scale each joint's y accordingly
            for joint in self.ik_joints[:-1]:
                mc.connectAttr(bta + '.output', joint + '.scaleY')



