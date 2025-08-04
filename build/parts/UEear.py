import maya.cmds as mc
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


class UEear(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        side = prefix.split('_')[-1]  # "L"

        root_jnt, root_ctrl, root_offset = UEface.Simple_joint_and_Control(
            guide=f'{prefix}_Root',
            overwrite=True,
            overwrite_name=f'{prefix}_Root',
            orient=True,
            CTRL_Size=3,
            JNT_Size=0.9,
            CTRL_Color=(1, 0.6, 0)
        )
        for guides in ['Upper', 'Lower', 'Outer']:
            jnt, ctrl, offset = UEface.Simple_joint_and_Control(
                guide=f'{prefix}_{guides}',
                overwrite=True,
                overwrite_name=f'{prefix}_{guides}',
                orient=True,
                CTRL_Size=1,
                JNT_Size=0.9,
                CTRL_Color=(1, 0.6, 0)
            )
            mc.parent(f'{prefix}_{guides}_{side}_CTRL_CNST_GRP', root_ctrl)
            mc.parent(jnt, root_jnt)
