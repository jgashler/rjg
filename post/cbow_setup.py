import maya.cmds as mc

try:
    mc.createNode('script', n='vis_setup')
    mc.setAttr('vis_setup.scriptType', 1)
    mc.setAttr('vis_setup.before', "import maya.cmds as mc; mc.connectAttr('Rayden:switch_CTRL.staticCbowRiggedCbow', 'Crossbow:ROOT.visibility');", type='string')
    mc.setAttr('vis_setup.sourceType', 1)
except Exception as e:
    print('vis_setup error:', e)

try:
    mc.createNode('script', n='spsw_setup')
    mc.setAttr('spsw_setup.scriptType', 1)
    mc.setAttr('spsw_setup.before', "import maya.cmds as mc; import pipe.m.space_switch as spsw; mc.select('Rayden:chest_M_02_CTRL', 'Rayden:arm_R_03_fk_CTRL', 'Rayden:arm_L_03_fk_CTRL', 'Crossbow:Crossbow_Global_CTRL'); spsw.run();", type='string')
    mc.setAttr('spsw_setup.sourceType', 1)
except Exception as e:
    print('spsw_setup error:', e)