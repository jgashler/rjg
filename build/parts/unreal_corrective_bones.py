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

class Unreal_Correctives(rModule.RigModule):
    # constructor. see init parameter comments for info.
    def __init__(self,
                 side=None,             # string. which side of the rig (L, R, M)
                 part=None,             # string. part name (spine, arm, etc.)
                 guide_list=None,       # [string]. list of names of guides to be iterated over during build.
                 ctrl_scale=None,       # float. base scale value for all controls on this part.
                 model_path=None,       # string. path to model.
                 guide_path=None,
                 par_ctrl=None, par_jnt=None, root_loc=None):      # string. path to guides.
        
        # initialize super class RigModule
        super().__init__(side=side,part=part,guide_list=guide_list,ctrl_scale=ctrl_scale,model_path=model_path,guide_path=guide_path)
        
        self.__dict__.update(locals())
        
        # base name conventions: part_side. used for naming objects.
        self.base_name = self.part + '_' + self.side

        self.create_module()

    # main function to call other functions.
    def create_module(self):
        # RigModule.create_module(), buildPart.create_module()
        # ensures that model and guides are loaded, generates basic hierarchy groups, creates global scale attr
        super().create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    # create all controls using the Control class
    def control_rig(self):
        # create parent controls first
        # so that they can be set as the parent parameter for their children
        self.ctrls = []
        for guide in self.guide_list:
            self.corr_ctrl = rCtrl.Control(parent=self.control_grp, shape='circle', side=self.side, suffix='CTRL', name=guide, axis='z', group_type='main', rig_type='primary', translate=guide, rotate=guide, ctrl_scale=self.ctrl_scale)
            self.corr_ctrl.tag_as_controller()
            self.ctrls.append(self.corr_ctrl.ctrl)

    # create rig systems and joints
    def output_rig(self):
        # create empty group at first guide
        # build systems and/or joints and place in the part group
        # parent constrain joints to controls
        ue_correcitve_jnt_grp = mc.group(parent=self.module_grp, empty=True, name=self.base_name + '_JNT_GRP')
        mc.matchTransform(ue_correcitve_jnt_grp, self.par_ctrl)

        self.rig_jnts = []

        for guide in self.guide_list:
            self.corr_jnt = mc.joint('{}_{}_CTRL'.format(guide, self.side), name='{}_{}_JNT'.format(guide, self.side))
            mc.parentConstraint('{}_{}_CTRL'.format(guide, self.side), self.corr_jnt, mo=True)
            mc.parent(self.corr_jnt, ue_correcitve_jnt_grp)
            self.rig_jnts.append(self.corr_jnt)

    # create chain from joints
    def skeleton(self):
        # create chain
        # tag any bind joints
        self.root_chain = rChain.Chain(transform_list=[self.root_loc], side=self.side, suffix='JNT', name=self.base_name)
        self.root_chain.create_from_transforms(parent=self.skel, pad=False, parent_constraint=False)
        self.tag_bind_joints(self.root_chain.joints)
        for guide, rig_jnt in zip(self.guide_list, self.rig_jnts):
            child_chain = rChain.Chain(transform_list=[rig_jnt], side=self.side, suffix='JNT', name='{}_{}_Bind_JNT'.format(guide, self.side))
            child_chain.create_from_transforms(parent=self.skel, pad=False)
            mc.parent(child_chain.joints[0], self.root_chain.joints[0])
            self.tag_bind_joints(child_chain.joints)


    # create extra attributes to be used during finalization stage (see ../post/finalize.py)
    def add_plugs(self):
        # skeletonPlugs
        # indicate input/output joints in order to connect skeleton components
        # rAttr.Attribute(node=self.part_grp, type='plug', value=['PARENT_JNT'], name='skeletonPlugs', children_name=['CONNECTED_CHILD_JNT'])
        rAttr.Attribute(node=self.part_grp, type='plug', value=[self.par_jnt], name='skeletonPlugs', children_name=[self.root_chain.joints[0]])

        # for ctrl in self.ctrls:
        #     print(ctrl)
        #     rAttr.Attribute(node=self.part_grp, type='plug', value=self.par_ctrl, name='pacRigPlugs', children_name=[ctrl + '_CNST_GRP'])

        driver_list = [self.par_ctrl]*len(self.guide_list)
        driven_list = [x + '_CNST_GRP' for x in self.ctrls]

        rAttr.Attribute(node=self.part_grp, type='plug',
                            value=driver_list, name='pacRigPlugs',
                            children_name=driven_list)

        #mc.setAttr(self.self.root_chain.joints[0] + '.translate', (0, 0, 0))


        # hideRigPlugs, deleteRigPlugs
        # indicate controls to be hidden or deleted during finalization
        #                                                        space separated list
        # rAttr.Attribute(node=self.part_grp, type='plug', value=[' '.join(hide_list)], name='hideRigPlugs', children_name=['hideNodes'])

        # pacRigPlugs, pacPocRigPlugs, pocRigPlugs, orcRigPlugs
        # parent,      parent no rotate, point,     orient     
        # given a list of drivers and drivens, set up constraints based on these plug attrs
        # rAttr.Attribute(node=self.part_grp, type='plug', value=[driver1, driver2], name='pacRigPlugs', children_name=[driven1, driven2])

        # switchRigPlugs
        # give an object this plug attribute if it has IKFK switch attributes to be connected to the switch control
        # rAttr.Attribute(node=self.part_grp, type='plug', value=[switch_attr], name='switchRigPlugs', children_name=['ikFkSwitch'])

        # transferAttributes
        # tell an object which attributes to transfer to other objects and where
        # rAttr.Attribute(node=self.part_grp, type='plug', value=['transfer target'], name='transferAttributes', children_name=['obj to transfer'])
        pass
