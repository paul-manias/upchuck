"""Build an editable Upchuck logo scene. Blender 4.x; no external add-ons.

Run: blender --background --python create_upchuck.py -- --render
Outputs are written alongside this script. Existing output scene is overwritten.
"""
import bpy
import math
import os
import sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = os.path.dirname(os.path.abspath(__file__))
RENDER = '--render' in sys.argv
PREVIEW = '--preview' in sys.argv
COLOURED = '--coloured' in sys.argv  # Letters take their die's pip colour instead of black.
NAME = 'upchuck_coloured' if COLOURED else 'upchuck'

# Each entry: letter, sRGB pip colour, top/right/front numerical values, the side
# face shown to the camera, position (x,y,z) and local XYZ rotations in degrees.
# X tips the top toward the camera, Y rolls the die in the picture plane and
# Z turns it: negative Z shows the right face, positive Z the left face.
# The front number is replaced by the letter. Opposite faces always sum to seven.
# Each hidden face is also fully modelled.
DICE = [
    ('U', '#f0141e', (1,5,3), 'left',  (-7.05,0.20,0.00), ( 5, -6, 18)),
    ('P', '#0a63f5', (2,4,1), 'left',  (-4.70,0.30,-0.10), ( 7,  6, 18)),
    ('C', '#12a62a', (3,5,1), 'right', (-2.35,0.05,-0.02), ( 4, -5,-18)),
    ('H', '#ff8a00', (4,6,2), 'right', ( 0.00,0.00,0.26), ( 8,  3,-14)),
    ('U', '#f0141e', (5,6,3), 'left',  ( 2.35,0.25,-0.18), ( 6, -6, 18)),
    ('C', '#8f1ee0', (6,5,3), 'left',  ( 4.70,0.05,0.02), ( 8,  4, 16)),
    ('K', '#0a63f5', (1,4,2), 'left',  ( 7.05,0.20,-0.10), ( 5,  8, 20)),
]
BEVEL = .30          # Edge radius of the 2x2x2 body: large for a soft, toy-like feel.
PIP_RADIUS = .17
PIP_SPACING = .44
LETTER_SIZE = 1.20   # Each glyph is scaled to fill this square on the flat face.
LETTER_RELIEF = .034 # How far the letters stand proud of the face.
LETTER_ROUNDING = .026 # Edge radius of the embossed letters; near half the relief
                       # gives a pillowed profile whose edges catch reflections.
PATTERNS = {
    1: [(0,0)],
    2: [(-1,1),(1,-1)],
    3: [(-1,1),(0,0),(1,-1)],
    4: [(-1,-1),(-1,1),(1,-1),(1,1)],
    5: [(-1,-1),(-1,1),(0,0),(1,-1),(1,1)],
    6: [(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)],
}
# Normal, face-horizontal and face-vertical: local cube coordinates.
FACES = {
    'front': ((0,-1,0),(1,0,0),(0,0,1)),
    'back':  ((0,1,0),(-1,0,0),(0,0,1)),
    'right': ((1,0,0),(0,1,0),(0,0,1)),
    'left':  ((-1,0,0),(0,-1,0),(0,0,1)),
    'top':   ((0,0,1),(1,0,0),(0,1,0)),
    'bottom':((0,0,-1),(1,0,0),(0,-1,0)),
}

def linear(v):
    return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4

def material(name, colour, roughness, coat=.22, coat_roughness=.2):
    rgb = tuple(linear(int(colour[i:i+2],16)/255) for i in (1,3,5))
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb,1)
    p.inputs['Roughness'].default_value = roughness
    if 'Coat Weight' in p.inputs:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = coat_roughness
    return m

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def move_collection(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)

def cylinder(name, radius, depth, position, normal, collection):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth,
                                       location=position)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector(normal).to_track_quat('Z','Y')
    move_collection(o,collection)
    return o

def dome(name, radius, height, position, normal, collection):
    # Flattened sphere: a glossy, slightly convex pip that catches a highlight.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius,
                                         location=position)
    o = bpy.context.object
    o.name = name
    o.scale = (1,1,height/radius)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector(normal).to_track_quat('Z','Y')
    for poly in o.data.polygons:
        poly.use_smooth = True
    move_collection(o,collection)
    return o

