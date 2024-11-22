import maya.cmds as mc
import rjg.libs.util as rUtil


def export_frames(obj, dir, names):
    maxFrames = int(mc.playbackOptions(q=True, max=True))
    minFrames = int(mc.playbackOptions(q=True, min=True))

    for f in range(minFrames, maxFrames+1):
        mc.currentTime(f)
        #mc.select(obj)
        dup = mc.duplicate(obj)[0]
        mc.delete(dup, ch=True)
        mc.select(dup)
        mc.file(dir + '/' + names + '_' + str(f).zfill(5) + '.mb', es=True, typ='mayaBinary', force=True)
        mc.delete(dup)
        
    mc.currentTime(minFrames)
    mc.select(clear=True)
    
#export_frames('proxyClothes_sim', '/groups/dungeons/character/Rigging/proxy sim proof/proxy_sim_proof_frames_8pt2', 'test')


def import_frames(dir, names, min, max, pre, post):
    for f in range(min, max+1):
        new = mc.file(dir + '/' + names + '_' + str(f).zfill(5) + '.mb', i=True, namespace='proxy_sim_proof_clothSim')
        mc.rename(pre + (str(f) if f > 0 else '') + post, 'f_' + str(f).zfill(5))
        
#import_frames('/groups/dungeons/character/Rigging/proxy sim proof/proxy_sim_proof_frames_8pt2', 'test', 0, 1000, 'proxy_sim_proof_clothSim', ':proxyClothes_sim1')

def clean_frames_file(duration, interval):
    for f in range(duration+1):
        if f == 0 or (f % (2*interval)) > interval or (f % (2*interval)) == 0:
            mc.delete('f_' + str(f).zfill(5))
            
#clean_frames_file(1000, 20)


def create_pose_interpolator(joint, twistAxis):
    ta = 'xyz'.index(twistAxis)
    mc.select(joint)
    mel.eval(f'createPoseInterpolatorNode {joint}_poseInterpolator 1 {ta}')
    mc.setAttr(f'{joint}_poseInterpolator.allowNegativeWeights', 0)


def create_poses(pose_interp, shape, name, psf_namespace, start_frame, end_frame, interval, ofst=0):
    mc.select(shape)
    if not mc.objExists(name):
        mc.blendShape(automatic=True, name=name)
        mc.setAttr(name + '.nodeState', 1)
        
    pose = 3
    for f in range(start_frame, end_frame+1, 2*interval):
        mc.currentTime(f)
        mel.eval(f'poseInterpolatorAddPose {pose_interp} f_{str(f).zfill(5)}_pose')
        mc.setAttr(f'{pose_interp}Shape.pose[{pose}].poseType', 1)
        target_shape = f'{psf_namespace}:f_{str(f).zfill(5)}'
        mc.blendShape(name, e=True, t=[f'{shape}Shape', pose-3+ofst, target_shape, 1])
        mc.connectAttr(f'{pose_interp}Shape.output[{pose}]', f'{name}.f_{str(f).zfill(5)}')
        
        pose += 1
        
    pose = 3
    for f in range(start_frame, end_frame+1, 2*interval):
        for sub_f in range(f-interval+1, f):
            mc.currentTime(sub_f)
            ib_target_shape = f'{psf_namespace}:f_{str(sub_f).zfill(5)}'
            ib_weight = mc.getAttr(f'{pose_interp}Shape.output[{pose}]')
            mc.blendShape(name, e=True, ib=True, t=[shape, pose-3+ofst, ib_target_shape, round(ib_weight, 3)], ibt='absolute')
            
        pose += 1
                
    mc.currentTime(0)
    mc.setAttr(name + '.nodeState', 0)
    mc.select(clear=True)
        
        
create_pose_interpolator('joint2', 'x')
create_pose_interpolator('joint3', 'x')
create_pose_interpolator('joint4', 'x')

# create_poses('joint2_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 20, 160, 20)
# create_poses('joint3_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 180, 320, 20, 4)
# create_poses('joint4_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 340, 480, 20, 8)

create_poses('joint2_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 'proxy_sim_frames_8pt', 20, 320, 20)
create_poses('joint3_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 'proxy_sim_frames_8pt', 180, 640, 20, 8)
create_poses('joint4_poseInterpolator', 'proxyClothes_nosim', 'proxyClothes_BS', 'proxy_sim_frames_8pt', 340, 960, 20, 16)

# rUtil.create_pxWrap('realClothes', 'proxyClothes_nosim')