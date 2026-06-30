import bpy, os
OVR = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II/Override"
MODELNAME = "w_lghtsbr_088"
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.io_scene_kotor')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()

# import the real animated TSL saber (blade + ignition anims)
bpy.ops.kb.mdlimport(filepath=r"C:/Users/alex4/AppData/Local/Temp/whereami206/tsl_saber.mdl")
root = next(o for o in bpy.data.objects if o.parent is None)
lshandle = bpy.data.objects["lshandle01"]
# target footprint = vanilla hilt local bbox
zs=[v.co.z for v in lshandle.data.vertices]; xs=[v.co.x for v in lshandle.data.vertices]
tz0,tz1=min(zs),max(zs); trad=max(max(abs(x) for x in xs), 1e-4)
print("VANILLA hilt z[%.3f,%.3f] rad~%.4f"%(tz0,tz1,trad))
KEEP_BITMAP = getattr(lshandle.kb,'bitmap','')
print("VANILLA hilt bitmap:", KEEP_BITMAP)

# ---- build my hilt parts (local, will be transformed to fit) ----
seg=24; parts=[]
P=dict(body_r=0.0175,body_len=0.140,emitter_r=0.0230,emitter_len=0.040,
       neck_r=0.0150,neck_len=0.012,pommel_r=0.0205,pommel_len=0.032,ring_r=0.0200,n_ridges=6)
def cyl(r,d,z,n):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg,radius=r,depth=d,location=(0,0,z));o=bpy.context.active_object;o.name=n;parts.append(o)
def cone(r1,r2,d,z,n):
    bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r1,radius2=r2,depth=d,location=(0,0,z));o=bpy.context.active_object;o.name=n;parts.append(o)
def tor(maj,mi,z,n,s=20):
    bpy.ops.mesh.primitive_torus_add(location=(0,0,z),major_radius=maj,minor_radius=mi,major_segments=s,minor_segments=8);o=bpy.context.active_object;o.name=n;parts.append(o)
z=0.0
cone(P['pommel_r']*1.05,P['pommel_r'],P['pommel_len'],z+P['pommel_len']/2,"p");z+=P['pommel_len']
g0=z; cyl(P['body_r'],P['body_len'],z+P['body_len']/2,"g")
for i in range(P['n_ridges']): tor(P['body_r']+0.0006,0.0016,g0+P['body_len']*(0.16+0.66*i/(P['n_ridges']-1)),"r%d"%i)
z+=P['body_len']
cyl(P['ring_r'],0.014,z+0.007,"c"); tor(P['ring_r']+0.0009,0.0022,z+0.012,"cr")
bpy.ops.mesh.primitive_cube_add(size=1,location=(P['ring_r'],0,z+0.007));b=bpy.context.active_object;b.name="btn";b.scale=(0.006,0.005,0.006);parts.append(b)
z+=0.014
cyl(P['neck_r'],P['neck_len'],z+P['neck_len']/2,"n");z+=P['neck_len']
cone(P['emitter_r']*0.86,P['emitter_r'],P['emitter_len'],z+P['emitter_len']/2,"e")
tor(P['emitter_r']*0.98,0.0028,z+P['emitter_len']-0.004,"el"); z+=P['emitter_len']

for o in bpy.data.objects: o.select_set(False)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
newhilt=bpy.context.active_object; newhilt.rotation_mode='QUATERNION'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

# fit newhilt into vanilla hilt's local z-range (uniform scale, emitter -> +Z top)
nzs=[v.co.z for v in newhilt.data.vertices]; nz0,nz1=min(nzs),max(nzs)
s=(tz1-tz0)/(nz1-nz0)
newhilt.scale=(s,s,s); bpy.ops.object.transform_apply(scale=True)
nzs=[v.co.z for v in newhilt.data.vertices]; nz0=min(nzs)
newhilt.location.z = tz0 - nz0
bpy.ops.object.transform_apply(location=True)
print("NEWHILT fitted z[%.3f,%.3f]"%(min(v.co.z for v in newhilt.data.vertices),max(v.co.z for v in newhilt.data.vertices)))

# swap geometry into lshandle01 (keeps its kb props, texture, transform, children=blade, anims)
new_mesh = newhilt.data
bpy.data.objects.remove(newhilt, do_unlink=True)
old_mesh = lshandle.data
lshandle.data = new_mesh
bpy.data.meshes.remove(old_mesh)
# preserve the hilt texture (kb.bitmap) that the swap may have dropped
if KEEP_BITMAP:
    lshandle.kb.bitmap = KEEP_BITMAP
print("kb.bitmap kept:", getattr(lshandle.kb,'bitmap',''))
print("hilt verts now:", len(lshandle.data.vertices))

# rename root and export over variation 088
root.name = MODELNAME
def sel_all(o):
    o.select_set(True)
    o.rotation_mode='QUATERNION'   # exporter needs quaternion rotation mode
    for c in o.children: sel_all(c)
for o in bpy.data.objects: o.select_set(False)
sel_all(root)
bpy.context.view_layer.objects.active=root
out=os.path.join(OVR, MODELNAME+".mdl")
try:
    bpy.ops.kb.mdlexport(filepath=out)
    print("EXPORT_OK", os.path.getsize(out), os.path.getsize(out[:-4]+'.mdx'))
except Exception as e:
    print("EXPORT_FAIL", repr(e)); raise
