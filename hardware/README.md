# WEB-1 hardware model (Blender)

`web1.blend` is the CAD-accurate Blender model of the physical WEB-1 (Blender 5.3, millimetres, +Y = back, Z = up).
Every printed part (names containing `(Pxx)`) is a closed, manifold solid ready to export as STL.
Hardware parts are named with their `(Hxx)` id from the parts list in `../web1-3d.html`.

`blender-scripts/` holds the parametric build. To rebuild, open the scripts as text blocks and run, with
`web1_lib.py` executed first in the same namespace each time:

1. `web1_build_1_case.py` … `web1_build_6_pcb.py`
2. `web1_build_7_printed.py` (about 60 s)
3. `web1_build_8_cables.py`

`web1_check.py` reports every pair of solids that intersect; `web1_depth.py` measures how deep.

Design summary: 345 × 129 × 21.3 mm, about 1.14 kg with the centre of mass within 4 mm of the middle.
CM5 + on-board RP2040, WM8960 codec (line in, line/phones out, built-in mic, speaker), five 2000 mAh LiPo cells
in parallel (37 Wh, about 6 h) with a BQ25895 charger, USB-C data/charging, ON/OFF slide switch on the right side,
1.2 mm steel plate and a 4 mm steel plate at the back, Poron and PE foam, 3 mm walls and a 2 mm floor with a
cooling grille under the CM5. Keycaps are single solids: flat underside with the stem socket printed on.

`renders/` has the latest renders.

`pi/` has the software that runs on the device: `hw.html` (shows WEB-1's screen on the panel and links the
key and knob controller) and `web1-helper.py` (serves the app, and handles the battery, clock, USB stick, line in,
updates and power off). Setup is in the Software tab of `../web1-3d.html`.
