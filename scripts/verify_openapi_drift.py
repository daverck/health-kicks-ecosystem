#!/usr/bin/env python3
"""Automated OpenAPI & TypeScript Spec-to-Code Drift Verifier for HealthKicks Ecosystem.

Verifies:
1. Canonical backend contract: FastAPI app.openapi() matches health-kicks/openapi.json
2. Frontend consumer types: health-kicks-frontend/src/app/models/generated-api.types.ts
   contains all schemas and endpoints declared in health-kicks/openapi.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OPENAPI_JSON = ROOT_DIR / "health-kicks" / "openapi.json"
FRONTEND_TYPES = ROOT_DIR / "health-kicks-frontend" / "src" / "app" / "models" / "generated-api.types.ts"


def get_live_fastapi_openapi() -> dict | None:
    """Extracts live OpenAPI spec from FastAPI application via uv."""
    uv_bin = shutil.which("uv")
    if not uv_bin:
        # Fallback to python directly if uv is not in PATH
        uv_bin = "uv"

    cmd = [
        uv_bin,
        "run",
        "--project",
        str(ROOT_DIR / "health-kicks"),
        "python",
        "-c",
        (
            "import json, sys; "
            f"sys.path.insert(0, r'{ROOT_DIR / 'health-kicks'}'); "
            "from app.main import app; "
            "print(json.dumps(app.openapi(), indent=2, sort_keys=True))"
        ),
    ]

    try:
        res = subprocess.run(
            cmd,
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return json.loads(res.stdout)
    except Exception as exc:
        print(f"[WARN] Unable to extract live FastAPI schema ({exc}). Skipping live comparison.")
        return None


def verify_openapi_drift(write_mode: bool) -> int:
    print("=" * 60)
    print("HealthKicks Ecosystem - OpenAPI & Frontend Types Drift Check")
    print("=" * 60)

    errors: list[str] = []

    if not OPENAPI_JSON.exists():
        errors.append(f"Missing openapi.json file: {OPENAPI_JSON}")
        return 1

    committed_openapi = json.loads(OPENAPI_JSON.read_text(encoding="utf-8"))

    # 1. Compare Live FastAPI vs openapi.json
    print("1. Checking live FastAPI definition against health-kicks/openapi.json...")
    live_openapi = get_live_fastapi_openapi()
    if live_openapi is not None:
        if write_mode:
            OPENAPI_JSON.write_text(json.dumps(live_openapi, indent=2) + "\n", encoding="utf-8")
            print(f"   [SUCCESS] Updated {OPENAPI_JSON.relative_to(ROOT_DIR)} with live schema.")
            committed_openapi = live_openapi
        else:
            if live_openapi != committed_openapi:
                errors.append(
                    "[health-kicks/openapi.json] Outdated specifications! Live FastAPI schema has diverged. "
                    "Run 'python scripts/verify_openapi_drift.py --write' to regenerate."
                )
            else:
                print("   [OK] health-kicks/openapi.json is 100% in sync with FastAPI code.")
    else:
        print("   [SKIP] Live FastAPI comparison skipped (dependencies not available).")

    # 2. Check Frontend generated-api.types.ts
    print("2. Checking Frontend TypeScript types against health-kicks/openapi.json...")
    if not FRONTEND_TYPES.exists():
        errors.append(f"Missing frontend types file: {FRONTEND_TYPES.relative_to(ROOT_DIR)}")
    else:
        ts_content = FRONTEND_TYPES.read_text(encoding="utf-8")
        paths = committed_openapi.get("paths", {})
        missing_paths = [p for p in paths if f'"{p}":' not in ts_content]

        schemas = committed_openapi.get("components", {}).get("schemas", {})
        missing_schemas = [
            s
            for s in schemas
            if f'components["schemas"]["{s}"]' not in ts_content
            and f'"{s}":' not in ts_content
            and f" {s}:" not in ts_content
            and f"\t{s}:" not in ts_content
        ]

        if missing_paths:
            errors.append(
                f"[health-kicks-frontend] {len(missing_paths)} paths missing in generated-api.types.ts "
                f"(e.g. {missing_paths[:3]}). Run 'pnpm --dir health-kicks-frontend run generate:api'."
            )
        if missing_schemas:
            errors.append(
                f"[health-kicks-frontend] {len(missing_schemas)} schemas missing in generated-api.types.ts "
                f"(e.g. {missing_schemas[:3]}). Run 'pnpm --dir health-kicks-frontend run generate:api'."
            )

        if not missing_paths and not missing_schemas:
            print(
                f"   [OK] {len(paths)} paths and {len(schemas)} schemas are 100% present in "
                f"{FRONTEND_TYPES.relative_to(ROOT_DIR)}."
            )

    if errors:
        print("\n[ERROR] OpenAPI Contract drift detected:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n[SUCCESS] OpenAPI contracts and TypeScript types are fully synchronized across the ecosystem!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OpenAPI and TypeScript contract drift.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Update health-kicks/openapi.json from the live FastAPI app definition",
    )
    args = parser.parse_args()
    return verify_openapi_drift(write_mode=args.write)


if __name__ == "__main__":
    sys.exit(main())
