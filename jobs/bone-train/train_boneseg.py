"""Ray entrypoint for bone-train's MONAI SwinUNETR training job.

The ml-compute working directory supplies this stable entrypoint while Ray's
``py_modules`` runtime environment ships the canonical bone-train source tree.
This avoids maintaining a second copy of the model and training loop here.
"""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def find_bone_train_root() -> Path:
    """Find the bone-train source tree shipped in the Ray runtime environment.

    Returns:
        Directory containing bone-train's ``src`` and canonical training job.

    Raises:
        RuntimeError: If bone-train was not included in ``py_modules``.
    """
    configured = os.environ.get("BONE_TRAIN_ROOT")
    candidates = [Path(configured)] if configured else []
    candidates.extend(Path(item) for item in sys.path if item)

    for candidate in candidates:
        # Ray places a directory passed through py_modules below the generated
        # package root (for example: <ray-package>/bone-train/).
        for root in (candidate, candidate / "bone-train"):
            job = root / "jobs" / "train_boneseg.py"
            config = root / "config" / "bone-train.yaml"
            if job.is_file() and config.is_file():
                return root.resolve()

    raise RuntimeError(
        "bone-train source is missing from the Ray runtime. Submit with "
        "runtime_env.py_modules=['/opt/onyx/skills/bone-train']."
    )


def main() -> None:
    """Run bone-train's canonical SwinUNETR entrypoint."""
    bone_train_root = find_bone_train_root()
    sys.path.insert(0, str(bone_train_root))
    runpy.run_path(str(bone_train_root / "jobs" / "train_boneseg.py"), run_name="__main__")


if __name__ == "__main__":
    main()
