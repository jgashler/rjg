import maya.cmds as mc
import json

def connectUSDAttr():
    
    try:
        USD_attr = mc.getAttr('FaceAtOrigin.USD_UserExportedAttributesJson')
        mc.select('*_UBM')
        ubm = mc.ls(selection=True)[0]
        mc.addAttr(longName='USD_UserExportedAttributesJson', dt='string')
        mc.setAttr(ubm + '.USD_UserExportedAttributesJson', USD_attr, type ='string', )
    except Exception as e:
        mc.warning('connectUSDAttr:', e)
        return


    as_json = json.loads(USD_attr)
    for attr in as_json:
        mc.select(ubm)
        try:
            mc.addAttr(longName=attr, at='double')
            mc.connectAttr('FaceAtOrigin.' + attr, ubm + '.' + attr)
        except Exception as e:
            mc.warning('connectUSDAttr:', e)