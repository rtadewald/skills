# Render a GLB from fixed views with the same camera and light (Blender, headless), to compare models with the image.
#
#   blender -b -P render_views.py -- <model.glb> <out_prefix> [--yaw -35] [--rotate 90] [--pose]
#
# Writes <out_prefix>-front.png, -side.png, -back.png and, with --yaw, -yaw.png: the view at that angle (degrees), to
# match the character's angle in the image (if it turns the wrong way, flip the sign).
# --rotate: turns the MODEL by these degrees around the vertical axis (same meaning as in rig_bust.py), for models whose
#           front is on another axis. Render once without it; if "front" shows a side or the back, try -90, 90 or 180.
# --pose: for a rigged model (bones "neck" and "head", or "pescoco" and "cabeca"): renders the head turned left, right
#         and down, front and side views, to check the weights (the face must not smear, the shoulders must not move).
import argparse
import math
import sys

import bpy
from mathutils import Matrix, Vector

ap = argparse.ArgumentParser()
ap.add_argument('glb')
ap.add_argument('prefix')
ap.add_argument('--yaw', type=float)
ap.add_argument('--rotate', type=float, default=0)
ap.add_argument('--pose', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a.glb)
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
center, size = (lo + hi) / 2, max(hi - lo)

for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        pass
scene.render.resolution_x = scene.render.resolution_y = 640
world = bpy.data.worlds.new('w')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.32, 0.33, 0.36, 1)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.type = 'ORTHO'
cam.data.ortho_scale = size * 1.15
for name, pos, power in (('key', (1.5, -2, 2), 4), ('fill', (-2, -1, 0.5), 1.5), ('rim', (0, 2.5, 1.5), 3)):
    light = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN'))
    light.data.energy = power
    scene.collection.objects.link(light)
    light.location = center + Vector(pos) * size
    light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()


def shoot(direction: Vector, path: str) -> None:
    cam.location = center + direction * size * 3
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# glTF front (+Z) is -Y in Blender; turning the model by +a is the same as turning the camera by -a
R = Matrix.Rotation(math.radians(-a.rotate), 3, 'Z')
front, side = R @ Vector((0, -1, 0)), R @ Vector((1, 0, 0))

if a.pose:
    rig = next((o for o in scene.objects if o.type == 'ARMATURE'), None)
    if rig is None:
        sys.exit('no armature in the model')
    bones = rig.pose.bones
    head = bones.get('head') or bones.get('cabeca')
    neck = bones.get('neck') or bones.get('pescoco')
    for name, (pitch, yaw) in {'neutral': (0, 0), 'left': (0, 35), 'right': (0, -35), 'down': (15, 0)}.items():
        for b in bones:
            b.rotation_mode = 'XYZ'
            b.rotation_euler = (0, 0, 0)
        # the bone points up: rotating around its Y axis turns the head sideways, around X tilts it
        head.rotation_euler = (math.radians(pitch) * 0.65, math.radians(yaw) * 0.65, 0)
        neck.rotation_euler = (math.radians(pitch) * 0.35, math.radians(yaw) * 0.35, 0)
        if name == 'left' and bones.get('arm_l'):   # raise the left arm sideways (check the arm moves alone)
            bones['arm_l'].rotation_euler = (0, 0, math.radians(70))
        if name == 'right' and bones.get('arm_r'):
            bones['arm_r'].rotation_euler = (0, 0, math.radians(-70))
        bpy.context.view_layer.update()
        shoot(front, f'{a.prefix}-{name}-front.png')
        shoot(side, f'{a.prefix}-{name}-side.png')
else:
    for view, d in (('front', front), ('side', side), ('back', -front)):
        shoot(d, f'{a.prefix}-{view}.png')
    if a.yaw is not None:
        shoot(Matrix.Rotation(math.radians(-a.yaw), 3, 'Z') @ front, f'{a.prefix}-yaw.png')
print('OK')
