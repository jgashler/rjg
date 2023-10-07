# rjg

This is an in-progress, modular auto-rigger.

## Todo
Overall
- Connect all components! Once this is done, the rig will be a rig.
- Look for ways to optimize everything!

Controls
- Add more sophisticated control shapes throughout the rig. Circles, squares, and cubes aren't very visually descriptive, especially when that's all there are. 
- Add color to all controls. The functionality is there, just need a way to send a color argument from the build script all the way down to the curve drawing function. This should help with rig readability.
- Figure out how to tag all control curves as controls. (Rigging > Control > Tag as Controller)

Hands
- Add metacarpal joint creator to finger part. Handle case when they are given in the guides and when they are not (Mixamo)
- Add IK capability for chains longer than three joints. This kinda works right now but it would be nice to have for IK fingers (4-5 joint chain)
- Hand and finger attributes (fist, cup, spread, individual finger curl). Add a 2D control to drive SDKs on fist/cup/spread.

Head
- Add jaw part (extension of head or separate part?)
- Add eye part
- Add mouth part (integrate sealing mouth script into this one)
- Face! Probably place locators at key vertices (cheek matrix, nose, nostril, chin, eyebrows 2*[1:n], eye corners, forehead, etc), then either set up a bone based face determined by locators or figure out a reliable way to script foundational blend shapes into the face.

Skin
- Set up a basic auto skinning class. Literally just bind to nearby joints.
- Set up a way to save and retrieve skin weights files easily.
- Something more sophisticated? Think about this...

UI
- Select model and guides files from file browser.
- Pass guide names in here instead of the script.
- Select/deselect which components to place/replace.
- Save/load control color scheme (dict to and from json)
- Picker


### License

Licensed under the [GNU GPL v3.0](COPYING).