"""組合 A（雙軌主從軌＋中央柱塞）的參數化模型，輸出 STEP／STL。

座標與 3D 網頁相同（單位 mm）：
  X：滑動方向，平板由 +X 往 -X 滑入（由右往左）
  Y：平板上下緣方向，+Y 為上緣
  Z：厚度方向，平板後蓋背面在 z=0，平板在 +Z，翻板在 -Z
尺寸都是估算值，改下面 P 的數字就能重新產生模型。
"""
from pathlib import Path

import cadquery as cq

P = dict(
    tabW=150, tabH=85, tabT=14, tabR=9,      # 平板後蓋外形與圓角
    plateW=108, plateH=117, plateT=6,        # 胸掛翻板
    f=0.3,                                    # 平板背面與翻板面的間隙
    yc=32,                                    # 上下軌中心 y=±yc
    a=8, h=3,                                 # 公軌根部寬、高（45° 鳩尾，頂部寬 a+2h）
    c=0.25,                                   # 主軌斜面側隙
    d=3.2,                                    # 母槽深度
    g=0.6,                                    # 從軌內側浮動間隙
    L=80, x0=-50,                             # 公軌長度與起點（x0 抵住左端擋塊）
    stopW=4,                                  # 左端擋塊寬
    pinD=5.6, holeD=6.6, holeDepth=2.0,       # 柱塞直徑、後蓋定位孔
)
OUT = Path(__file__).parent / "out"


def tablet_back():
    """平板後蓋：外形實體＋上（主）下（從）兩條公軌＋中央定位孔。"""
    p = P
    body = (cq.Workplane("XY").rect(p["tabW"], p["tabH"]).extrude(p["tabT"])
            .edges("|Z").fillet(p["tabR"]))
    yc, a, h = p["yc"], p["a"], p["h"]
    # 公軌斷面畫在 YZ 平面（工作平面座標 = 全域 (Y, Z)），沿 +X 拉伸；根部多埋 0.5 mm 進後蓋
    master = [(yc - a / 2, 0.5), (yc + a / 2, 0.5), (yc + a / 2, 0), (yc + a / 2 + h, -h), (yc - a / 2 - h, -h), (yc - a / 2, 0)]
    slave = [(-yc + a / 2, 0.5), (-yc + a / 2, -h), (-yc - a / 2 - h, -h), (-yc - a / 2, 0), (-yc - a / 2, 0.5)]
    for pts in (master, slave):
        rail = cq.Workplane("YZ").polyline(pts).close().extrude(p["L"]).translate((p["x0"], 0, 0))
        body = body.union(rail)
    hole = cq.Workplane("XY").circle(p["holeD"] / 2).extrude(p["holeDepth"])
    return body.cut(hole)


def mount_plate():
    """胸掛翻板：上（主，完整鳩尾）下（從，單斜面＋浮動）母槽、左端擋塊、柱塞孔。"""
    p = P
    H, T, f, a, c, d, g, yc = p["plateH"], p["plateT"], p["f"], p["a"], p["c"], p["d"], p["g"], p["yc"]
    zf, zb = -f, -f - T
    y1, y0 = yc + a / 2 + f + c, yc - a / 2 - f - c          # 主槽開口（含斜面側隙）
    yi, yo = -yc + a / 2 + g, -yc - a / 2 - f - c            # 從槽：內側浮動、外側斜面
    pts = [
        (-H / 2, zb), (H / 2, zb), (H / 2, zf),
        (y1, zf), (y1 + d, zf - d), (y0 - d, zf - d), (y0, zf),
        (yi, zf), (yi, zf - d), (yo - d, zf - d), (yo, zf),
        (-H / 2, zf),
    ]
    length = p["plateW"] - p["stopW"]
    plate = cq.Workplane("YZ").polyline(pts).close().extrude(length).translate((-p["plateW"] / 2 + p["stopW"], 0, 0))
    stop = cq.Workplane("XY").box(p["stopW"], H, T).translate((-p["plateW"] / 2 + p["stopW"] / 2, 0, zf - T / 2))
    plate = plate.union(stop)
    pin_hole = cq.Workplane("XY").workplane(offset=zb).circle(p["pinD"] / 2 + 0.2).extrude(T)
    return plate.cut(pin_hole)


def plunger():
    """柱塞（伸出狀態：頂面高出翻板面 1.8 mm，伸進後蓋定位孔）。"""
    p = P
    top = -p["f"] + 1.8
    return cq.Workplane("XY").workplane(offset=top - 6).circle(p["pinD"] / 2).extrude(6)


def main():
    OUT.mkdir(exist_ok=True)
    parts = {"tablet_back": tablet_back(), "mount_plate": mount_plate(), "plunger": plunger()}
    for name, wp in parts.items():
        cq.exporters.export(wp, str(OUT / f"{name}.step"))
        cq.exporters.export(wp, str(OUT / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
    asm = cq.Assembly(name="combo_a")
    asm.add(parts["tablet_back"], name="tablet_back", color=cq.Color(0.89, 0.69, 0.16))
    asm.add(parts["mount_plate"], name="mount_plate", color=cq.Color(0.56, 0.59, 0.55))
    asm.add(parts["plunger"], name="plunger", color=cq.Color(0.82, 0.33, 0.12))
    asm.export(str(OUT / "combo_a_assembly.step"))
    # 預覽用：從入口端（+X）看的斷面投影
    cq.exporters.export(
        parts["mount_plate"].union(parts["tablet_back"]),
        str(OUT / "combo_a_end.svg"),
        opt={"projectionDir": (1, 0, 0), "width": 900, "height": 500, "showHidden": False, "strokeWidth": 0.3},
    )
    for name, wp in parts.items():
        bb = wp.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, 體積 {wp.val().Volume():.0f} mm3, valid={wp.val().isValid()}")


if __name__ == "__main__":
    main()
