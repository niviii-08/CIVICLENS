#!/usr/bin/env python3
"""
CIVICLENS TN — Automated Quality & CI Verification Runner

Executes comprehensive repository checks:
1. Python syntax compilation (py_compile)
2. Database migration alignment (alembic current)
3. Security & database integrity test suite
4. Machine learning model evaluation tests
5. Data integration and traceability tests
6. NLP pipeline and promise extraction tests
7. Domain REST API test suite
8. Frontend TypeScript type checking (if Node.js/npm available)

Exit code: 0 if all checks pass; nonzero on any failure.
"""

import os
import sys
import time
import shutil
import py_compile
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)
sys.path.insert(0, str(ROOT_DIR))

# ANSI formatting for readable test terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_step(title: str):
    print(f"\n{BOLD}{CYAN}==> [{time.strftime('%H:%M:%S')}] {title}{RESET}")


def run_command(cmd, desc: str) -> bool:
    print(f"{YELLOW}Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}{RESET}")
    start = time.time()
    res = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=ROOT_DIR)
    duration = time.time() - start
    if res.returncode == 0:
        print(f"{GREEN}[PASS] {desc} ({duration:.2f}s){RESET}")
        return True
    else:
        print(f"{RED}[FAIL] {desc} (exit code: {res.returncode}, duration: {duration:.2f}s){RESET}")
        return False


def check_python_syntax() -> bool:
    print_step("Step 1: Python Syntax Validation (py_compile)")
    py_files = list(ROOT_DIR.glob("backend/**/*.py")) + list(ROOT_DIR.glob("tests/**/*.py"))
    failed_files = []
    for f in py_files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            failed_files.append((f, str(e)))

    if failed_files:
        for f, err in failed_files:
            print(f"{RED}Syntax error in {f}: {err}{RESET}")
        return False
    print(f"{GREEN}[PASS] All {len(py_files)} Python source files compiled with valid syntax.{RESET}")
    return True


def check_database_migrations() -> bool:
    print_step("Step 2: Database Migration Check (alembic current)")
    return run_command([sys.executable, "-m", "alembic", "current"], "Alembic schema migration status")


def run_test_suites() -> bool:
    suites = [
        (
            [sys.executable, "-m", "pytest", "tests/unit/test_config.py", "tests/unit/test_security_hardening.py", "tests/unit/test_database_integrity.py", "tests/unit/test_logging_monitoring.py", "-v"],
            "Security, Database Integrity & Logging/Monitoring Tests"
        ),
        (
            [sys.executable, "-m", "pytest", "tests/ml/", "-v"],
            "Machine Learning Evaluation Suite"
        ),
        (
            [sys.executable, "-m", "pytest", "tests/integration/", "-v"],
            "Data Integration & Traceability Suite"
        ),
        (
            [sys.executable, "-m", "pytest", "tests/nlp/", "-v"],
            "NLP Processing & Promise Extraction Suite"
        ),
        (
            [sys.executable, "-m", "pytest", "tests/api/", "-v"],
            "Domain REST API Test Suite"
        ),
    ]

    all_passed = True
    for cmd, desc in suites:
        print_step(f"Running: {desc}")
        if not run_command(cmd, desc):
            all_passed = False
            # Fail fast on test suite failures
            break
    return all_passed


def check_frontend() -> bool:
    print_step("Step 8: Frontend Quality Checks (TypeScript typecheck)")
    npm_path = shutil.which("npm")
    if not npm_path:
        print(f"{YELLOW}[SKIP] npm not found on PATH; skipping frontend checks.{RESET}")
        return True

    cmd = "npm run typecheck --prefix frontend"
    return run_command(cmd, "Frontend TypeScript type check (tsc --noEmit)")


def main():
    print(f"{BOLD}======================================================================{RESET}")
    print(f"{BOLD}  CIVICLENS TN — Automated Quality Verification Pipeline{RESET}")
    print(f"{BOLD}======================================================================{RESET}")

    start_total = time.time()
    results = {}

    results["Python Syntax"] = check_python_syntax()
    if not results["Python Syntax"]:
        sys.exit(1)

    results["Database Migrations"] = check_database_migrations()
    if not results["Database Migrations"]:
        sys.exit(1)

    results["Test Suites"] = run_test_suites()
    if not results["Test Suites"]:
        sys.exit(1)

    results["Frontend Typecheck"] = check_frontend()
    if not results["Frontend Typecheck"]:
        sys.exit(1)

    total_duration = time.time() - start_total
    print(f"\n{BOLD}======================================================================{RESET}")
    print(f"{BOLD}  Verification Summary ({total_duration:.2f}s total){RESET}")
    print(f"{BOLD}======================================================================{RESET}")

    all_success = True
    for check_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"  - {check_name:<30} {status}")
        if not passed:
            all_success = False

    if all_success:
        print(f"\n{BOLD}{GREEN}[SUCCESS] All quality checks and tests passed cleanly.{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{RED}[FAILURE] One or more checks failed. See details above.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
