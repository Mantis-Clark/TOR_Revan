import bpy, math, sys, os

# ---------------- parameters (everything tweakable) ----------------
P = dict(
    body_r       = 0.0175,  # grip radius (m)
    body_len     = 0.150,
    emitter_r    = 0.0215,  # emitter bell radius
    emitter_len  = 0.040,
    neck_r       = 0.0150,
    neck_len     = 0.012,
    pommel_r     = 0.0205,
    pommel_len   = 0.032,
    ring_r       = 0.0195,  # control rings near top of grip
    n_grip_ridges= 7,
    seg          = 64,      # radial resolution
    out          = r"C:/Users/alex4/AppData/Local/Temp/whereami206/render_hilt.png",
)

# ---------------- helpers ----------------
def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for d in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(d): d.remove(b)

def mat(name, color, metallic=1.0, rough=0.35, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1)
        bsdf.inputs["Emission Strength"].default_value = 6.0
    return m

def cyl(r, depth, z, seg, m, name):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=depth, location=(0,0,z))
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(m)
    return o

def torus(major, minor, z, m, name, seg=48):
    bpy.ops.mesh.primitive_torus_add(location=(0,0,z), major_radius=major, minor_radius=minor,
                                     major_segments=seg, minor_segments=16)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(m)
    return o

def cube(sx, sy, sz, loc, m, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = (sx, sy, sz); o.data.materials.append(m)
    return o

def smooth_bevel(o, width=0.0012):
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    b = o.modifiers.new("bev", 'BEVEL'); b.width = width; b.segments = 3; b.limit_method='ANGLE'

# ---------------- build ----------------
clear()
m_metal  = mat("metal",  (0.62,0.64,0.66), 1.0, 0.30)
m_dark   = mat("dark",   (0.045,0.045,0.05), 0.55, 0.55)
m_brass  = mat("brass",  (0.70,0.55,0.22), 1.0, 0.25)
m_accent = mat("accent", (0.85,0.05,0.05), 0.2, 0.4, emit=(1.0,0.05,0.05))

parts = []
# stack from bottom (pommel) to top (emitter) along +Z, centered later
z = 0.0
# pommel
parts.append(cyl(P['pommel_r'], P['pommel_len'], z + P['pommel_len']/2, P['seg'], m_metal, "pommel"))
parts.append(torus(P['pommel_r']*0.96, 0.003, z+0.004, m_dark, "pommel_ring"))
z += P['pommel_len']
# main grip
grip_z0 = z
parts.append(cyl(P['body_r'], P['body_len'], z + P['body_len']/2, P['seg'], m_dark, "grip"))
# grip ridges (metal rings across the dark grip)
for i in range(P['n_grip_ridges']):
    rz = grip_z0 + P['body_len']*(0.18 + 0.64*i/(P['n_grip_ridges']-1))
    parts.append(torus(P['body_r']+0.0005, 0.0016, rz, m_metal, f"ridge{i}"))
z += P['body_len']
# control section: two bright rings + activation button box
parts.append(cyl(P['ring_r'], 0.012, z+0.006, P['seg'], m_metal, "ctrl"))
parts.append(torus(P['ring_r']+0.0008, 0.0022, z+0.006, m_brass, "ctrl_ring"))
# activation button (red) on the side of control section
parts.append(cube(0.006, 0.004, 0.004, (P['ring_r']*0.92, 0, z+0.006), m_accent, "button"))
z += 0.012
# neck
parts.append(cyl(P['neck_r'], P['neck_len'], z + P['neck_len']/2, P['seg'], m_dark, "neck"))
z += P['neck_len']
# emitter bell (slightly conical: use cylinder then scale top loop is complex; use two stacked)
em = cyl(P['emitter_r'], P['emitter_len'], z + P['emitter_len']/2, P['seg'], m_metal, "emitter")
parts.append(em)
parts.append(torus(P['emitter_r']*0.97, 0.0028, z+P['emitter_len']-0.004, m_brass, "emitter_lip"))
# emitter inner (dark recess)
parts.append(cyl(P['emitter_r']*0.6, 0.006, z+P['emitter_len']-0.001, P['seg'], m_dark, "emitter_hole"))
z += P['emitter_len']

total = z
# center the whole hilt on origin in Z
for o in parts:
    o.location.z -= total/2
for o in parts:
    if o.type=='MESH': smooth_bevel(o)

# ---------------- camera + lights + world ----------------
# empty target
bpy.ops.object.empty_add(location=(0,0,0)); tgt = bpy.context.active_object
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 90; cam_data.sensor_width = 36
cam = bpy.data.objects.new("cam", cam_data); bpy.context.collection.objects.link(cam)
cam.location = (0.42, -0.46, 0.07)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
bpy.context.scene.camera = cam

def area_light(name, loc, energy, size=0.4):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy=energy; ld.size=size
    o = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(o); o.location=loc
    cc=o.constraints.new('TRACK_TO'); cc.target=tgt; cc.track_axis='TRACK_NEGATIVE_Z'; cc.up_axis='UP_Y'
    return o
area_light("key",  (0.5,-0.4,0.5), 90)
area_light("fill", (-0.5,-0.3,0.1), 25, size=0.6)
area_light("rim",  (-0.2,0.5,0.4), 70)

# world bg
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.10,0.11,0.13,1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.4

# floor
bpy.ops.mesh.primitive_plane_add(size=4, location=(0,0,-total/2-0.001))
floor = bpy.context.active_object; floor.data.materials.append(mat("floor",(0.18,0.18,0.20),0.0,0.6))

# ---------------- render ----------------
sc = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
    try: sc.render.engine = eng; break
    except: pass
print("ENGINE", sc.render.engine)
try: sc.eevee.taa_render_samples = 64
except: pass
sc.render.resolution_x = 900; sc.render.resolution_y = 1200
sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard'
sc.render.filepath = P['out']
bpy.ops.render.render(write_still=True)
print("WROTE", P['out'], os.path.exists(P['out']))
