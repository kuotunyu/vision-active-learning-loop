"""Compare two directory trees file by file (names, sizes, SHA-256). Usage: verify_backup.py SRC DST OUT.json"""
import hashlib, json, os, sys, time
from pathlib import Path

src, dst, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])

def walk(root):
    files = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = Path(dirpath) / n
            files[str(p.relative_to(root)).replace(os.sep, "/")] = p.stat().st_size
    return files

def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

t0 = time.time()
a, b = walk(src), walk(dst)
missing = sorted(set(a) - set(b)); extra = sorted(set(b) - set(a))
size_mismatch = sorted(k for k in a if k in b and a[k] != b[k])
hash_mismatch = []
checked = 0; total_bytes = 0
for k in sorted(set(a) & set(b)):
    if a[k] != b[k]:
        continue
    if digest(src / k) != digest(dst / k):
        hash_mismatch.append(k)
    checked += 1; total_bytes += a[k]
report = {
    "source": str(src), "destination": str(dst),
    "source_files": len(a), "destination_files": len(b), "source_bytes": sum(a.values()),
    "hash_checked_files": checked, "hash_checked_bytes": total_bytes,
    "missing_in_destination": missing, "extra_in_destination": extra,
    "size_mismatch": size_mismatch, "hash_mismatch": hash_mismatch,
    "seconds": round(time.time() - t0, 1),
}
report["ok"] = not (missing or extra or size_mismatch or hash_mismatch) and len(a) == len(b)
out.write_text(json.dumps(report, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if not isinstance(v, list)}, indent=1))
print("mismatches:", len(missing), len(extra), len(size_mismatch), len(hash_mismatch))
sys.exit(0 if report["ok"] else 1)
