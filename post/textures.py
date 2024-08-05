import maya.cmds as mc
import maya.mel as mel

def set_textures(character):
    mt = mc.ls(type='aiStandardSurface')

    if character == 'Rayden':
        path = 'production/character/rayden/tex/main/variants/default/src/'
        f_suff = 'SG_DiffuseColor_sRGB-Texture.1001.jpeg'
    elif character == 'Robin':
        path = 'production/character/robin/tex/main/variants/default/src/'
        f_suff = '1_BaseColor_ACEScg.1001.png'

    # create, connect, and configure file nodes for each shader
    for m in mt:
        file_name = m + f_suff
        mel.eval(f'shadingNode -asTexture -isColorManaged file -name "{m[:-3]}_file"; shadingNode -asUtility place2dTexture -name "{m[:-3]}_place2dTexture"; connectAttr -f {m[:-3]}_place2dTexture.coverage {m[:-3]}_file.coverage; connectAttr -f {m[:-3]}_place2dTexture.translateFrame {m[:-3]}_file.translateFrame; connectAttr -f {m[:-3]}_place2dTexture.rotateFrame {m[:-3]}_file.rotateFrame; connectAttr -f {m[:-3]}_place2dTexture.mirrorU {m[:-3]}_file.mirrorU; connectAttr -f {m[:-3]}_place2dTexture.mirrorV {m[:-3]}_file.mirrorV; connectAttr -f {m[:-3]}_place2dTexture.stagger {m[:-3]}_file.stagger; connectAttr -f {m[:-3]}_place2dTexture.wrapU {m[:-3]}_file.wrapU; connectAttr -f {m[:-3]}_place2dTexture.wrapV {m[:-3]}_file.wrapV; connectAttr -f {m[:-3]}_place2dTexture.repeatUV {m[:-3]}_file.repeatUV; connectAttr -f {m[:-3]}_place2dTexture.offset {m[:-3]}_file.offset; connectAttr -f {m[:-3]}_place2dTexture.rotateUV {m[:-3]}_file.rotateUV; connectAttr -f {m[:-3]}_place2dTexture.noiseUV {m[:-3]}_file.noiseUV; connectAttr -f {m[:-3]}_place2dTexture.vertexUvOne {m[:-3]}_file.vertexUvOne; connectAttr -f {m[:-3]}_place2dTexture.vertexUvTwo {m[:-3]}_file.vertexUvTwo; connectAttr -f {m[:-3]}_place2dTexture.vertexUvThree {m[:-3]}_file.vertexUvThree; connectAttr -f {m[:-3]}_place2dTexture.vertexCameraOne {m[:-3]}_file.vertexCameraOne; connectAttr {m[:-3]}_place2dTexture.outUV {m[:-3]}_file.uv; connectAttr {m[:-3]}_place2dTexture.outUvFilterSize {m[:-3]}_file.uvFilterSize;')
        mc.connectAttr(f'{m[:-3]}_file.outColor', f'{m}.baseColor')
        mc.setAttr(f'{m[:-3]}_file.fileTextureName', path + file_name, type='string')
        mc.setAttr(f'{m[:-3]}_file.uvTilingMode', 3)
        mc.setAttr(f'{m[:-3]}_file.colorSpace', 'ACEScg', type='string')
        mc.setAttr(f'{m[:-3]}_file.aiAutoTx', 0)
        mc.setAttr(f'{m[:-3]}_file.uvTileProxyQuality', 1)

    # create script node to load textures on file open
    if not mc.objExists('previewTex'):
        mc.createNode('script', n='previewTex')
    mc.setAttr('previewTex.scriptType', 1)
    mc.setAttr('previewTex.before', 'generateAllUvTilePreviews;', type='string')
        
