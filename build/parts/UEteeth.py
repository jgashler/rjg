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


class UEteeth(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        UEface.Simple_joint_and_Control(
            guide=f'topTeeth',
            overwrite=True,
            overwrite_name=f'TopTeeth',
            orient=True,
            CTRL_Size=.5,
            JNT_Size=0.5,
            CTRL_Color=(1, 0.6, 0),
            bind = False
        )
        UEface.Simple_joint_and_Control(
            guide=f'botTeeth',
            overwrite=True,
            overwrite_name=f'BotTeeth',
            orient=True,
            CTRL_Size=.5,
            JNT_Size=0.5,
            CTRL_Color=(1, 0.6, 0),
            bind = False
        )

        index = 1
        guides = []

        while True:
            guide_name = f'Tounge_{index:02d}'  # formats as 01, 02, 03, etc.
            if mc.objExists(guide_name):
                guides.append(guide_name)
                UEface.Simple_joint_and_Control(
                    guide=guide_name,
                    overwrite=True,
                    overwrite_name=guide_name,
                    orient=True,
                    CTRL_Size=.5,
                    JNT_Size=0.5,
                    CTRL_Color=(1, 0.6, 0),
                    bind = False
                )
                if index != 1:
                    old_index = index - 1 
                    mc.parent(f'{guide_name}_0{index}_CTRL_CNST_GRP', f'{last_guide}_0{old_index}_CTRL')

                last_guide = guide_name
                index += 1
            else:
                break  # stop if the guide doesn't exist
        
        UEface.chain_parts(guides, joints=True, controls=True)