def point_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
# Denoise only where the build includes OpenImageDenoise, so the script stays portable.
# Without it, extra samples keep the glossy ivory clean.
denoisers = {i.identifier for i in scene.cycles.bl_rna.properties['denoiser'].enum_items}
scene.cycles.use_denoising = 'OPENIMAGEDENOISE' in denoisers
if scene.cycles.use_denoising:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.samples = 64 if PREVIEW else (256 if scene.cycles.use_denoising else 512)
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.resolution_x = 1400
scene.render.resolution_y = 425
scene.render.resolution_percentage = 50 if PREVIEW else 100
scene.render.filepath = os.path.join(OUT,NAME+('_preview.png' if PREVIEW else '.png'))
# Standard keeps the pip colours fully saturated; AgX desaturates them toward pastel.
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
# Display tone curve for a punchy logo: whiter whites and deeper blacks. It is part of
# the view transform, so it is baked into the saved PNG and stays editable in Blender.
scene.view_settings.use_curve_mapping = True
tone = scene.view_settings.curve_mapping
tone.curves[3].points[0].location = (0,0)
tone.curves[3].points[1].location = (1,1)
tone.curves[3].points.new(.18,.07)
tone.curves[3].points.new(.62,.80)
tone.curves[3].points.new(.90,.97)  # Shoulder: lit faces roll off instead of clipping.
tone.update()

ivory = material('Ivory glossy dice', '#fffdf8', .22, coat=.6, coat_roughness=.06)
ivory.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = .08
ivory.node_tree.nodes['Principled BSDF'].inputs['Subsurface Radius'].default_value = (.4,.3,.2)
# High-gloss black: flat tops mirror the dark studio front and stay deep black, while
# the rounded edges mirror the bright overhead world and lights.
ink = material('Glossy black letters', '#040404', .08, coat=1, coat_roughness=.02)
colours = {c:material('Pips '+c,c,.22,coat=.35,coat_roughness=.1) for c in set(d[1] for d in DICE)}
letter_inks = {c:material('Glossy letters '+c,c,.08,coat=1,coat_roughness=.02) for c in colours}
# A weak base specular keeps upward-facing pips from washing out under the top light;
# the clear coat still provides a small glossy highlight.
for m in colours.values():
    m.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = .2

font_path = os.path.join(OUT,'Fredoka-Bold.ttf')
if not os.path.isfile(font_path):
    raise RuntimeError('Place Fredoka-Bold.ttf alongside this script.')
font = bpy.data.fonts.load(font_path)
font.pack()
roots = []
bodies = []
letters = []

for index, (letter, colour, nums, side, position, rotation) in enumerate(DICE,1):
    top,right,front = nums
    values = {'top':top,'bottom':7-top,'right':right,'left':7-right,
              'front':front,'back':7-front}
    assert sorted(values.values()) == [1,2,3,4,5,6]
    coll = bpy.data.collections.new(f'{index:02d} — {letter} die')
    scene.collection.children.link(coll)
    root = bpy.data.objects.new(f'Die {index} {letter} — rotate me',None)
    coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = .5
    root['face_values'] = str(values)
    root['letter_replaces'] = front
    root['top_pips'] = top
    root['right_pips'] = right
    root['shown_side'] = side
    roots.append(root)

    bpy.ops.mesh.primitive_cube_add(size=2)
    body = bpy.context.object
    body.name = f'{letter} — rounded ivory body'
    move_collection(body,coll)
    body.data.materials.append(ivory)
    bevel = body.modifiers.new('Rounded cube edges','BEVEL')
    bevel.width = BEVEL
    bevel.segments = 16
    activate(body)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for poly in body.data.polygons:
        poly.use_smooth = True

    # Each pip sits in a recess slightly wider than itself, so a thin shaded groove
    # outlines a glossy coloured dome whose crown is just below the face.
    cutters = []
    for face,value in values.items():
        if face == 'front':
            continue
        normal,horizontal,vertical = map(Vector,FACES[face])
        for j,(a,b) in enumerate(PATTERNS[value],1):
            offset = horizontal*(a*PIP_SPACING)+vertical*(b*PIP_SPACING)
            cutter = cylinder('Temporary pip recess',PIP_RADIUS+.016,.12,
                              normal*1.0+offset,normal,coll)
            cutters.append(cutter)
            height = .03
            dot = dome(f'{letter} {face} {value} — pip {j}',PIP_RADIUS,height,
                       normal*(.996-height)+offset,normal,coll)
            dot.data.materials.append(colours[colour])
            dot.parent = root
    bpy.ops.object.select_all(action='DESELECT')
    for obj in cutters:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = cutters[0]
    bpy.ops.object.join()
    cutter = bpy.context.object
    boolean = body.modifiers.new('Physical recessed pips','BOOLEAN')
    boolean.operation = 'DIFFERENCE'
    boolean.solver = 'EXACT'
    boolean.object = cutter
    activate(body)
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    normal_mod = body.modifiers.new('Correct face normals','WEIGHTED_NORMAL')
    normal_mod.keep_sharp = True
    if hasattr(body.data,'use_auto_smooth'):
        body.data.use_auto_smooth = True
    body.parent = root
    bodies.append(body)

    curve = bpy.data.curves.new(f'Editable letter {letter}','FONT')
    curve.body = letter
    curve.font = font
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = 1
    curve.bevel_resolution = 4  # Extrude and bevel are set once the glyph scale is known.
    text = bpy.data.objects.new(f'{letter} — editable black letter',curve)
    coll.objects.link(text)
    curve.materials.append(letter_inks[colour] if COLOURED else ink)
    text.rotation_euler = (math.pi/2,0,0)
    text.parent = root
    letters.append(text)

    root.location = position
    root.rotation_euler = tuple(math.radians(a) for a in rotation)

