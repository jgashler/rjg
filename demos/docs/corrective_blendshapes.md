# Corrective blendshape workflow


### Setup

You can work on corrective blendshapes in a file separate from the rest of the rig without affecting the work of other artists. In order to create a new working file, you will want to build the most recent version of the rig and set up a few custom attributes to make working with thte rig possible. 

1. In Dungaya, under the `LnD_Rigging` shelf tab, run the `Build` tool. 

2. Select the character to build in the upper-right dropdown menu. 

4. Leave the `Build face` and `Build previs rig` boxes unchecked.

5. Click `Build` and wait a moment while the rig is built

6. When it is finished, select the `vis_CTRL` (eyeball shaped control on the floor to the right of the big gear) and change `Skel Vis` to `on` and `Model Display` and `Skel Display` to `Normal`. This will allow you to more easily select the mesh and joints. You will occasionally toggle `Skel Vis` whenever you want to hide/show the skeleton again, so remember this control.

7. To hide the clothes, go to the Outliner and find `ROOT/MODEL/{character}_EXTRAS`. Hide this group.

8. At this point, you have your own working file. Save it in the directory `/groups/dungeons/character/Rigging/Rigs/{character}/Skin` as `{character}_skinning_file_{your name}.mb`. Feel free to set up a versioning system, but keep things organized/consistent. If you do, it might be helpful to create a directory in `/Skin` to hold all your work.


### The Pose Editor

1. Open the Pose Editor. (From the Modeling/Rigging/Animation menus, `Deform > Pose Space Deformation > Pose Editor`)

2. Right click in the left pane of the Pose Editor and check the boxes named `Show Advanced/Driver Settings`

3. Right click in the right pane of the Pose Editor and check the box named `Show Advanced Settings`


### Create a Pose

1. Select the joint you want to work with.

2. In the Pose Editor, click `Create Pose Interpolator`. If a warning dialog comes up talking about neutral poses, click Yes to create them.

3. In the `Driver Settings` panel (see The Pose Editor, step 2), change the `Twist Axis` to `Y Axis`. This is because our joint chains are "Y Down" so poseInterpolator nodes see Y rotation as "Twist" and X/Z rotations as "Swing". Forgetting to do this will cause weird problems.

4. Pose the joint by adjusting its control. I find it helpful to set the rotation values to whole numbers.

5. In the Pose Editor, click `Add Pose`. A pose should appear beneath the neutral poses. If it does not, see Note 1 below.

6. It is extremely helpful to rename the pose at this point. I detail my naming convention in Note 2 below.

7. Most poses only change the "Swing" of the joint, but in the case that you are affecting the "Twist", in the Pose Editor change the Type of the pose accordingly.

8. Every poseInterpolator can have multiple poses (i.e. positive X, negative X, positive Z, etc.). Every joint will need to have its own poseInterpolator.



***Note 1***: There is a bug that frequently prevents poses from being created if there is an active blendshape deforming the mesh. To create a pose if this is happening, select the mesh and hold right-click over the geometry. Navigate to `Inputs > All Inputs...` and change the Node State of any blendshapes to `Has No Effect`. At this point you should be able to create the pose. After creating a pose, make sure to set all the blendshapes back to `Normal`.

***Note 2***: To clearly name a pose:

1. Take the name of the pose joint minus JNT ( clavicle_L_JNT -> clavicle_L_ )
2. For every rotation on the control, add r{X, Y, Z}_{rotation value}. Represent negative values with a lowercase 'n'.( if rot X = 20 and rot y = -15, add rX_20_rY_n15)
3. Putting these together, our example pose would be named `clavicle_L_rX_20_rY_n15`


### Editing a Pose

To edit poses we use vertex modeling techniques as weill as the Maya sculpting tools. My favorite sculpt tools are Lift, Pull, Level, and Build Up, but use whatever you need. This process can be extremely crashy if things are done out of order, so try to follow the steps as closely as possible. It will become habit eventually, but I still make mistakes and Maya is unpredictable, so save early and often.

0. Save your work (Maya crashed on me while writing these docs)

1. On the far right side of the Pose Editor, make sure Edit is enabled (red).

2. Deselect the mesh

3. Click your sculpting tool from the shelf.

4. When "Select a polygon mesh" flashes on the screen, click the mesh.

5. Sculpt! At this point, as long as the mesh is active, you should be able to switch tools and keep working. If you have to stop sculpting at any point, repeat steps 1-4 (and 0) again.

6. You can turn any shape off at any point by clicking the little circle button to the left of the pose name. 

7. When you are finished editing, disable Edit for the pose.

8. To mirror a pose, Right Click > Mirror. You can also mirror an entire poseInterpolator.

9. Save!

***Note 3***: In order to see the shape working and not have to keep selecting/deselecting the mesh, it is super helpful to set keyframes on the relevant control at (0, 0, 0) and the pose. This way you can scrub the time slider to check your work and never need to touch the control. This is why a well named pose is nice, when you come back to it, you can quickly set up the keys and get to work.


### Publishing

In order for your work to be integrated into a rig build, you need to export poses and/or poseInterpolators. It is generally easier to work with pose files that contain all your poseInterpolators and poses. 

1. In the Pose Editor, `File > Export All`

2. Navigate to `/groups/dungeons/character/Rigging/Rigs/{character}/Skin` and save the file with the same name as the .mb file you are working in, plus any other info you need (date/version). For example, if my file is named `rayden_skinning_file_jack.mb`, I might save the pose file as `rayden_skinning_file_jack_09-17-24.pose`.

3. Doing this creates two files: a .shp file that stores all the blendshape targets associated with each pose, and a .pose file that contains all the poseInterpolators and information mapping joint orientation to shape targets.

4. Let me know when you have exported poses and tell me the .pose file path/name so I can check your work and integrate it into future builds.



### Troubleshooting

???