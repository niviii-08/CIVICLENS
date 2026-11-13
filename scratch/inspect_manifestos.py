import os
import json

manifest_file = "data/raw/manifestos/manifest.json"
if os.path.exists(manifest_file):
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Manifest keys:", list(data.keys()))
    print("Total files reported:", data.get("total_files"))
    files = data.get("files", [])
    for item in files[:10]:
        print(" ", item.get("file_id"), item.get("party"), item.get("election_year"), item.get("filename"), item.get("source_url"))
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")

print("\nFiles in data/raw/manifestos:")
for root, dirs, files in os.walk("data/raw/manifestos"):
    for f in files:
        fp = os.path.join(root, f)
        print(" ", os.path.relpath(fp, "data/raw/manifestos").replace("\\", "/"), f"({os.path.getsize(fp)} bytes)")
