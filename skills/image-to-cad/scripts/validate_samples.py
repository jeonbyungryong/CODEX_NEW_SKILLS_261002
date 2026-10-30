# /// script
# requires-python = ">=3.12"
# dependencies = ["ezdxf>=1.4,<2", "shapely>=2.0,<3", "opencv-python-headless>=4.10,<5", "numpy>=2.1,<3", "Pillow>=11,<12", "PyMuPDF>=1.26,<2"]
# ///
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import ezdxf


root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="image-to-cad-") as temporary:
    workspace = Path(temporary)
    source = workspace / "capsule.dxf"
    document = ezdxf.new("R2010")
    document.header["$INSUNITS"] = 4
    modelspace = document.modelspace()
    modelspace.add_lwpolyline(
        [(0, 40, 0), (0, 200, -1), (80, 200, 0), (80, 40, -1)],
        format="xyb",
        close=True,
    )
    document.saveas(source)
    output = workspace / "out"
    subprocess.run(
        [sys.executable, str(root / "reconstruct_geometry.py"), "--input", str(source), "--output-dir", str(output), "--tolerance-mm", "0.01"],
        check=True,
    )
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["unit"] == "mm"
    assert report["entity_count"] == 1
    assert report["shape_group_count"] == 1
    assert report["production_region_count"] == 1
    assert abs(report["width"] - 80) < 0.02
    assert abs(report["height"] - 240) < 0.02
    assert 17820 < report["area"] < 17835
    assert (output / "normalized.dxf").is_file()
    assert (output / "preview.png").is_file()
    for code, mm_per_unit in [(4, 1.0), (1, 25.4), (6, 1000.0)]:
        drawing = ezdxf.new("R2010")
        drawing.header["$INSUNITS"] = code
        ms = drawing.modelspace()
        ms.add_circle((0, 0), 10 / mm_per_unit)
        ms.add_arc((30 / mm_per_unit, 0), 5 / mm_per_unit, 0, 90)
        ms.add_lwpolyline([(50 / mm_per_unit, 0, .5), (60 / mm_per_unit, 0, 0),
                          (60 / mm_per_unit, 10 / mm_per_unit, 0)], format="xyb", close=True)
        ms.add_line((80 / mm_per_unit, 0), (90 / mm_per_unit, 0))
        ms.add_line((90.1 / mm_per_unit, 0), (100 / mm_per_unit, 0))
        fixture = workspace / f"units-{code}.dxf"
        drawing.saveas(fixture)
        target = workspace / f"units-{code}"
        subprocess.run([sys.executable, str(root / "reconstruct_geometry.py"),
                        "--input", str(fixture), "--output-dir", str(target),
                        "--tolerance-mm", "0.05"], check=True, stdout=subprocess.PIPE)
        result = json.loads((target / "report.json").read_text(encoding="utf-8"))
        saved = ezdxf.readfile(target / "normalized.dxf")
        assert saved.header["$INSUNITS"] == code, "Source unit identity lost"
        assert len(saved.modelspace().query("CIRCLE")) == 1, "Analytic circle lost"
        assert len(saved.modelspace().query("ARC")) == 1, "Analytic arc lost"
        poly = list(saved.modelspace().query("LWPOLYLINE"))[0]
        assert abs(poly.get_points("xyb")[0][2] - .5) < 1e-12, "Bulge lost"
        assert abs(result["calculation_tolerance"] * mm_per_unit - .05) < 1e-12
        assert result["snap_count"] == 0, "0.1 mm gap must not close at 0.05 mm tolerance"
        assert abs(result["width"] * mm_per_unit - 110) < .05
print("image-to-cad sample validation passed")
