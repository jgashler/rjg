import maya.cmds as mc
from importlib import reload

import rjg.libs.file as rFile
import rjg.build.rigModule as rModule
import rjg.libs.attribute as rAttr
reload(rFile)
reload(rAttr)
reload(rModule)

class Prop():
    def __init__(self, name='prop', prop_filepath=None, target_names=None, target_list=None, char_ctrl=None, prop_ctrl=None):
        self.__dict__.update(locals())

        self.prop_setup()

    def import_prop(self):
        self.prop = rFile.import_hierarchy(self.prop_filepath, namespace='mixamorig')

    def space_switch_loc(self):
        self.ssl = mc.spaceLocator(name=self.name + '_PROP_SSL')[0]
        self.ssl_grp = mc.group(self.ssl, name=self.name + '_PROP')

        self.control_dict = {
                             "side" : 'P',
                             "name" : self.name,
                             "rig_groups" : 'prop',
                             "rig_type" : 'prop',
                             #"ctrl_scale" : self.ctrl_scale
                            }
        tag_string = str(self.control_dict)

        rAttr.Attribute(type='string', node=self.ssl, name='ctrlDict', value=tag_string, lock=True)

        rAttr.Attribute(node=self.ssl_grp, type='plug', value=self.target_list, name=self.ssl +'_parent', children_name=self.target_names)
    
    def prop_follow_loc(self):
        mc.parentConstraint(self.ssl, self.prop)
    
    def prop_setup(self):
        self.import_prop()
        self.space_switch_loc()
        self.prop_follow_loc()