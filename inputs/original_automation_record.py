"""Prepare an OpenRadioss working copy of the VIVA+ beta head-drop curves.

Keep the published source deck intact. Reorder only the three source curves
whose abscissae decrease; retain the original (strain, stress) pairs verbatim.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent / "vivaplus-validation-main"
CASE = ROOT / "catalog/Yoganandan-2004-Head-lateral-drop/dyna/50F"
SOURCE = CASE / "setup/yoganandan_2005_setup.key"
OUTPUT = SOURCE.with_name("yoganandan_2005_setup-openradioss.key")
MAIN = CASE / "drop_test/drop_3.5/main-openradioss.key"
EXPECTED = {10: 17, 112: 17, 150: 1}

source = SOURCE.read_text()
pattern = re.compile(
    r"(?ms)^(?P<header>\*DEFINE_CURVE_TITLE\n[^\n]*\n[^\n]*\n)"
    r"(?P<points>.*?)(?=^\*|\Z)"
)
fixed = set()


def reorder(match):
    header, data = match.group("header", "points")
    curve_id = int(header.splitlines()[2][:10])
    if curve_id not in EXPECTED:
        return match.group(0)
    points = data.splitlines(keepends=True)
    if not points or any(not p.strip() or p.startswith("$") or len(p.rstrip("\n")) != 40 for p in points):
        raise ValueError("Unexpected data format in curve {}".format(curve_id))
    strains = [float(p[:20]) for p in points]
    inversions = sum(b <= a for a, b in zip(strains, strains[1:]))
    if inversions != EXPECTED[curve_id] or len(set(strains)) != len(strains):
        raise ValueError("Unexpected source points in curve {}".format(curve_id))
    fixed.add(curve_id)
    print("Curve {}: reordered {} of {} steps".format(curve_id, inversions, len(points)))
    return header + "".join(sorted(points, key=lambda p: float(p[:20])))


working = pattern.sub(reorder, source)
if fixed != set(EXPECTED):
    raise ValueError("Expected curves {}, found {}".format(sorted(EXPECTED), sorted(fixed)))

main = MAIN.read_text()
old = "yoganandan_2005_setup.key"
if main.count(old) != 1:
    raise ValueError("Expected one unmodified setup include in main-openradioss.key")
if "../../../../../../submodels/Head/" not in main:
    raise ValueError("Corrected head-model include path is missing")
if OUTPUT.exists():
    raise FileExistsError("Working setup already exists: {}".format(OUTPUT))

OUTPUT.write_text(working)
MAIN.write_text(main.replace(old, OUTPUT.name))
print("Wrote working setup and updated main include; original setup is intact")
