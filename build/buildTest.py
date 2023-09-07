import maya.cmds as mc

def buildSphere(name = 'hoinky'):
    sph = mc.polySphere(n=name, ch=False)[0]
    return sph