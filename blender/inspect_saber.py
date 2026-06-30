import bpy, sys
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.io_scene_kotor')
# clear
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
mdl=r"C:/Users/alex4/AppData/Local/Temp/whereami206/vanilla_saber.mdl"
try:
    bpy.ops.kb.mdlimport(filepath=mdl)
    print("IMPORT_OK")
except Exception as e:
    print("IMPORT_FAIL", repr(e)); raise

def tree():
    for o in bpy.data.objects:
        par=o.parent.name if o.parent else '-'
        info=f"{o.type:8}"
        if o.type=='MESH':
            me=o.data
            xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
            if xs:
                info+=f" verts={len(me.vertices)} bbox z[{min(zs):.3f},{max(zs):.3f}] x[{min(xs):.3f},{max(xs):.3f}]"
            mats=[m.name for m in me.materials]
            info+=f" mats={mats}"
        # kotor props
        kb=getattr(o,'kb',None)
        extra=''
        if kb:
            for attr in ('meshtype','nodetype','bitmap'):
                if hasattr(kb,attr): extra+=f" {attr}={getattr(kb,attr)}"
        print(f"  {o.name:24} parent={par:18} {info}{extra}")
print("=== OBJECT TREE ===")
tree()
print("=== scene loc/scale of root ===")
for o in bpy.data.objects:
    if o.parent is None: print(" ROOT", o.name, "loc",tuple(round(c,3) for c in o.location))
