import bpy, math, os
from mathutils import Matrix

OVR = r"C:/Program Files (x86)/Steam/steamapps/common/swkotor/Override"
MODELNAME = "w_lghtsbr_099"
TEX = "w_Vbroswrd_001"
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.io_scene_kotor')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()

# 1) import scaffold (valid weapon root + engine metadata)
bpy.ops.kb.mdlimport(filepath=r"C:/Users/alex4/AppData/Local/Temp/whereami206/vbro.mdl")
root = [o for o in bpy.data.objects if o.parent is None][0]
root.location = (0,0,0); root.rotation_euler=(0,0,0)
# delete its mesh children, keep root
for c in list(root.children):
    bpy.data.objects.remove(c, do_unlink=True)

# 2) build hilt geometry, grip bottom at z=0, emitter toward +Z
seg=24
P=dict(body_r=0.0175,body_len=0.140,emitter_r=0.0230,emitter_len=0.040,
       neck_r=0.0150,neck_len=0.012,pommel_r=0.0205,pommel_len=0.032,ring_r=0.0200,n_ridges=6)
parts=[]
def cyl(r,depth,z,name):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg,radius=r,depth=depth,location=(0,0,z))
    o=bpy.context.active_object;o.name=name;parts.append(o);return o
def cone(r1,r2,depth,z,name):
    bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r1,radius2=r2,depth=depth,location=(0,0,z))
    o=bpy.context.active_object;o.name=name;parts.append(o);return o
def tor(major,minor,z,name,s=20):
    bpy.ops.mesh.primitive_torus_add(location=(0,0,z),major_radius=major,minor_radius=minor,major_segments=s,minor_segments=8)
    o=bpy.context.active_object;o.name=name;parts.append(o);return o
z=0.0
cone(P['pommel_r']*1.05,P['pommel_r'],P['pommel_len'],z+P['pommel_len']/2,"pommel")
z+=P['pommel_len']
g0=z
cyl(P['body_r'],P['body_len'],z+P['body_len']/2,"grip")
for i in range(P['n_ridges']):
    tor(P['body_r']+0.0006,0.0016,g0+P['body_len']*(0.16+0.66*i/(P['n_ridges']-1)),f"ridge{i}")
z+=P['body_len']
cyl(P['ring_r'],0.014,z+0.007,"ctrl")
tor(P['ring_r']+0.0009,0.0022,z+0.012,"ctrlring")
# activation button
bpy.ops.mesh.primitive_cube_add(size=1,location=(P['ring_r']*1.0,0,z+0.007))
b=bpy.context.active_object;b.name="button";b.scale=(0.006,0.005,0.006);parts.append(b)
z+=0.014
cyl(P['neck_r'],P['neck_len'],z+P['neck_len']/2,"neck"); z+=P['neck_len']
cone(P['emitter_r']*0.86,P['emitter_r'],P['emitter_len'],z+P['emitter_len']/2,"emitter")
tor(P['emitter_r']*0.98,0.0028,z+P['emitter_len']-0.004,"emitterlip")
z+=P['emitter_len']
H=z
print("HILT_HEIGHT", round(H,3))

# 3) join all parts into one mesh
for o in bpy.data.objects: o.select_set(False)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
hilt=bpy.context.active_object
hilt.name="saberhilt"
hilt.rotation_mode='QUATERNION'
# apply transforms so geometry is clean
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 4) material + kotor texture
mat=bpy.data.materials.new("hiltmat"); mat.use_nodes=True
bsdf=mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value=(0.6,0.62,0.64,1); bsdf.inputs["Metallic"].default_value=1.0; bsdf.inputs["Roughness"].default_value=0.35
hilt.data.materials.clear(); hilt.data.materials.append(mat)
# kotor mesh props
kb=hilt.kb
try: kb.meshtype='TRIMESH'
except: pass
for attr,val in [('bitmap',TEX),('bitmap2',''),('diffuse',(1,1,1)),('ambient',(1,1,1)),('render',True),('shadow',True)]:
    if hasattr(kb,attr):
        try: setattr(kb,attr,val)
        except: pass

# 5) parent to scaffold root, rename root to model name
hilt.parent=root
hilt.matrix_parent_inverse=root.matrix_world.inverted()
root.name=MODELNAME
# kotor root props: set modelname if present
rkb=root.kb
for attr in ('classification',):
    pass

# 6) export
for o in bpy.data.objects: o.select_set(False)
root.select_set(True)
for c in root.children: c.select_set(True)
bpy.context.view_layer.objects.active=root
out=os.path.join(OVR, MODELNAME+".mdl")
try:
    bpy.ops.kb.mdlexport(filepath=out)
    print("EXPORT_OK")
except Exception as e:
    print("EXPORT_FAIL", repr(e)); raise
print("MDL exists:", os.path.exists(out), "MDX exists:", os.path.exists(out[:-4]+".mdx"))
print("sizes:", os.path.getsize(out) if os.path.exists(out) else 0, os.path.getsize(out[:-4]+'.mdx') if os.path.exists(out[:-4]+'.mdx') else 0)
