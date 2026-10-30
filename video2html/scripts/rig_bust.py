# Prepare an image-to-3D bust (head and shoulders) for the web and rig it so the head can turn (Blender, headless).
#
#   blender -b -P rig_bust.py -- <in.glb> <emissive.png | -> <out.glb> [--rotate -90] [--tris 120000] [--arms]
#
# What it does:
#  1. orientation: rotates the mesh data by --rotate degrees around the vertical axis so the front faces +Z in glTF
#     (render first with render_views.py to know the angle; Tripo models usually need -90);
#  2. size: 2 units tall, base at z = 0, centered;
#  3. fewer triangles (--tris);
#  4. finds the neck: the narrowest horizontal slice between 35% and 80% of the height;
#  5. bones bust → neck → head;
#  6. weights: the head is an ellipsoid fitted to it with a soft edge, plus a slanted boundary in front of the neck, so
#     the chin goes with the head; the shoulders stay with the bust;
#  7. --arms: for a character with arms hanging at its sides, the loose parts that sit far to the side and below the
#     neck become two rigid arms (bones arm_l and arm_r, children of the bust, pivoting at the shoulder);
#  8. plugs the emissive texture into the material's emission (pass "-" to skip) and exports with WebP textures.
# Check the result with: blender -b -P render_views.py -- <out.glb> <prefix> --pose
import argparse
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

ap = argparse.ArgumentParser()
ap.add_argument('glb_in')
ap.add_argument('emissive')
ap.add_argument('glb_out')
ap.add_argument('--rotate', type=float, default=0)
ap.add_argument('--tris', type=int, default=120_000)
ap.add_argument('--arms', action='store_true')
ap.add_argument('--arm-side', type=float, default=0.36, help='min distance to the side (height = 2 units) for a part to be an arm; lower it if pieces of the arm stay behind, raise it if pieces of the body go with the arm')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a.glb_in)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if len(meshes) > 1:  # join everything into one mesh
    bpy.context.view_layer.objects.active = meshes[0]
    for o in bpy.context.scene.objects:
        o.select_set(o in meshes)
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active or meshes[0]
bpy.context.view_layer.objects.active = obj
for o in bpy.context.scene.objects:
    o.select_set(o == obj)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# rotate the mesh data, not the object: the glTF importer uses quaternions, so rotation_euler would be ignored
obj.data.transform(Matrix.Rotation(math.radians(a.rotate), 4, 'Z'))
for o in list(bpy.context.scene.objects):
    if o != obj:
        bpy.data.objects.remove(o, do_unlink=True)

# size: 2 units tall, base at z = 0, centered in x/y
co = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = co.min(0), co.max(0)
k = 2.0 / (mx[2] - mn[2])
cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
obj.data.transform(Matrix.Translation((-cx * k, -cy * k, -mn[2] * k)) @ Matrix.Scale(k, 4))
obj.data.update()

tris0 = sum(len(p.vertices) - 2 for p in obj.data.polygons)
if tris0 > a.tris:
    m = obj.modifiers.new('decimate', 'DECIMATE')
    m.ratio = a.tris / tris0
    bpy.ops.object.modifier_apply(modifier='decimate')
print(f'triangles: {tris0} -> {sum(len(p.vertices) - 2 for p in obj.data.polygons)}')

# the neck: the narrowest slice between 35% and 80% of the height (width measured near the central axis)
co = np.array([v.co[:] for v in obj.data.vertices])
zs = np.linspace(0.7, 1.6, 60)
widths = []
for z in zs:
    s = co[np.abs(co[:, 2] - z) < 0.015]
    widths.append(np.percentile(np.hypot(s[:, 0], s[:, 1]), 92) if len(s) > 20 else 9)
i = int(np.argmin(widths))
z_neck, r_neck = float(zs[i]), float(widths[i])
s = co[np.abs(co[:, 2] - z_neck) < 0.02]
ex, ey = float(s[:, 0].mean()), float(s[:, 1].mean())
z0, z1 = z_neck - 0.12, z_neck + 0.10  # the neck zone (transition)
z_top = float(co[:, 2].max())
print(f'neck at z={z_neck:.3f} (radius {r_neck:.3f}) · axis ({ex:.3f}, {ey:.3f})')


def smooth(lo, hi, x):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


arm = bpy.data.armatures.new('rig')
rig = bpy.data.objects.new('rig', arm)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
b_bust = arm.edit_bones.new('bust')
b_bust.head, b_bust.tail = (ex, ey, 0.25), (ex, ey, z0)
b_neck = arm.edit_bones.new('neck')
b_neck.head, b_neck.tail, b_neck.parent = (ex, ey, z0), (ex, ey, z1), b_bust
b_head = arm.edit_bones.new('head')
b_head.head, b_head.tail, b_head.parent = (ex, ey, z1), (ex, ey, z_top), b_neck

