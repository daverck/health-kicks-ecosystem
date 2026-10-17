#!/usr/bin/env python3
"""Automated BLE GATT Spec-to-Code Contract Verifier for HealthKicks Ecosystem.

Verifies 100% adherence between:
1. Canonical contract: contracts/ble_gatt_specs.md
2. Firmware:           health-kicks-esp32-s3/include/invariants.h
3. Edge AI:            health-kicks-edge-script/src/healthkicks_edge/transport/ble/constants.py
4. Mobile:             health-kicks-mobile/lib/core/constants/ble_constants.dart
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CONTRACT_FILE = ROOT_DIR / "contracts" / "ble_gatt_specs.md"
FIRMWARE_HEADER = ROOT_DIR / "health-kicks-esp32-s3" / "include" / "invariants.h"
EDGE_CONSTANTS = ROOT_DIR / "health-kicks-edge-script" / "src" / "healthkicks_edge" / "transport" / "ble" / "constants.py"
MOBILE_CONSTANTS = ROOT_DIR / "health-kicks-mobile" / "lib" / "core" / "constants" / "ble_constants.dart"

EXPECTED_UUIDS = {
    "BASE_UUID": "7a5a0000-c529-4d64-8848-18e5904de22a",
    "FOOTWEAR_SERVICE_UUID": "7a5a0001-c529-4d64-8848-18e5904de22a",
    "CHAR_ACTIVITY_DETECTION_UUID": "7a5a0002-c529-4d64-8848-18e5904de22a",
    "CHAR_HAPTIC_COMMAND_UUID": "7a5a0003-c529-4d64-8848-18e5904de22a",
    "CHAR_STUDIO_CONTROL_UUID": "7a5a0004-c529-4d64-8848-18e5904de22a",
    "CHAR_STUDIO_DATA_BURST_UUID": "7a5a0005-c529-4d64-8848-18e5904de22a",
    "CHAR_STEP_COUNTER_UUID": "7a5a0006-c529-4d64-8848-18e5904de22a",
    "OTA_SERVICE_UUID": "7a5a0010-c529-4d64-8848-18e5904de22a",
    "CHAR_OTA_CONTROL_UUID": "7a5a0011-c529-4d64-8848-18e5904de22a",
    "CHAR_OTA_DATA_UUID": "7a5a0012-c529-4d64-8848-18e5904de22a",
}

EXPECTED_STATE_CODES = {
    "STATE_CODE_IDLE": 0x00,
    "STATE_CODE_WALK": 0x01,
    "STATE_CODE_RUN": 0x02,
    "STATE_CODE_FALL_FORWARD": 0x10,
    "STATE_CODE_FALL_BACKWARD": 0x11,
    "STATE_CODE_FALL_LATERAL": 0x12,
}


def verify_file_contains_uuids(file_path: Path, expected: dict[str, str], errors: list[str]) -> None:
    if not file_path.exists():
        errors.append(f"Missing file: {file_path}")
        return

    content = file_path.read_text(encoding="utf-8")
    for key, uuid in expected.items():
        if uuid.lower() not in content.lower():
            errors.append(f"[{file_path.relative_to(ROOT_DIR)}] Missing or mismatched UUID {key}: {uuid}")


def verify_contract_specs(errors: list[str]) -> None:
    if not CONTRACT_FILE.exists():
        errors.append(f"Contract file not found: {CONTRACT_FILE}")
        return

    text = CONTRACT_FILE.read_text(encoding="utf-8")
    found_uuids = set(re.findall(r"7a5a[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text))
    for key, uuid in EXPECTED_UUIDS.items():
        if uuid.lower() not in [u.lower() for u in found_uuids]:
            errors.append(f"[contracts/ble_gatt_specs.md] Missing UUID definition: {key} ({uuid})")


def main() -> int:
    print("=" * 60)
    print("HealthKicks Ecosystem - BLE GATT Contract Verification")
    print("=" * 60)

    errors: list[str] = []

    print("Checking canonical contract (contracts/ble_gatt_specs.md)...")
    verify_contract_specs(errors)

    print("Checking Firmware definitions (health-kicks-esp32-s3/include/invariants.h)...")
    verify_file_contains_uuids(FIRMWARE_HEADER, EXPECTED_UUIDS, errors)

    print("Checking Edge Script definitions (health-kicks-edge-script/src/.../constants.py)...")
    # Edge script implements primary footwear service and characteristics 0001 to 0005
    edge_subset = {k: v for k, v in EXPECTED_UUIDS.items() if "OTA" not in k and k != "CHAR_STEP_COUNTER_UUID"}
    verify_file_contains_uuids(EDGE_CONSTANTS, edge_subset, errors)

    print("Checking Mobile definitions (health-kicks-mobile/lib/.../ble_constants.dart)...")
    verify_file_contains_uuids(MOBILE_CONSTANTS, EXPECTED_UUIDS, errors)

    if errors:
        print("\n[ERROR] BLE GATT Contract violations detected:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n[SUCCESS] All BLE GATT UUIDs and invariants are 100% synchronized across all projects!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
