'''import maya.cmds as mc
from importlib import reload
import re

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
import rjg.libs.transform as rXform
from rjg.build.UEface import UEface
reload(rAttr)
reload(rChain)
reload(rCtrl)
reload (rGuide)
reload(rXform)


class UEwing(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Wing', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        '''

