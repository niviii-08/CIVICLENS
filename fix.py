import re

path = r'E:\CIVCLENS\backend\api\schemes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split("@schemes_bp.route('/<int:scheme_id>/similar', methods=['GET'])")

if len(parts) == 3:

    new_content = parts[0] + "@schemes_bp.route('/<int:scheme_id>/similar', methods=['GET'])" + parts[2]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed duplicates.")
else:
    print("Unexpected parts length:", len(parts))
