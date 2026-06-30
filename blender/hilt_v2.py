import bpy, math, sys, os
from mathutils import Matrix, Vector

P = dict(
    body_r=0.0175, body_len=0.140,
    emitter_r=0.0230, emitter_len=0.042,
    neck_r=0.0150, neck_len=0.012,
    pommel_r=0.0205, pommel_len=0.034,
    ring_r=0.0200, n_grip_ridges=6, seg=64,
    tilt_deg=12.0,
    out=r"C:/Users/alex4/AppData/Local/Temp/whereami206/render_hilt_v2.png",
)

def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for d in (bpy.data.meshes,bpy.data.materials,bpy.data.lights,bpy.data.cameras,bpy.data.objects):
        for b in list(d):
            try: d.remove(b)
            except: pass

def mat(name,color,metallic=1.0,rough=0.35,emit=None):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*color,1)
    b.inputs["Metallic"].default_value=metallic
    b.inputs["Roughness"].default_value=rough
    if emit is not None:
        b.inputs["Emission Color"].default_value=(*emit,1)
        b.inputs["Emission Strength"].default_value=8.0
    return m

def cyl(r,depth,z,seg,m,name):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg,radius=r,depth=depth,location=(0,0,z))
    o=bpy.context.active_object; o.name=name; o.data.materials.append(m); return o
def cone(r1,r2,depth,z,seg,m,name):
    bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r1,radius2=r2,depth=depth,location=(0,0,z))
    o=bpy.context.active_object; o.name=name; o.data.materials.append(m); return o
def torus(major,minor,z,m,name,seg=48):
    bpy.ops.mesh.primitive_torus_add(location=(0,0,z),major_radius=major,minor_radius=minor,
                                     major_segments=seg,minor_segments=16)
    o=bpy.context.active_object; o.name=name; o.data.materials.append(m); return o
def cube(sx,sy,sz,loc,m,name):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.active_object; o.name=name; o.scale=(sx,sy,sz); o.data.materials.append(m); return o
def finish(o,width=0.0012):
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    b=o.modifiers.new("bev",'BEVEL'); b.width=width; b.segments=3; b.limit_method='ANGLE'

clear()
m_metal =mat("metal",(0.62,0.64,0.66),1.0,0.28)
m_dark  =mat("dark",(0.018,0.018,0.022),0.10,0.62)     # dielectric black -> stays dark
m_brass =mat("brass",(0.72,0.54,0.18),1.0,0.22)
m_accent=mat("accent",(0.85,0.04,0.04),0.2,0.4,emit=(1.0,0.04,0.04))

parts=[]; z=0.0
# pommel (slightly flared cone) + belt ring
parts.append(cone(P['pommel_r']*1.05,P['pommel_r'],P['pommel_len'],z+P['pommel_len']/2,P['seg'],m_metal,"pommel"))
parts.append(torus(P['pommel_r']*0.94,0.0032,z+0.005,m_dark,"pommel_knurl"))
# belt ring (D-ring) sticking out on -Y side near pommel
br=torus(0.007,0.0022,z+P['pommel_len']*0.7,m_metal,"beltring",seg=32)
br.location.y-=P['pommel_r']; br.rotation_euler=(math.radians(90),0,0)
parts.append(br)
z+=P['pommel_len']
# grip (dark) with metal ridges
g0=z
parts.append(cyl(P['body_r'],P['body_len'],z+P['body_len']/2,P['seg'],m_dark,"grip"))
for i in range(P['n_grip_ridges']):
    rz=g0+P['body_len']*(0.16+0.66*i/(P['n_grip_ridges']-1))
    parts.append(torus(P['body_r']+0.0006,0.0017,rz,m_metal,f"ridge{i}"))
# brass band at top of grip
parts.append(torus(P['body_r']+0.0010,0.0024,g0+P['body_len']*0.95,m_brass,"gband"))
z+=P['body_len']
# control section
parts.append(cyl(P['ring_r'],0.014,z+0.007,P['seg'],m_metal,"ctrl"))
parts.append(torus(P['ring_r']+0.0009,0.0024,z+0.012,m_brass,"ctrl_ring"))
# activation button: housing (dark) + red button, turned to face camera (cam at +X,-Y)
ang=math.atan2(-0.46,0.40)   # camera azimuth
bx,by=math.cos(ang),math.sin(ang)
hou=cube(0.010,0.008,0.012,(bx*P['ring_r']*0.85,by*P['ring_r']*0.85,z+0.007),m_dark,"btn_house")
hou.rotation_euler=(0,0,ang)
parts.append(hou)
btn=cube(0.007,0.005,0.006,(bx*P['ring_r']*1.05,by*P['ring_r']*1.05,z+0.009),m_accent,"button")
btn.rotation_euler=(0,0,ang)
parts.append(btn)
z+=0.014
# neck
parts.append(cyl(P['neck_r'],P['neck_len'],z+P['neck_len']/2,P['seg'],m_dark,"neck"))
z+=P['neck_len']
# emitter: flared cone shroud + lip + dark recess
parts.append(cone(P['emitter_r']*0.86,P['emitter_r'],P['emitter_len'],z+P['emitter_len']/2,P['seg'],m_metal,"emitter"))
parts.append(torus(P['emitter_r']*0.98,0.0030,z+P['emitter_len']-0.004,m_brass,"emitter_lip"))
parts.append(cyl(P['emitter_r']*0.58,0.008,z+P['emitter_len']-0.001,P['seg'],m_dark,"emitter_hole"))
z+=P['emitter_len']

total=z
for o in parts: o.location.z-=total/2
for o in parts:
    if o.type=='MESH': finish(o)

# parent to root empty and tilt
bpy.ops.object.empty_add(location=(0,0,0)); root=bpy.context.active_object
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)
root.rotation_euler=(0,math.radians(P['tilt_deg']),0)

# target/camera
bpy.ops.object.empty_add(location=(0,0,0)); tgt=bpy.context.active_object
cd=bpy.data.cameras.new("cam"); cd.lens=95; cd.sensor_width=36
cam=bpy.data.objects.new("cam",cd); bpy.context.collection.objects.link(cam)
cam.location=(0.40,-0.46,0.09)
cam.constraints.new('TRACK_TO').target=tgt
cam.constraints[0].track_axis='TRACK_NEGATIVE_Z'; cam.constraints[0].up_axis='UP_Y'
bpy.context.scene.camera=cam

def light(name,loc,energy,size=0.4):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.size=size
    o=bpy.data.objects.new(name,ld); bpy.context.collection.objects.link(o); o.location=loc
    cc=o.constraints.new('TRACK_TO'); cc.target=tgt; cc.track_axis='TRACK_NEGATIVE_Z'; cc.up_axis='UP_Y'
light("key",(0.5,-0.4,0.5),85); light("fill",(-0.55,-0.25,0.05),18,0.7); light("rim",(-0.15,0.55,0.45),80)

w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.08,0.09,0.11,1)
w.node_tree.nodes["Background"].inputs[1].default_value=0.25
bpy.ops.mesh.primitive_plane_add(size=4,location=(0,0,-total/2-0.001))
bpy.context.active_object.data.materials.append(mat("floor",(0.07,0.07,0.085),0.0,0.7))

sc=bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
    try: sc.render.engine=eng; break
    except: pass
try: sc.eevee.taa_render_samples=96
except: pass
sc.render.resolution_x=900; sc.render.resolution_y=1200
sc.view_settings.view_transform='Standard'
sc.render.filepath=P['out']
bpy.ops.render.render(write_still=True)
print("WROTE",P['out'],os.path.exists(P['out']))
