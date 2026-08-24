"""Configuration loader for ml-compute.

Loads settings from config/ml-compute.yaml to avoid hardcoded URLs and constants.
"""

from pathlib import Path
from typing import Any

import yaml


def load_config() -> dict[str, Any]:
    """Load the YAML configuration file.

    Returns:
        Configuration dictionary.
    """
    config_path = Path(__file__).parent.parent / "config" / "ml-compute.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


CONFIG: dict[str, Any] = load_config()
