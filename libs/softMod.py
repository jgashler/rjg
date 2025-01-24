'''

Written by Josh Sobel
joshsobel89@gmail.com
http://www.joshsobelrigs.com

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
import os
#from six.moves import range

#import js_stickyMod.stickyMod_funcs as funcs
#reload (funcs)

'''

Written by Josh Sobel
joshsobel89@gmail.com
http://www.joshsobelrigs.com

'''



def createOffsetGrp(sel = 'NOTHING SELECTED'): 
	import maya.cmds as mc
	
	sel = mc.ls(sl=True)
	offsGrps = []
	
	for x in range(len(sel)):
		offsGrps.append(mc.group(sel[x],name=sel[x]+'_offset'))
		mc.select(offsGrps[x],sel[x])
		mc.matchTransform(piv=True)
	
	mc.select(sel,offsGrps)
	
	return offsGrps


##############
### Basics ###
##############



def rivet_sel (loc = 0):

	sel = cmds.ls (sl = 1, fl = 1)
	if len(sel) == 1:
		if '.vtx[' in sel[0]:
			surf = cmds.ls (sl = 1, o = 1)[0]
			riv = rivet (sel[0], surf, loc = loc)
			return riv
		else:
			cmds.warning ('Select 1 vertex.')
	else:
		cmds.warning ('Select 1 vertex.')

def rivet (vtx, surf, outGeo = '', loc = 0):

	# Get geo
	geo = cmds.listRelatives (surf, p = 1)[0]

	# Get vertex ID
	vtxId = vtx.split ('[')[1]
	vtxId = vtxId.split (']')[0]

	# Get adjacent edge
	edges1 = cmds.polyInfo (vtx, vertexToEdge = 1)[0]
	edges1 = edges1.split (':')[1]
	edges1 = edges1.split (' ')
	edges = []
	for i in edges1:
		if i:
			if '\n' not in i:
				edges.append (int(i))

	# Create a live curve on edge
	cme = cmds.createNode ('curveFromMeshEdge', n = '{}_edge_{}_CFME'.format (surf,edges[1]))
	cmds.setAttr ('{}.edgeIndex[0]'.format (cme), edges[1])
	if outGeo:
		cmds.connectAttr (outGeo, '{}.inputMesh'.format (cme))
	else:
		cmds.connectAttr ('{}.worldMesh'.format (surf), '{}.inputMesh'.format (cme))

	# Create a curve info node for edge curve
	poc = cmds.createNode ('pointOnCurveInfo', n = '{}_e{}_v{}_POC'.format (surf,edges[1],vtxId))
	cmds.setAttr ('{}.turnOnPercentage'.format (poc), 1)
	cmds.connectAttr ('{}.outputCurve'.format (cme), '{}.inputCurve'.format (poc))

	# Create rivet
	if loc == 1:
		riv = cmds.spaceLocator (n = '{}_RIV'.format (geo))[0]
	else:
		riv = cmds.createNode ('transform', n = '{}_RIV'.format (geo))
	cmds.connectAttr ('{}.result.position'.format (poc), '{}.translate'.format (riv))

	# Check if at the correct end of the curve
	chk1 = cmds.xform (riv, q = 1, ws = 1, t = 1)
	chk2 = cmds.xform (vtx, q = 1, ws = 1, t = 1)
	if chk1 != chk2 :
		cmds.setAttr ('{}.parameter'.format (poc), 1)

	# Create a normal constraint to orient
	cnst = cmds.normalConstraint (surf, riv, n = '{}_nrml_CNST'.format (riv), aim = [0,1,0], u = [1,0,0])[0]
	if outGeo:
		con = cmds.listConnections ('{}.target[0].targetGeometry'.format (cnst), d = 0, p = 1)[0]
		cmds.disconnectAttr (con, '{}.target[0].targetGeometry'.format (cnst))
		cmds.connectAttr (outGeo, '{}.target[0].targetGeometry'.format (cnst))
	cmds.connectAttr ('{}.tangent'.format (poc), '{}.worldUpVector'.format (cnst))
	cmds.setAttr ('{}.hiddenInOutliner'.format (cnst), 1)

	return riv



def stickyMod (surf, falloff = 1):

	sm_dfrm,sm_hdl = cmds.softMod (surf)
	sm_shp = cmds.listRelatives (sm_hdl, c = 1)[0]
	cmds.setAttr ('{}.visibility'.format (sm_shp), 0)
	cmds.setAttr ('{}.visibility'.format (sm_hdl), l = 1, k = 0)
	cmds.setAttr ('{}.rp'.format (sm_hdl), 0, 0, 0)
	cmds.setAttr ('{}.sp'.format (sm_hdl), 0, 0, 0)
	cmds.setAttr('{}.falloffAroundSelection'.format (sm_dfrm), 0)
	cmds.addAttr (sm_hdl, ln = 'envelope', at = 'float', dv = 1, min = 0, max = 1, k = 1)
	cmds.connectAttr ('{}.envelope'.format (sm_hdl), '{}.envelope'.format (sm_dfrm))
	cmds.addAttr (sm_hdl, ln = 'falloffRadius', at = 'float', min = .001, dv = falloff, k = 1)
	cmds.connectAttr ('{}.falloffRadius'.format (sm_hdl), '{}.falloffRadius'.format (sm_dfrm))
	cmds.setAttr ('{}.displayHandle'.format (sm_hdl), 1)
	cmds.connectAttr ('{}.worldMatrix'.format (surf), '{}.geomMatrix[0]'.format (sm_dfrm))
	outGeo = cmds.listConnections ('{}.input[0].inputGeometry'.format (sm_dfrm), plugs = 1)[0]

	rslt = sm_dfrm, sm_hdl, outGeo
	return rslt



###########
### Run ###
###########



def run_sel (falloff = 1, color = 22, sphVis = 1, smooth = 3, lra = 1, mode = 0, scale = 1):

	tsl = cmds.selectPref (q = 1, tso = 1)
	if tsl != 1:
		cmds.selectPref (tso = 1)

	sel = cmds.ls (sl = 1, o = 1)
	if sel:
		surf = sel[0]
		comps = cmds.ls (os = 1, fl = 1)
		bads = []
		for c in comps:
			if '.vtx' not in c and '.cv' not in c and '.u' not in c:
				bads.append (c)
		if not bads:
			comp = comps[-1]
			if '.vtx' in comp:
				sm = run_vtx (comp, surf, falloff = falloff, color = color, sphVis = sphVis, lra = lra, mode = mode, scale = scale)
				if len(comps) >= 2:
					cmds.setAttr ('{}.falloffRadius'.format (sm[1]), 5000)
					cmds.setAttr ('{}.sphere'.format (sm[1]), 0)
					floodReplace (comps, sm[0])
					if smooth >= 1:
						floodSmooth (comps, sm[0], smooth = smooth)
					sys.stdout.write ('Sticky Mod created in multi-vertex mode. Map has been flooded, Falloff Radius set to 100, and sphere visibility disabled.')
				else:
					sys.stdout.write ('Sticky Mod created!')
				cmds.select (sm[1])
			elif '.u' in comp:
				if len(comps) == 1:
					sm = run_cp (comp, surf, falloff = falloff, color = color, sphVis = sphVis, lra = lra, mode = mode, scale = scale)
					sys.stdout.write ('Sticky Mod created!')
				else:
					cmds.warning ('Select at least 1 vertex on 1 mesh, or 1 curve point on 1 curve.')
			elif '.cv' in comp:
				cmds.warning ('Select at least 1 vertex on 1 mesh, or 1 curve point on 1 curve.')
			else:
				cmds.warning ('Select at least 1 vertex on 1 mesh, or 1 curve point on 1 curve.')
		else:
			cmds.warning ('Select at least 1 vertex on 1 mesh, or 1 curve point on 1 curve.')
	else:
		cmds.warning ('Select at least 1 vertex on 1 mesh, or 1 curve point on 1 curve.')


def run_vtx (vtx, surf, falloff = 1, color = 22, sphVis = 1, lra = 1, mode = 1, scale = 1):

	# Create soft mod
	sm = stickyMod (surf, falloff = falloff)
	sm_dfrm, sm_hdl, outGeo = sm

	# Create rivet
	riv = rivet (vtx, surf, outGeo = outGeo)

	# Create offset to drive falloff center
	off = cmds.circle (n = '{}_OFF'.format (sm_dfrm))[0]
	cmds.setAttr ('{}.sx'.format (off), .75)
	cmds.setAttr ('{}.sy'.format (off), .75)
	cmds.setAttr ('{}.sz'.format (off), .75)
	cmds.makeIdentity (off, a = 1, s = 1)
	cnst = cmds.parentConstraint (riv, off)
	cmds.delete (cnst)
	cmds.parent (off, riv)
	cmds.makeIdentity (off, a = 1, t = 1, r = 1, s = 1)
	inf = cmds.createNode ('transform', n = '{}_INF'.format (sm_hdl), p = riv)
	cmds.setAttr ('{}.hiddenInOutliner'.format (inf), 1)
	cmds.setAttr ('{}.inheritsTransform'.format (inf), 0)
	cmds.pointConstraint (off, inf)
	cmds.connectAttr ('{}.t'.format (inf), '{}.falloffCenter'.format (sm_dfrm), force = 1)

	cmds.setAttr ('{}.sx'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.sy'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.sz'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.v'.format (off), l = 1, k = 0)

	# Parent soft mod under rivet
	cmds.parent (sm_hdl, off, r = 1)
	cmds.connectAttr ('{}.pim'.format (sm_hdl), '{}.bindPreMatrix'.format (sm_dfrm), force = 1)

	# Finalize
	sm = [sm_dfrm, sm_hdl]
	sm = finalize (sm, surf, color = color, sphVis = sphVis, lra = lra, mode = mode, scale = scale)

	# Return result
	return sm



def run_cp (cp, surf, falloff = 1, color = 22, sphVis = 1, lra = 1, mode = 1, scale = 1):

	# Get geo
	geo = cmds.listRelatives (surf, p = 1)[0]

	# Create soft mod
	sm = stickyMod (surf, falloff = falloff)
	sm_dfrm, sm_hdl, outGeo = sm

	# Create pointOnCurveInfo
	poc = cmds.createNode ('pointOnCurveInfo', n = '{}_{}_POC'.format (surf,sm_hdl))
	param = cp.split ('[')[1]
	param = float(param.split (']')[0])
	cmds.setAttr ('{}.parameter'.format (poc), param)
	cmds.connectAttr (outGeo, '{}.inputCurve'.format (poc))

	# Create rivet
	riv = cmds.createNode ('transform', n = '{}_RIV'.format (geo))
	cmds.connectAttr ('{}.position'.format (poc), '{}.translate'.format (riv))

	# Create offset to drive falloff center
	off = cmds.circle (n = '{}_OFF'.format (sm_dfrm))[0]
	cmds.setAttr ('{}.sx'.format (off), .75)
	cmds.setAttr ('{}.sy'.format (off), .75)
	cmds.setAttr ('{}.sz'.format (off), .75)
	cmds.makeIdentity (off, a = 1, s = 1)
	cnst = cmds.parentConstraint (riv, off)
	cmds.delete (cnst)
	cmds.parent (off, riv)
	cmds.makeIdentity (off, a = 1, t = 1, r = 1, s = 1)
	inf = cmds.createNode ('transform', n = '{}_INF'.format (sm_hdl), p = riv)
	cmds.setAttr ('{}.hiddenInOutliner'.format (inf), 1)
	cmds.setAttr ('{}.inheritsTransform'.format (inf), 0)
	cmds.pointConstraint (off, inf)
	cmds.connectAttr ('{}.t'.format (inf), '{}.falloffCenter'.format (sm_dfrm), force = 1)

	cmds.setAttr ('{}.sx'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.sy'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.sz'.format (off), l = 1, k = 0)
	cmds.setAttr ('{}.v'.format (off), l = 1, k = 0)

	# Parent soft mod under rivet
	cmds.parent (sm_hdl, off, r = 1)
	cmds.connectAttr ('{}.pim'.format (sm_hdl), '{}.bindPreMatrix'.format (sm_dfrm), force = 1)

	# Finalize
	sm = [sm_dfrm, sm_hdl]
	sm = finalize (sm, surf, color = color, sphVis = sphVis, lra = lra, mode = mode, scale = scale)

	# Return result
	return sm



def finalize (sm, surf, color = 22, sphVis = 1, lra = 1, mode = 1, scale = 1):

	# Get names
	sm_dfrm = sm[0]
	sm_hdl = sm[1]
	off = cmds.listRelatives (sm_hdl, p = 1)[0]
	riv = cmds.listRelatives (off, p = 1)[0]
	geo = cmds.listRelatives (surf, p = 1)[0]
	if ':' in geo:
		geo = geo.split (':')[1]

	# Falloff
	cmds.addAttr (sm_hdl, ln = 'falloffMode_keyable', nn = 'Falloff Mode',  at = 'enum', en = 'Volume:Surface', k = 1)
	cmds.connectAttr ('{}.falloffMode_keyable'.format (sm_hdl), '{}.falloffMode'.format (sm_dfrm))

	# Falloff curve
	cmds.addAttr (sm_hdl, ln = 'falloffCurve', at = 'enum', en = 'None:Linear:Smooth:Spline', k = 1, dv = 2)
	cmds.connectAttr ('{}.falloffCurve'.format (sm_hdl), '{}.falloffCurve[0].falloffCurve_Interp'.format (sm_dfrm))

	# Sphere
	shp = cmds.listRelatives (off, s = 1)[0]
	crv2, make2 = cmds.circle (n = shp.replace ('Shape','2'), nr = [0,1,0])
	shp2 = cmds.listRelatives (crv2, s = 1)[0]
	cmds.setAttr ('{}.sx'.format (crv2), .75)
	cmds.setAttr ('{}.sy'.format (crv2), .75)
	cmds.setAttr ('{}.sz'.format (crv2), .75)
	#cmds.setAttr ('{}.ihi'.format (make2), 0)
	cmds.makeIdentity (crv2, a = 1, s = 1)
	crv3, make3 = cmds.circle (n = shp.replace ('Shape','3'), nr = [1,0,0])
	shp3 = cmds.listRelatives (crv3, s = 1)[0]
	cmds.setAttr ('{}.sx'.format (crv3), .75)
	cmds.setAttr ('{}.sy'.format (crv3), .75)
	cmds.setAttr ('{}.sz'.format (crv3), .75)
	#cmds.setAttr ('{}.ihi'.format (make3), 0)
	cmds.makeIdentity (crv3, a = 1, s = 1)
	cmds.parent (shp2, off, add = 1, s = 1)
	cmds.parent (shp3, off, add = 1, s = 1)

	hist = cmds.listHistory (shp)
	for h in hist:
		if 'makeNurbCircle' in h:
			make = h
			cmds.setAttr ('{}.ihi'.format (h), 0)
		if 'transformGeometry' in h:
			cmds.setAttr ('{}.ihi'.format (h), 0)

	hist = cmds.listHistory (shp2)
	for h in hist:
		if 'makeNurbCircle' in h:
			make2 = h
			cmds.setAttr ('{}.ihi'.format (h), 0)
		if 'transformGeometry' in h:
			cmds.setAttr ('{}.ihi'.format (h), 0)

	hist = cmds.listHistory (shp3)
	for h in hist:
		if 'makeNurbCircle' in h:
			make3 = h
			cmds.setAttr ('{}.ihi'.format (h), 0)
		if 'transformGeometry' in h:
			cmds.setAttr ('{}.ihi'.format (h), 0)

	cmds.connectAttr ('{}.falloffRadius'.format (sm_hdl), '{}.radius'.format (make))
	cmds.connectAttr ('{}.falloffRadius'.format (sm_hdl), '{}.radius'.format (make2))
	cmds.connectAttr ('{}.falloffRadius'.format (sm_hdl), '{}.radius'.format (make3))
	cmds.delete (crv2, crv3)
	cmds.addAttr (sm_hdl, ln = 'sphere', at = 'bool', dv = sphVis)
	cmds.setAttr ('{}.sphere'.format (sm_hdl), cb = 1)
	cmds.connectAttr ('{}.sphere'.format (sm_hdl), '{}.v'.format (shp))
	cmds.connectAttr ('{}.sphere'.format (sm_hdl), '{}.v'.format (shp2))
	cmds.connectAttr ('{}.sphere'.format (sm_hdl), '{}.v'.format (shp3))

	# LRA
	cmds.addAttr (sm_hdl, ln = 'localRotationAxis', at = 'bool', dv = lra)
	cmds.setAttr ('{}.localRotationAxis'.format (sm_hdl), cb = 1)
	cmds.connectAttr ('{}.localRotationAxis'.format (sm_hdl), '{}.displayLocalAxis'.format (sm_hdl))

	# Nurbs Curve
	crv = cmds.curve (d = 1, p = [(-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5), (-0.5,0.5,0.5), (-0.5,-0.5,0.5), (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,-0.5,0.5), (-0.5,-0.5,0.5), (0.5,-0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (0.5,-0.5,-0.5), (-0.5,-0.5,-0.5), (-0.5,0.5,-0.5)])
	crv_shp = cmds.listRelatives (crv, s = 1)[0]
	for a in ['sx','sy','sz']:
		cmds.setAttr ('{}.{}'.format (crv,a), .4)
	cmds.makeIdentity (crv, a = 1, s = 1)
	for a in ['sx','sy','sz']:
		cmds.setAttr ('{}.{}'.format (crv,a), scale)
	cmds.makeIdentity (crv, a = 1, s = 1)
	cmds.parent (crv, off)
	for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
		if 't' in a or 'r' in a:
			cmds.setAttr ('{}.{}'.format (crv,a), 0)
		elif 's' in a:
			cmds.setAttr ('{}.{}'.format (crv,a), 1)
	cmds.parent (crv_shp, sm_hdl, add = 1, s = 1)
	cmds.delete (crv)
	shps = cmds.listRelatives (sm_hdl, s = 1)
	for shp1 in shps:
		if 'curve' in shp1:
			crv_shp2 = shp1
	if mode == 1:
		vis_dv = 0
	elif mode == 2:
		vis_dv = 1
	cmds.addAttr (sm_hdl, ln = 'visualizationMode', at = 'enum', en = 'Handle:Nurbs Curve', dv = vis_dv)
	cmds.setAttr ('{}.visualizationMode'.format (sm_hdl), cb = 1)
	cmds.connectAttr ('{}.visualizationMode'.format (sm_hdl), '{}.v'.format (crv_shp2))
	rev = cmds.createNode ('reverse', n = '{}_REV'.format (sm_hdl))
	cmds.setAttr ('{}.ihi'.format (rev), 0)
	cmds.connectAttr ('{}.visualizationMode'.format (sm_hdl), '{}.inputX'.format (rev))
	cmds.connectAttr ('{}.outputX'.format (rev), '{}.displayHandle'.format (sm_hdl))

	# Color
	cmds.setAttr ('{}.overrideEnabled'.format (sm_hdl), 1)
	cmds.setAttr ('{}.overrideColor'.format (sm_hdl), color)

	# Group
	grp = 'stickyMods_GRP'
	if not cmds.objExists (grp):
		cmds.group (n = grp, em = 1, w = 1)
	geoGrp = '{}_MOD_GRP'.format (geo)
	if not cmds.objExists (geoGrp):
		cmds.group (n = geoGrp, em = 1, w = 1)
		cmds.parent (geoGrp, grp)
	cmds.parent (riv, geoGrp)

	# Layer
	dl = 'stickyMods_LAY'
	if not cmds.objExists (dl):
		cmds.createDisplayLayer (n = dl, e = 1)
		cmds.editDisplayLayerMembers (dl, grp)
		cmds.setAttr ('{}.color'.format (dl), color)
	try:
		cmds.disconnectAttr ('stickyMods_LAY.drawInfo', '{}.drawOverride'.format (shp))
		cmds.disconnectAttr ('stickyMods_LAY.drawInfo', '{}.drawOverride'.format (shp2))
		cmds.disconnectAttr ('stickyMods_LAY.drawInfo', '{}.drawOverride'.format (shp3))
	except:
		pass
	cmds.setAttr ('{}.overrideEnabled'.format (shp), 1)
	cmds.setAttr ('{}.overrideColor'.format (shp), 29)
	cmds.setAttr ('{}.overrideEnabled'.format (shp2), 1)
	cmds.setAttr ('{}.overrideColor'.format (shp2), 29)
	cmds.setAttr ('{}.overrideEnabled'.format (shp3), 1)
	cmds.setAttr ('{}.overrideColor'.format (shp3), 29)

	# Cleanup
	sms = cmds.ls ('{}_*_MOD'.format (geo))
	if sms:
		#cnt = len(sms) + 1
		nums = []
		for i in sms:
			spl = i.split ('{}_'.format (geo))[1]
			num = spl.split ('_')[0]
			nums.append (int(num))
		nums.sort ()
		cnt = nums[-1] + 1
	else:
		cnt = 1
	sm_hdl = cmds.rename (sm_hdl, '{}_{}_MOD'.format (geo,cnt))
	cmds.rename (crv_shp2, '{}_{}_CRVShape'.format (geo,cnt))
	sm_dfrm = '{}SoftMod'.format (sm_hdl)
	cmds.rename (riv, '{}_{}_MOD_RIV'.format (geo,cnt))
	cmds.rename (off, '{}_{}_MOD_OFF'.format (geo,cnt))
	sm_dfrm = cmds.rename (sm_dfrm, '{}_{}_MOD_DFRM'.format (geo,cnt))
	cmds.select (sm_hdl)
	sm = [sm_dfrm, sm_hdl]
	
	cmds.select(sm_hdl)
	createOffsetGrp()
	cmds.select(sm_hdl)


	return sm



#####################
### Utility Funcs ###
#####################



def floodReplace (comps, sm_dfrm):

	obj = str(comps[0]).split ('.')[0]
	cmds.hilite (obj, replace = 1)
	cmds.select (comps)

	mel.eval ('artSetToolAndSelectAttr( "artAttrCtx", "softMod.{}.weights" );'.format (sm_dfrm))
	mel.eval ('artAttrInitPaintableAttr;')
	mel.eval ('artAttrValues artAttrContext;')
	mel.eval ('artAttrPaintOperation artAttrCtx Replace;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	mel.eval ('artAttrCtx -e -value 0 `currentCtx`;')
	cmds.select (comps)
	mel.eval ('invertSelection;')
	mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')



def floodSmooth (comps, sm_dfrm, smooth = 3):

	obj = str(comps[0]).split ('.')[0]
	cmds.select (obj)
	cmds.hilite (obj, replace = 1)
	cmds.select ('{}.vtx[*]'.format (obj))

	mel.eval ('artSetToolAndSelectAttr( "artAttrCtx", "softMod.{}.weights" );'.format (sm_dfrm))
	mel.eval ('artAttrInitPaintableAttr;')
	mel.eval ('artAttrValues artAttrContext;')
	mel.eval ('artAttrPaintOperation artAttrCtx Smooth;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	cmds.select ('{}.vtx[*]'.format (obj))
	for i in range (smooth):
		mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')



def addGeo_sel ():

	sel = cmds.ls (sl = 1)
	added = 0
	if len(sel) >= 2:
		sm = ''
		for i in sel:
			if i.endswith ('_MOD'):
				sm_hdl = i
				cons = cmds.listConnections (sm_hdl)
				for c in cons:
					if i in c and (cmds.nodeType (c) == 'softMod'):
						sm = c
		if sm:
			for geo in sel:
				if geo != sm_hdl:
					try:
						addGeo (sm, geo)
						added = 1
					except:
						pass
		else:
			cmds.warning ("No stickyMod in selection.")

	if added == 1 and len(sel) >= 3:
		sys.stdout.write ("Added multiple meshes to '{}'.".format (sm))



def addGeo (sm, geo):

	surf = cmds.listRelatives (geo, s = 1, f = 1)[0]
	cnt = 0
	yes = 0
	while yes == 0:
		if cnt <= 100:
			try:
				cmds.deformer (sm, e = 1, g = geo)
				if not cmds.isConnected ('{}.worldMatrix'.format (surf), '{}.geomMatrix[{}]'.format (sm,cnt)):
					cmds.connectAttr ('{}.worldMatrix'.format (surf), '{}.geomMatrix[{}]'.format (sm,cnt))
					sys.stdout.write ("Added '{}' to '{}'.".format (geo,sm))
				yes = 1
			except:
				cnt += 1
		else:
			cmds.warning ("Couldn't add '{}' to '{}'.".format (geo,sm))
			break



def removeGeo_sel ():

	sel = cmds.ls (sl = 1)
	removed = 0
	if len(sel) >= 2:
		sm = ''
		for i in sel:
			if i.endswith ('_MOD'):
				sm_hdl = i
				cons = cmds.listConnections (sm_hdl)
				for c in cons:
					if i in c and (cmds.nodeType (c) == 'softMod'):
						sm = c
		if sm:
			for geo in sel:
				if geo != sm_hdl:
					try:
						removeGeo (sm, geo)
						removed = 1
					except:
						pass
		else:
			cmds.warning ("No stickyMod in selection.")

	if removed == 1 and len(sel) >= 3:
		sys.stdout.write ("Removed multiple meshes from '{}'.".format (sm))



def removeGeo (sm, geo):

	surf = cmds.listRelatives (geo, s = 1, f = 1)[0]
	cnt = 0
	yes = 0
	while yes == 0:
		if cnt <= 100:
			try:
				cmds.deformer (sm, e = 1, rm = 1, g = geo)
				cmds.disconnectAttr ('{}.worldMatrix'.format (surf), '{}.geomMatrix[{}]'.format (sm,cnt))
				yes = 1
				sys.stdout.write ("Removed '{}' from '{}'.".format (geo,sm))
			except:
				cnt += 1
		else:
			cmds.warning ("Couldn't remove '{}' from '{}'.".format (geo,sm))
			break



def breakRot_sel ():

	sel = cmds.ls (sl = 1)
	yes = 0
	if sel:
		for i in sel:
			try:
				breakRot (i)
				yes = 1
			except:
				pass
	if yes == 0:
		cmds.warning ("No stickyMods in selection.")



def breakRot (sm):

	off = cmds.listRelatives (sm, p = 1)[0]
	riv = cmds.listRelatives (off, p = 1)[0]

	cons = []
	con = cmds.listConnections ('{}.rx'.format (riv), d = 0, p = 1)
	if con:
		cons.append (con[0])
		cmds.disconnectAttr (con[0], '{}.rx'.format (riv))
	con = cmds.listConnections ('{}.ry'.format (riv), d = 0, p = 1)
	if con:
		cons.append (con[0])
		cmds.disconnectAttr (con[0], '{}.ry'.format (riv))
	con = cmds.listConnections ('{}.rz'.format (riv), d = 0, p = 1)
	if con:
		cons.append (con[0])
		cmds.disconnectAttr (con[0], '{}.rz'.format (riv))

	sys.stdout.write ("Broke rotations on the rivet for '{}'.".format (sm))

	return cons



def oriToWorld_sel ():

	sel = cmds.ls (sl = 1)
	yes = 0
	if sel:
		for i in sel:
			if i.endswith ('_MOD'):
				oriToWorld (i)
				yes = 1
		cmds.select (sel)
	if yes == 0:
		cmds.warning ("No stickyMods in selection.")



def oriToWorld (sm):

	off = cmds.listRelatives (sm, p = 1)[0]
	riv = cmds.listRelatives (off, p = 1)[0]

	loc = cmds.spaceLocator ()[0]
	cnst = cmds.orientConstraint (loc, off)
	cmds.delete (cnst,loc)



def aimAtObj_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) == 2:
			sm = ''
			for i in sel:
				if i.endswith ('_MOD'):
					sm = i
				else:
					obj = i
			if sm and obj:
				aimAtObj (obj, sm)
			cmds.select (sm)
		else:
			cmds.warning ("Select an object and a stickyMod.")
	else:
		cmds.warning ("Select an object and a stickyMod.")



def aimAtObj (obj, sm):

	off = cmds.listRelatives (sm, p = 1)[0]
	riv = cmds.listRelatives (off, p = 1)[0]

	cnst = cmds.aimConstraint (obj, off, aim = [0,0,1], u = [0,1,0], wut = 'scene')
	cmds.delete (cnst)

def ui ():

	version = 'v1.02'

	# Define

	win = 'stickyMod_win'
	width = 300
	height = 10
	bWidth = width - 35
	bWidth2 = bWidth * .494
	bHeight = 35
	bHeight2 = bHeight * .6
	bColor_green = [0.670,0.736,0.602]
	bColor_blue = [0.571,0.676,0.778]
	bColor_purple = [0.691,0.604,0.756]
	bColor_red = [0.765,0.525,0.549]
	bColor_brown = [0.804,0.732,0.646]

	if (cmds.window (win, exists = 1)):
		cmds.deleteUI (win)

	cmds.window (win, rtf = 1, t = 'Sticky Mod (edited)', s = 1, w = width)
	cmds.columnLayout (adj = 1, rs = 3, w = width)

	# Contents

	cmds.frameLayout ('jssm_stickyMod_fl', l = '                                 Sticky Mod {}'.format (version), cll = 0, mh = 8, mw = 15, w = width, ann = "Ride-along manipulator with adjustable falloff and placement for quick mesh adjustments.\nThis tool uses Handles and Nurbs Curves, which are turned on automatically if 'Force Display' is on.")
	cmds.columnLayout (adj = 0, rs = 3)

	cmds.text (l = "Select 1 vertex, then click 'Create Sticky Mod'. Select the new softMod control and mesh to 'Add Geo' to influence or 'Remove Geo' from influence", ww = 1, w = bWidth)

	cmds.separator (h = 6, style = 'none')

	cmds.iconTextButton (l = '                Create Sticky Mod', i = 'softMod.png', bgc = bColor_green, ann = "Creates a ride-along manipulator with adjustable falloff for quick mesh adjustments.\n* Select 1 vertex to run, or multiple vertices to ignore interactive falloff and auto-flood/smooth the map. When running on multiple, the rivet will be built on the last vert in the selection.\nThis tool uses Handles and Nurbs Curves, which are turned on automatically if 'Force Display' is on.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'sm_create()')
	cmds.rowColumnLayout (nc = 2, rs = [2,3], cs = [2,3])
	cmds.button (l = 'Add Geo', bgc = bColor_brown, ann = 'Add selected geo to selected sticky mod.', w = bWidth2, h = bHeight2, c = 'addGeo_sel ()')
	cmds.button (l = 'Remove Geo', bgc = bColor_brown, ann = 'Remove selected geo from selected sticky mod.', w = bWidth2, h = bHeight2, c = 'removeGeo_sel ()')
	'''cmds.button (l = 'Ori To World', bgc = bColor_brown, ann = 'Orient selected sticky mod to the world.', w = bWidth2, h = bHeight2, c = 'oriToWorld_sel ()')
	cmds.button (l = 'Aim At Sel', bgc = bColor_brown, ann = "Select an object and a sticky mod to aim the sticky mod's null at the object.", w = bWidth2, h = bHeight2, c = 'aimAtObj_sel ()')
	cmds.setParent ('..')
	cmds.button (l = 'Break Rivet Rotation', bgc = bColor_brown, ann = 'Break rotation follow on the null of the selected sticky mod.', h = bHeight2, w = bWidth, c = 'breakRot_sel ()')
	
	cmds.separator (h = 4, style = 'none')

	cmds.rowColumnLayout (nc = 5, rs = [3,3], cs = [3,3])
	cmds.text (l = '   Falloff Radius:  ', ann = 'Default value for Falloff Radius.')
	cmds.floatField ('jssm_sm_falloff_ff', v = 1, pre = 2, w = 40, ann = 'Default value for Falloff Radius.')
	cmds.text (l = '  Smooth Map:  ', ann = "If running on multiple verts for auto-flooding, the map will be smoothed this number of times.")
	cmds.intField ('jssm_sm_smooth_if', v = 3, min = 0, w = 40, ann = "If running on multiple verts for auto-flooding, the map will be smoothed this number of times.")
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')
	cmds.rowColumnLayout (nc = 4, cs = ([2,3],[3,3],[4,3]))
	cmds.optionMenu ('jssm_sm_vis_om', l = '      Mode:', w = 139, ann = 'Choose whether default visualization mode is a Nurbs Curve or a Handle. Set your viewport display options accordingly.')
	cmds.menuItem ('jssm_sm_vis1_mi', l = 'Handle')
	cmds.menuItem ('jssm_sm_vis2_mi', l = 'Nurbs Crv')


	cmds.text (l = '  Crv Scale: ', ann = 'Size the nurbs curve control is built at. Ignore if you prefer Handle mode.')
	cmds.floatField ('jssm_sm_scale_ff', v = 1, pre = 2, min = .001, w = 40, ann = 'Size the nurbs curve control is built at. Ignore if you prefer Handle mode.')
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')
	cmds.rowColumnLayout (nc = 4, cs = ([2,3],[3,3],[4,3]))
	cmds.text (l = '      ')
	cmds.checkBox ('jssm_sm_sphere_cb', l = 'Sphere   ', v = 0, ann = 'Radius display spheres will be turned off by default.')
	cmds.checkBox ('jssm_sm_lra_cb', l = 'Axis   ', v = 0, ann = 'Local Rotation Axes will be turned on be default.')
	cmds.checkBox ('jssm_sm_forceDisplay_cb', l = 'Force Display', v = 1, ann = 'Turns on viewport display for relevant object types on creation.')
	cmds.setParent ('..')
	cmds.setParent ('..')

	cmds.columnLayout (adj = 1, rs = 3)
	cmds.button (l = "Create Rivet", bgc = bColor_blue, w = bWidth2, h = bHeight2, ann = "Select a vertex and run.", c = "rivet_sel (loc = 1)")
	cmds.button (l = "Download 'AnimPolish' For More Finaling Tools", bgc = bColor_blue, w = bWidth2, h = bHeight2, c = "import webbrowser ; webbrowser.open('http://joshsobelrigs.com/animpolish')")
	cmds.setParent ('..')
	'''
	# Launch
	cmds.showWindow (win)
	cmds.window (win, e = 1, w = width, h = height)



def sm_create ():

	sphVis = False
	lra = False
	falloff = 3.0
	smooth = 3
	mode = 1
	scale = 1.0
	display = True
	run_sel (falloff = falloff, sphVis = sphVis, smooth = smooth, lra = lra, mode = 2, scale = scale)
	if display == 1:
		try:
			panel = cmds.getPanel (wf = 1)
			cmds.modelEditor (panel, e = 1, nurbsCurves = 1)
			if mode == 1 or lra == 1:
				cmds.modelEditor (panel, e = 1, handles = 1)
		except:
			try:
				cmds.modelEditor ('modelPanel4', e = 1, nurbsCurves = 1)
				if mode == 1 or lra == 1:
					cmds.modelEditor ('modelPanel4', e = 1, handles = 1)
			except:
				sys.stdout.write ("Sticky Mod created! However, relevant viewport display options were not enabled because a viewport was not found.")


#ui()