#!/usr/bin/env python3
"""
CIVICLENS TN — Operational Health Check and Probe Verification

Probes backend process liveness and database readiness endpoints.
Designed for use in deployment verification, container health probes, and CI/CD pipelines.

Usage:
    python scripts/check_health.py [--url http://localhost:5000] [--timeout 5]
Exit codes:
    0: All probes healthy and ready.
    1: One or more probes failed or service unreachable.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

# ANSI escape codes for terminal formatting
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def probe_endpoint(url: str, timeout: int = 5) -> tuple[int, dict, float]:
    """Issues an HTTP GET request and returns (status_code, payload_dict, latency_ms)."""
    start = time.time()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CivicLens-HealthProbe/1.0", "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency_ms = (time.time() - start) * 1000
            data = json.loads(response.read().decode("utf-8"))
            return response.status, data, latency_ms
    except urllib.error.HTTPError as e:
        latency_ms = (time.time() - start) * 1000
        try:
            data = json.loads(e.read().decode("utf-8"))
        except Exception:
            data = {"raw_error": str(e)}
        return e.code, data, latency_ms
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return 0, {"error": str(e)}, latency_ms


def main():
    parser = argparse.ArgumentParser(description="CivicLens TN Deployment Health Probe")
    parser.add_argument(
        "--url",
        default=os.getenv("INTERNAL_API_URL", "http://127.0.0.1:5000"),
        help="Base URL of the CIVICLENS backend service (default: http://127.0.0.1:5000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Probe timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit result in machine-readable JSON format"
    )

    args = parser.parse_args()
    base_url = args.url.rstrip("/")

    results = {
        "target": base_url,
        "liveness": {"healthy": False},
        "readiness": {"ready": False},
        "all_passed": False
    }

    if not args.json:
        print(f"\n{BOLD}{CYAN}=== CIVICLENS TN Deployment Health Check ==={RESET}")
        print(f"Target Service: {YELLOW}{base_url}{RESET}\n")

    # 1. Check Liveness Probe (/health/live or /health)
    live_url = f"{base_url}/health/live"
    live_code, live_body, live_ms = probe_endpoint(live_url, timeout=args.timeout)

    is_live = (live_code == 200 and live_body.get("status") in ("healthy", "success"))
    results["liveness"] = {
        "url": live_url,
        "status_code": live_code,
        "healthy": is_live,
        "latency_ms": round(live_ms, 2),
        "payload": live_body
    }

    if not args.json:
        if is_live:
            print(f" {GREEN}[PASS]{RESET} Process Liveness  : HTTP {live_code} ({live_ms:.1f}ms) -> {live_body.get('status', 'healthy')}")
        else:
            print(f" {RED}[FAIL]{RESET} Process Liveness  : HTTP {live_code} ({live_ms:.1f}ms) -> {live_body}")

    # 2. Check Readiness Probe (/health/ready or /health/db)
    ready_url = f"{base_url}/health/ready"
    ready_code, ready_body, ready_ms = probe_endpoint(ready_url, timeout=args.timeout)

    is_ready = (
        ready_code == 200 and
        ready_body.get("status") in ("ready", "healthy", "success") and
        ready_body.get("database") in ("connected", "ok", None)
    )
    results["readiness"] = {
        "url": ready_url,
        "status_code": ready_code,
        "ready": is_ready,
        "latency_ms": round(ready_ms, 2),
        "payload": ready_body
    }

    if not args.json:
        if is_ready:
            print(f" {GREEN}[PASS]{RESET} Database Readiness: HTTP {ready_code} ({ready_ms:.1f}ms) -> db: {ready_body.get('database', 'connected')}")
        else:
            print(f" {RED}[FAIL]{RESET} Database Readiness: HTTP {ready_code} ({ready_ms:.1f}ms) -> {ready_body}")

    results["all_passed"] = is_live and is_ready

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("")
        if results["all_passed"]:
            print(f"{GREEN}{BOLD}[SUCCESS] Application is live, responsive, and database ready.{RESET}\n")
        else:
            print(f"{RED}{BOLD}[FAILURE] Application health check failed. Review log output above.{RESET}\n")

    sys.exit(0 if results["all_passed"] else 1)


if __name__ == "__main__":
    main()