# Each glyph is scaled to fill the flat face and centred by its visible bounds.
bpy.context.view_layer.update()
for text in letters:
    corners = [Vector(c) for c in text.bound_box]
    lo = Vector(tuple(min(c[i] for c in corners) for i in range(3)))
    hi = Vector(tuple(max(c[i] for c in corners) for i in range(3)))
    scale = min(LETTER_SIZE/max(hi.x-lo.x,.01),LETTER_SIZE/max(hi.y-lo.y,.01))
    center = (lo+hi)*.5
    text.scale = (scale,scale,scale)
    text.location.x = -center.x*scale
    text.location.z = -center.y*scale
    # A shallow pillowed emboss, with the back of the letter sunk slightly into the
    # front face (y = -1) so no seam shows. The negative offset keeps the bevel from
    # fattening the glyph outline.
    sink = .006
    text.data.bevel_depth = LETTER_ROUNDING/scale
    text.data.offset = -LETTER_ROUNDING*.5/scale
    text.data.extrude = max((LETTER_RELIEF+sink)/(2*scale)-text.data.bevel_depth,0)
    text.location.y = -1+sink-(LETTER_RELIEF+sink)*.5

# Keep the solid dice from intersecting, even with their different rotations.
# A rounded die is its inner box (half-size 1-BEVEL) grown by a BEVEL-radius sphere,
# so a separating-axis gap above 2*BEVEL between inner boxes guarantees no contact.
# This lets dice nestle together as closely as their rounded corners allow.
def intersects(a,b):
    axes_a = [a.rotation_euler.to_matrix() @ Vector(v) for v in ((1,0,0),(0,1,0),(0,0,1))]
    axes_b = [b.rotation_euler.to_matrix() @ Vector(v) for v in ((1,0,0),(0,1,0),(0,0,1))]
    axes = axes_a+axes_b+[x.cross(y) for x in axes_a for y in axes_b]
    delta = b.location-a.location
    for axis in axes:
        if axis.length < 1e-8:
            continue
        axis.normalize()
        radius = sum(abs(axis.dot(x)) for x in axes_a+axes_b)*(1-BEVEL)
        if abs(axis.dot(delta)) > radius+2*BEVEL+.03:
            return False
    return True

for i,root in enumerate(roots):
    for attempt in range(100):
        if not any(intersects(root,prior) for prior in roots[:i]):
            break
        for later in roots[i:]:
            later.location.x += .04
    else:
        raise RuntimeError('Unable to separate dice')
midpoint = (roots[0].location.x+roots[-1].location.x)*.5
for root in roots:
    root.location.x -= midpoint

studio = bpy.data.collections.new('Studio — camera and softboxes')
scene.collection.children.link(studio)
# A centred, gently raised perspective camera keeps the row horizontal; each die's
# own rotation decides which side face it shows.
aim = Vector((0,0,0))
bpy.ops.object.camera_add(location=(0,-40,5.5))
camera = bpy.context.object
camera.name = 'Logo Camera'
move_collection(camera,studio)
point_at(camera,aim)
camera.data.type = 'PERSP'
camera.data.lens = 80
camera.data.sensor_fit = 'HORIZONTAL'
scene.camera = camera

