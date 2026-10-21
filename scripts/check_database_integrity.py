import sqlite3

def check_integrity():
    db_path = "data/processed/civiclens.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA integrity_check;")
    integ = cur.fetchall()
    print("=== PRAGMA integrity_check ===")
    for r in integ:
        print(f"  {r[0]}")

    cur.execute("PRAGMA foreign_key_check;")
    fk_violations = cur.fetchall()
    print(f"\n=== PRAGMA foreign_key_check ===")
    print(f"  Violations found: {len(fk_violations)}")
    for v in fk_violations[:10]:
        print(f"    Table: {v[0]}, RowId: {v[1]}, Target: {v[2]}, FkId: {v[3]}")

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;").fetchall()]
    print(f"\n=== Database Tables Inventory ({len(tables)} tables) ===")
    for t in tables:
        count = cur.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        print(f"  - {t:<40}: {count:>6} rows")

    # Check for potential duplicates in key tables
    print("\n=== Duplicate Checks on Canonical Tables ===")
    canonical_checks = [
        ("historical_schemes", "scheme_name", "SELECT scheme_name, count(*) FROM historical_schemes GROUP BY scheme_name HAVING count(*) > 1;"),
        ("political_parties", "party_name", "SELECT party_name, count(*) FROM political_parties GROUP BY party_name HAVING count(*) > 1;"),
        ("policy_registry", "policy_name", "SELECT policy_name, count(*) FROM policy_registry GROUP BY policy_name HAVING count(*) > 1;"),
        ("budget_departments", "name", "SELECT name, count(*) FROM budget_departments GROUP BY name HAVING count(*) > 1;"),
        ("promise_categories", "name", "SELECT name, count(*) FROM promise_categories GROUP BY name HAVING count(*) > 1;"),
        ("political_claims", "content_fingerprint", "SELECT content_fingerprint, count(*) FROM political_claims GROUP BY content_fingerprint HAVING count(*) > 1;")
    ]

    for table, col, query in canonical_checks:
        try:
            dups = cur.execute(query).fetchall()
            print(f"  - {table} ({col}): {len(dups)} duplicates")
            for d in dups[:5]:
                print(f"      Duplicate: {d[0]} (count: {d[1]})")
        except Exception as e:
            print(f"  - {table} ({col}): check failed ({e})")

    conn.close()

if __name__ == "__main__":
    check_integrity()