# arms: loose parts far to the side and below the neck (image-to-3D meshes come in many loose pieces)
arm_idx = {}
if a.arms:
    import bmesh
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table()
    parent = np.arange(len(bm.verts))
    def find(i):
        r = i
        while parent[r] != r:
            r = parent[r]
        while parent[i] != r:
            parent[i], i = r, parent[i]
        return r
    for e in bm.edges:
        ra, rb = find(e.verts[0].index), find(e.verts[1].index)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(len(bm.verts))])
    bm.free()
    for side, sign in (('arm_l', 1), ('arm_r', -1)):   # glTF: the character faces +Z, so its left is +X (Blender +X too)
        sel = np.zeros(len(co), bool)
        for r in np.unique(roots):
            m = roots == r
            c = co[m].mean(0)
            side_d = sign * (co[m][:, 0] - ex)
            # an arm piece sits far to the side as a whole: a body panel that only reaches out (e.g. a back plate behind
            # the shoulder) has a good part of itself near the center and must stay with the body
            if sign * (c[0] - ex) > a.arm_side and c[2] < z_neck and np.percentile(side_d, 10) > a.arm_side - 0.04:
                if os.environ.get('RIG_DEBUG'):
                    print(f'  {side} part {m.sum():6d}v  side p10 {np.percentile(side_d, 10):.2f} c {sign * (c[0] - ex):.2f}  '
                          f'y {co[m][:, 1].min():.2f}..{co[m][:, 1].max():.2f}  z {co[m][:, 2].min():.2f}..{co[m][:, 2].max():.2f}')
                sel |= m
        if sel.sum() < 50:
            print(f'{side}: no arm found'); continue
        pts = co[sel]
        # the pivot is the shoulder joint on the body: the outermost body points on that side, next to the top 30% of the
        # arm (a joint disc or socket). Pivoting at the top of the arm itself (often a cap curving over the joint) makes
        # the arm come loose when it rises. Fallback: the center of the arm between 80% and 92% of its height.
        lo, hi = pts[:, 2].min(), pts[:, 2].max()
        body = co[~sel]
        zone = body[(sign * (body[:, 0] - ex) > 0.2) & (body[:, 2] > lo + 0.7 * (hi - lo)) & (body[:, 2] < hi)]
        if len(zone) > 30:
            edge = zone[sign * zone[:, 0] > np.percentile(sign * zone[:, 0], 90)]
            sx, sy, sz = (float(v) for v in edge.mean(0))
        else:
            band = pts[(pts[:, 2] > lo + 0.80 * (hi - lo)) & (pts[:, 2] < lo + 0.92 * (hi - lo))]
            sx, sy, sz = (float(v) for v in band.mean(0))
        b = arm.edit_bones.new(side)
        b.head, b.tail, b.parent = (sx, sy, sz), (float(pts[:, 0].mean()), sy, float(pts[:, 2].min())), b_bust
        arm_idx[side] = np.nonzero(sel)[0]
        print(f'{side}: {sel.sum()} vertices, shoulder at ({sx:.2f}, {sy:.2f}, {sz:.2f})')
bpy.ops.object.mode_set(mode='OBJECT')

# weights: an ellipsoid fitted to the head (neck to top) with a soft edge; the boundary in front of the neck slants
# down so the chin follows the head; points far to the side at shoulder height stay with the bust
head_pts = co[co[:, 2] > z_neck + 0.15]
hx, hy = (head_pts[:, 0].min() + head_pts[:, 0].max()) / 2, (head_pts[:, 1].min() + head_pts[:, 1].max()) / 2
ax, ay = (head_pts[:, 0].max() - head_pts[:, 0].min()) / 2, (head_pts[:, 1].max() - head_pts[:, 1].min()) / 2
hz, az = (z_top + z_neck) / 2, (z_top - z_neck) / 2
d = np.sqrt(((co[:, 0] - hx) / ax) ** 2 + ((co[:, 1] - hy) / ay) ** 2 + ((co[:, 2] - hz) / az) ** 2)
z = co[:, 2]
lateral = np.abs(co[:, 0] - ex)
h = z + 0.35 * np.clip(ey - co[:, 1], 0, None) * smooth(0.75, 0.9, z)
shoulder = np.where(z < z1 + 0.08, 1 - smooth(r_neck * 1.1, r_neck * 1.8, lateral), 1.0)
w_head = np.maximum(1 - smooth(1.0, 1.22, d), smooth(z_neck - 0.02, z_neck + 0.1, h) * shoulder)
w_neck = smooth(z0, z_neck, h) * shoulder * (1 - w_head)
w_bust = np.clip(1 - w_head - w_neck, 0, 1)
for side, idx in arm_idx.items():   # the arms are rigid: all their weight goes to their bone
    w_head[idx] = 0; w_neck[idx] = 0; w_bust[idx] = 0
groups = {n: obj.vertex_groups.new(name=n) for n in ('bust', 'neck', 'head')}
for idx in range(len(co)):
    for n, w in (('bust', w_bust[idx]), ('neck', w_neck[idx]), ('head', w_head[idx])):
        if w > 0.001:
            groups[n].add([idx], float(w), 'REPLACE')
for side, idx in arm_idx.items():
    obj.vertex_groups.new(name=side).add([int(i) for i in idx], 1.0, 'REPLACE')
obj.parent = rig
obj.modifiers.new('rig', 'ARMATURE').object = rig

# material: emissive texture into the emission; smaller textures
mat = obj.data.materials[0]
bsdf = mat.node_tree.nodes.get('Principled BSDF')
if a.emissive != '-' and bsdf:
    img = bpy.data.images.load(a.emissive)
    img.scale(1024, 1024)
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 1.0
for im in bpy.data.images:
    if im.size[0] > 2048:
        im.scale(2048, 2048)
obj.name = 'character'

opts = dict(filepath=a.glb_out, export_format='GLB', export_skins=True, export_animations=False, export_yup=True)
try:
    bpy.ops.export_scene.gltf(**opts, export_image_format='WEBP')
except TypeError:
    bpy.ops.export_scene.gltf(**opts, export_image_format='JPEG')
print('OK', a.glb_out)
