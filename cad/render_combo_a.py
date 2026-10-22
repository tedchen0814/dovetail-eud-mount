"""組合 A 的 Blender（Eevee）靜態渲染：平板往 +X 拉出一段，讓中央柱塞露出來。

先跑 combo_a.py 產生 cad/out/*.stl，再用 Blender 背景模式執行：
  C:\\SPB_Data\\blender\\blender-4.5.14-windows-x64\\blender.exe -b --factory-startup --python cad\\render_combo_a.py
  （只出某幾張：在最後加 `-- iso closeup`）
輸出到 cad/out/render/<視角>.png。座標同 combo_a.py（mm，X 滑動、Y 上下緣、Z 厚度）。
"""
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).parent
OUT = HERE / "out"
RENDER = OUT / "render"

PULL = 85          # 平板往 +X 拉出的距離（mm）：左緣到 x=10，柱塞 x=0 露出，公軌仍咬住母槽約 19 mm
RES = (1920, 1080)
SAMPLES = 64

PARTS = {  # 顏色同 combo_a.py 組立檔
    "tablet_back": ((0.89, 0.69, 0.16), 0.5, (PULL, 0, 0)),
    "mount_plate": ((0.56, 0.59, 0.55), 0.55, (0, 0, 0)),
    "plunger": ((0.82, 0.33, 0.12), 0.35, (0, 0, 0)),
}

# 視角：相機位置、注視點（mm）、焦距（mm）
VIEWS = {
    "iso": ((-190, -230, 210), (25, 0, -3), 50),        # 斜視全景：從擋塊端上方看，翻板面、柱塞、公軌一起入鏡
    "closeup": ((-55, -70, 60), (2, 0, 0), 60),         # 柱塞與母槽特寫
    "entry_end": ((260, -45, -22), (54, 0, -3), 45),    # 入口端（+X）、從翻板面下方看：公軌端面與母槽斷面
    "back": ((-120, -180, -220), (10, 0, -3), 50),      # 翻板背面（-Z）：柱塞孔與擋塊
}


def mm(v):
    return Vector(v) * 0.001


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def material(name, rgb, rough):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for name, (rgb, rough, offset) in PARTS.items():
        bpy.ops.wm.stl_import(filepath=str(OUT / f"{name}.stl"), global_scale=0.001)
        obj = bpy.context.selected_objects[0]
        obj.location = mm(offset)
        obj.data.materials.append(material(name, rgb, rough))
        bpy.ops.object.shade_auto_smooth(angle=0.6)  # 圓角平滑、直角維持銳利

    # 灰色地板：放在翻板背面下方
    bpy.ops.mesh.primitive_plane_add(size=2, location=mm((0, 0, -60)))
    floor = bpy.context.active_object
    floor.data.materials.append(material("floor", (0.3, 0.31, 0.33), 0.8))

    for loc, energy, size in [((-150, -200, 300), 2.5, 250), ((250, 150, 200), 1.0, 300), ((0, 300, -150), 0.7, 300)]:
        data = bpy.data.lights.new("key", "AREA")
        data.energy, data.size = energy, size * 0.001
        light = bpy.data.objects.new("key", data)
        scene.collection.objects.link(light)
        light.location = mm(loc)
        look_at(light, Vector((0, 0, 0)))

    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.125, 0.135, 1)
    scene.world = world

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = SAMPLES
    scene.eevee.use_raytracing = True
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    return scene, cam, floor


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    names = argv or list(VIEWS)
    RENDER.mkdir(parents=True, exist_ok=True)
    scene, cam, floor = build_scene()
    for name in names:
        loc, target, lens = VIEWS[name]
        cam.location = mm(loc)
        cam.data.lens = lens
        cam.data.clip_start = 0.001
        look_at(cam, mm(target))
        floor.hide_render = name in ("back", "entry_end")  # 從翻板面下方看時地板會擋住
        scene.render.filepath = str(RENDER / f"{name}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED {name} {time.time() - t:.1f}s")


main()
