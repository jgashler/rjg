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

class Part(rModule.RigModule):
    # constructor. see init parameter comments for info.
    def __init__(self,
                 side=None,             # string. which side of the rig (L, R, M)
                 part=None,             # string. part name (spine, arm, etc.)
                 guide_list=None,       # [string]. list of names of guides to be iterated over during build.
                 ctrl_scale=None,       # float. base scale value for all controls on this part.
                 model_path=None,       # string. path to model.
                 guide_path=None):      # string. path to guides.
        
        # initialize super class RigModule
        super().init(side=side,
                     part=part,
                     guide_list=guide_list,
                     ctrl_scale=ctrl_scale,
                     model_path=model_path,
                     guide_path=guide_path)
        
        # base name conventions: part_side. used for naming objects.
        self.base_name = self.part + '_' + self.side

        self.create_module()

    # main function to call other functions.
    def create_module(self):
        # RigModule.create_module(), buildPart.create_module()
        # ensures that model and guides are loaded, generates basic hierarchy groups, creates global scale attr
        super.create_module()

        self.control_rig()
        self.output_rig()
        self.skeleton()
        self.add_plugs()

    # create all controls using the Control class
    def control_rig(self):
        # create parent controls first
        # so that they can be set as the parent parameter for their children
        pass

    # create rig systems and joints
    def output_rig(self):
        # create empty group at first guide
        # build systems and/or joints and place in the part group
        # parent constrain joints to controls
        pass

    # create chain from joints
    def skeleton(self):
        # create chain
        # tag any bind joints
        pass

    # create extra attributes to be used during finalization stage (see ../post/finalize.py)
    def add_plugs(self):
        # skeletonPlugs
        # indicate input/output joints in order to connect skeleton components
        # rAttr.Attribute(node=self.part_grp, type='plug', value=['PARENT_JNT'], name='skeletonPlugs', children_name=['CONNECTED_CHILD_JNT'])

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
