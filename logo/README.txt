UPCHUCK — editable Blender logo scene

Created and rendered in Blender 4.3.2 using Cycles (CPU).

Open upchuck.blend. Numpad 0 selects the logo camera; F12 renders.
The output is a 2800 x 850 PNG with a transparent RGBA background.
Set your desired output location in Output Properties before rendering.

Each numbered dice collection contains a named 'Die ... rotate me' empty.
Move/rotate this empty to change the whole die: its body, letter and pips
follow together. Black letters remain editable text. The font is packed.
The ivory bodies have large rounded edges. Each pip is a glossy coloured
dome seated in a physical recess, so a fine shaded groove outlines it.

All six numerical values are assigned once per die. The front numerical
value is replaced with the corresponding letter. Opposite faces sum to 7.
Hidden faces have real pip geometry, so the dice can be rotated freely.
The camera sees a front face, top face and one side per die; the side
(left or right) is chosen per die in DICE and checked by the script.
Dice are kept apart with a rounded-box separation test, so they may sit
closer than their square bounds would suggest but never intersect.

Face assignments (front numeric value replaced by the letter):
Letter   Front  Back  Top  Bottom  Right  Left   Side shown
U        3      4     1    6       5      2      left
P        1      6     2    5       4      3      left
C        1      6     3    4       5      2      right
H        2      5     4    3       6      1      right
U        3      4     5    2       6      1      left
C        3      4     6    1       5      2      left
K        2      5     1    6       4      3      left

The camera is a centred 80mm perspective camera at near eye level, so the
row stays horizontal and the lettered fronts dominate over the tops. The script dollies it and applies lens shift to frame the
dice with transparent padding.

There is no floor or baked ground shadow. Lighting comes from a studio world
(bright overhead, dark toward the horizon) and three area lights. Two strip
lights in the 'Letter shine' set use Cycles light linking to light only the
letters (receiver collection 'Letter shine receivers'): their reflections
run along the letters' rounded edges without brightening the ivory.
A 'Soft under fill' strip below the dice lights only the bodies and pips
(collection 'Under fill receivers'), lifting the undersides without greying
the glossy letters. The Standard view transform is used so the pip
colours stay fully saturated (AgX desaturates them toward pastel). A tone
curve (Color Management > Curves) gives whiter whites and deeper blacks; it
is applied when the PNG is saved and can be edited in the .blend.
Cycles denoising is enabled when the Blender build includes OpenImageDenoise
(256 samples); otherwise 512 samples are rendered without denoising.

Each uppercase letter is scaled to fill a LETTER_SIZE square on the flat
face. It is a high-gloss black emboss standing LETTER_RELIEF proud of the
face, with LETTER_ROUNDING edges: the flat tops mirror the dark studio front
and stay black, while the rounded edges pick up the strip lights.

To rebuild or change the layout numerically, edit DICE and the BEVEL,
PIP_RADIUS, PIP_SPACING, LETTER_SIZE, LETTER_RELIEF and LETTER_ROUNDING constants near the top of
create_upchuck.py, then run:
  blender --background --python create_upchuck.py -- --render
The script writes upchuck.blend and upchuck.png alongside itself, overwriting
those generated outputs. Work from a copy if you want to preserve edits.

For glossy letters in each die's pip colour instead of black, add --coloured.
It writes upchuck_coloured.blend and upchuck_coloured.png instead:
  blender --background --python create_upchuck.py -- --render --coloured

For a faster half-resolution check (writes upchuck_preview.png):
  blender --background --python create_upchuck.py -- --render --preview

Letters use Fredoka Bold, a static weight-700 instance of the Fredoka
variable font (SIL Open Font License; see FREDOKA-LICENSE.txt), generated
with: fonttools varLib.instancer Fredoka[wdth,wght].ttf wght=700 wdth=100
--remove-overlaps. Overlap removal is required: without it Blender renders
holes where the glyph contours overlap (for example in the 'p').
DejaVuSans-Bold.ttf and FONT-LICENSE.txt are no longer used by the script.
