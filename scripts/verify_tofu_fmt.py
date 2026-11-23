#!/usr/bin/env python3
"""
HealthKicks Ecosystem - OpenTofu Formatting Verification Script
Runs 'tofu fmt -check -recursive infra/tofu'.
Gracefully skips if the 'tofu' executable is not found in PATH.
"""

import shutil
import subprocess
import sys


def main() -> int:
    tofu_bin = shutil.which("tofu")
    if not tofu_bin:
        print("[SKIP] OpenTofu executable ('tofu') not found in PATH. Skipping tofu-fmt hook.")
        return 0

    res = subprocess.run([tofu_bin, "fmt", "-check", "-recursive", "infra/tofu"])
    if res.returncode != 0:
        print("\n[ERROR] OpenTofu code formatting check failed!")
        print("Run 'tofu fmt -recursive infra/tofu' to automatically format your files.")
        return res.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
