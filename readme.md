# rjg

This is an in-progress, modular auto-rigger being used in the BYU Class of 2025 animation capstone.

## Todo
Overall
- Look for ways to optimize everything!

Controls
- Add more sophisticated control shapes throughout the rig. Circles, squares, and cubes aren't very visually descriptive, especially when that's all there are. **in progress**

Hands
- Hand and finger attributes (fist, cup, spread, individual finger curl). Add a 2D control to drive SDKs on fist/cup/spread. **in progress**

Head
- Create a script to connect head to body

Skin
- Something more sophisticated than what is already in place? Think about this...

UI (low priority)
- Select model and guides files from file browser.
- Pass guide names in here instead of the script.
- Select/deselect which components to place/replace.
- Save/load control color scheme (dict to and from json)
- Picker (Diego)

Notes from anim
- <s>Combine ballRoll and heelRoll attrs, keep toes flat on roll forward</s>
- <s>Hide max roll from animators</s>
- Fix axis of rotation on feet (guides)
- Fix axis of rotation on wrists (guides)
- <s>Make COG control more conspicuous, find a better shape to grab</s>
- <s>Hip2</s> and Shoulder2 should not be in secondary group
- <s>Hide visibility control in graph editor</s>
- <s>SS head to COG</s>
- Check trap volume with modeling (model)
- heelRoll and toeRoll need to completely touch the ground. (guides)

Bigger notes from anim
- FK spine controls
- Improved neck control
- Mirror keys script (Alex)


### License

Licensed under the [GNU GPL v3.0](COPYING).