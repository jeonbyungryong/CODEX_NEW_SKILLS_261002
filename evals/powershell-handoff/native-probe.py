import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
values = sys.argv[1:]
print(json.dumps(values, ensure_ascii=False))
if len(values) != 4 or values[0] != "--input" or values[2] != "--label":
    sys.exit(9)
if values[3] == "FAIL":
    print("synthetic failure", file=sys.stderr)
    sys.exit(7)
