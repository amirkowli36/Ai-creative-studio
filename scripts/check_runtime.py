#!/usr/bin/env python3
"""Print a small diagnostic report for a Python/ComfyUI runtime."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path


def main() -> int:
    print("AI Creative Studio runtime check")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Free disk space: {shutil.disk_usage(Path.cwd()).free / (1024**3):.2f} GiB")

    try:
        import torch  # type: ignore

        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
    except ImportError:
        print("PyTorch: not installed")
    except Exception as exc:  # diagnostic should still show remaining information
        print(f"PyTorch diagnostic failed: {exc}")

    print(f"COMFYUI_PATH: {os.environ.get('COMFYUI_PATH', '(not set)')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
