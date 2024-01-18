import maya.cmds as mc
import json, os
from importlib import reload

def place_guides(model, directory, filename):
    path = directory + filename
    if os.path.isfile(path):
        file = open(path, 'r')
        guide_data = json.loads(file.read())
    else:
        mc.error('Guides file {} does not exist.'.format(path))
    
    guides = []
    for type, value in guide_data.items():
        if type[:5] == "chain":
            guides.append(place_chain(model, value))
        if type[:6] == "vertex":
            guides.append(place_vertices(model, value))
            
    mc.group(guides, n="GUIDES")
            
def place_vertices(model, vertices):
    info = []
    for item in vertices:
        for k, v in item.items():
            info.append((v, k))
    
    jnts = []
    for v in range(len(info)):
        mc.select(cl=True)
        vtx = mc.xform(model + '.vtx[{}]'.format(info[v][0]), q=True, t=True, ws=True)
        j = mc.joint(p=vtx, n=info[v][1])
        jnts.append(j)
    
    return mc.group(jnts, n = "guide_GRP")


def place_chain(model, chain):
    # build list of targets from json-dict
    info = []
    for item in chain:
        for k, v in item.items():
            info.append((v, k))
    
    loops = []
    
    # create curve based on edges
    for i in info:
        r = model + '.e[{}]'.format(i[0])
        c = mc.polyToCurve(r)
        mc.xform(c, cp=True)
        loops.append(c)
        
    mc.select(cl=True)
    jnts = []
    
    # place joints at center of each curve
    for i, loop in enumerate(loops):
        j = mc.joint(n='{}'.format(info[i][1]))
        mc.matchTransform(j, loop)
        jnts.append(j)
        mc.delete(loop)
        
    # orient joints (YZZ)
    for j in range(len(jnts)-1):
        mc.joint(jnts[j], e=True, oj='yzx', sao='zdown', zso=True)
    mc.joint(jnts[-1], e=True, oj='none', zso=True)
    
    return jnts[0]
    
place_guides('pCylinder1', 'C:/Users/jgash/Documents/maya/scripts/rjg/demos', 'UBM_test.json')

