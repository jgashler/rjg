import maya.cmds as mc
from importlib import reload

import rjg.libs.control.ctrl as rCtrl
import rjg.libs.common as rCommon
import rjg.libs.attribute as rAttr
import rjg.libs.transform as rXform
import rjg.libs.math as rMath
reload(rCtrl)
reload(rCommon)
reload(rAttr)
reload(rXform)
reload(rMath)

class Chain:
    def __init__(self, transform_list=None, label_chain=True, side='M', suffix='JNT', name='default'):
        self.transform_list = transform_list
        self.label_chain = label_chain
        self.side = side
        self.suffix = suffix
        self.name = name
        self.split_jnt_dict = None

    