def area(name, location, power, size, colour=(1,1,1)):
    data = bpy.data.lights.new(name,'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    data.color = colour
    obj = bpy.data.objects.new(name,data)
    studio.objects.link(obj)
    obj.location = location
    point_at(obj,(0,0,0))
    return obj

def strip(name, location, power, width, depth, receivers):
    # Wide softbox lighting only the letters (Cycles light linking): its reflection
    # runs along the letters' rounded edges without brightening the ivory.
    data = bpy.data.lights.new(name,'AREA')
    data.energy = power
    data.shape = 'RECTANGLE'
    data.size = width
    data.size_y = depth
    obj = bpy.data.objects.new(name,data)
    studio.objects.link(obj)
    obj.location = location
    point_at(obj,(0,0,0))
    obj.light_linking.receiver_collection = receivers
    return obj

area('Large warm key',(-7,-11,11),1500,10,(1,.95,.88))
area('Cool front fill',(8,-10,4),420,10,(.9,.95,1))
area('Top rim',(0,5,10),450,12)
shine = bpy.data.collections.new('Letter shine receivers')
for text in letters:
    shine.objects.link(text)
strip('Letter shine — overhead strip',(0,-7,10),5500,34,5,shine)
strip('Letter shine — left strip',(-16,-12,2),3500,3,14,shine)
# Soft bounce from below, as if from a pale tabletop, to open up the undersides.
# It lights the bodies and pips only; on the glossy letters its reflection would
# wash the flat faces grey.
dice_only = bpy.data.collections.new('Under fill receivers')
for root in roots:
    for child in root.children:
        if child not in letters:
            dice_only.objects.link(child)
strip('Soft under fill',(0,-6,-9),650,34,10,dice_only)
# Studio gradient: bright overhead and dark toward the horizon. Glossy surfaces
# facing the camera reflect the dark front; upward-curving edges pick up the light.
world = bpy.data.worlds.new('Soft studio gradient')
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
background = nodes['Background']
background.inputs['Color'].default_value = (.8,.82,.86,1)
coords = nodes.new('ShaderNodeTexCoord')
split = nodes.new('ShaderNodeSeparateXYZ')
ramp = nodes.new('ShaderNodeMapRange')
ramp.inputs['From Min'].default_value = -.05
ramp.inputs['From Max'].default_value = .85
ramp.inputs['To Min'].default_value = .03
ramp.inputs['To Max'].default_value = .75
links.new(coords.outputs['Generated'],split.inputs['Vector'])
links.new(split.outputs['Z'],ramp.inputs['Value'])
links.new(ramp.outputs['Result'],background.inputs['Strength'])
scene.world = world

# Fit the camera to the actual transformed body bounds with transparent padding:
# dolly to set the size, then lens shift to centre the logo in the frame.
aspect = scene.render.resolution_x/scene.render.resolution_y
for attempt in range(6):
    bpy.context.view_layer.update()
    points = [body.matrix_world @ Vector(corner) for body in bodies for corner in body.bound_box]
    projected = [world_to_camera_view(scene,camera,p) for p in points]
    lo_x,hi_x = min(p.x for p in projected),max(p.x for p in projected)
    lo_y,hi_y = min(p.y for p in projected),max(p.y for p in projected)
    fit = max((hi_x-lo_x)/.92,(hi_y-lo_y)/.84)
    camera.location = aim+(camera.location-aim)*fit
    camera.data.shift_x += ((lo_x+hi_x)*.5-.5)*fit
    camera.data.shift_y += ((lo_y+hi_y)*.5-.5)*fit/aspect
bpy.context.view_layer.update()

# Visibility is dictated by geometry: any convex cube has <=3 facing planes.
# Additionally verify this pose reveals the front, top and chosen side of every die.
for root,die in zip(roots,DICE):
    toward = (camera.location-root.matrix_world.translation).normalized()
    visible = [name for name,(n,_,_) in FACES.items()
               if (root.matrix_world.to_3x3() @ Vector(n)).dot(toward) > 1e-5]
    assert len(visible) <= 3, (root.name,visible)
    assert {'front','top',die[3]} <= set(visible), (root.name,visible)
    root['visible_faces_at_logo_camera'] = ', '.join(visible)
    print(root.name, visible)

scene['logo_notes'] = 'Seven editable dice. Front face replaces one pip value with a letter. Opposites sum to seven. Transparent RGBA PNG. Rotate each named die empty.'
scene['wordmark'] = 'Upchuck'
scene['generator'] = 'create_upchuck.py'
readme = bpy.data.texts.new('README — Upchuck scene')
readme.write('Select a Die … rotate me empty to change its pose. All letter and pip geometry follows.\nF12 renders a transparent PNG. Camera view: numpad 0.\nPips are glossy domes in physical recesses. Hidden faces also have valid unique values.\nFront face numerical value is replaced by the letter; opposite faces sum to seven.\nFredoka Bold is packed into this file. No image textures or external dependencies.\n')
activate(roots[0])
for screen in bpy.data.screens:
    for area_ in screen.areas:
        if area_.type == 'VIEW_3D':
            area_.spaces.active.region_3d.view_perspective = 'CAMERA'
            area_.spaces.active.shading.type = 'MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,NAME+'.blend'))
if RENDER:
    bpy.ops.render.render(write_still=True)
